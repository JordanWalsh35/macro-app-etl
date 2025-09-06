import argparse
import logging
import os
import pandas as pd
import requests
import time
import yfinance as yf
import xml.etree.ElementTree as ET

from datetime import date, datetime, timezone
from dotenv import load_dotenv
from fredapi import Fred
from helper import get_engine, load_table
from io import BytesIO


# Add parser logic to differentiate between initial run and update runs
parser = argparse.ArgumentParser(description="ETL script for macro data.")
parser.add_argument("--initial", action="store_true", help="Run full load and recreate tables.")
parser.add_argument("--debug", action="store_true", help="Runs script in debug mode which saves to Excel instead of SQL")
args = parser.parse_args()

# Add logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("macro_etl_log.txt", mode='a')
    ]
)

# Define the SQL engine
engine = get_engine("etl_writer_pw")
# Create an empty dictionary
all_data = {}


# Fed Liquidity Data
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")
# Initialize FRED API
fred = Fred(api_key=FRED_API_KEY)
# List of economic indicators to fetch
liquidity_dict = {
    "Fed Balance Sheet": "WALCL",
    "TGA": "WTREGEN",
    "RRP": "RRPONTSYD"}
# Loop through series and fetch data
liquidity_df = pd.DataFrame()
for series_name, series_id in liquidity_dict.items():
    liquidity_df[series_name] = fred.get_series(series_id)
liquidity_df.index.name = "Date"
# Handle Missing Values
liquidity_df['RRP'] = liquidity_df['RRP'].fillna(0)
if liquidity_df.iloc[-1].isnull().any():
    liquidity_df = liquidity_df.iloc[:-1]
# Change units of Fed Balance Sheet so everything is in billions
liquidity_df["Fed Balance Sheet"] = liquidity_df["Fed Balance Sheet"]/1000
# Calculate Fed Net Liquidity Column
liquidity_df["Fed Net Liquidity"] = liquidity_df["Fed Balance Sheet"] - liquidity_df["TGA"] - liquidity_df["RRP"]
all_data["fed_liquidity"] = liquidity_df
logging.info("Liquidity data fetched.")


# Nasdaq Composite Index
nasdaq_df = pd.DataFrame()
nasdaq_df["Nasdaq"] = fred.get_series("NASDAQCOM")
nasdaq_df.index.name = "Date"
nasdaq_df = nasdaq_df.dropna()
# Convert to weekly data
nasdaq_df = nasdaq_df.resample("W-FRI").last()
# Add column for YoY% changes
nasdaq_df["Nasdaq YoY%"] = nasdaq_df["Nasdaq"].pct_change(periods=52) * 100
# Drop missing values again
nasdaq_df = nasdaq_df.dropna()
all_data["nasdaq"] = nasdaq_df
logging.info("Nasdaq data fetched.")


# Gold Spot Price
gold_url = "https://auronum.co.uk/wp-content/uploads/2024/09/Auronum-Historic-Gold-Price-Data-5.xlsx"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
response = requests.get(gold_url, headers=headers)
response.raise_for_status()  # Raises a 403 or other HTTPError if one occurs
gold_file = pd.read_excel(BytesIO(response.content))
gold_spot = gold_file[["USD/Gold", "Unnamed: 5"]]
gold_spot = gold_spot.rename(columns={"USD/Gold": "Date", "Unnamed: 5": "Gold Price"})
gold_spot = gold_spot.set_index("Date")
gold_spot = gold_spot.resample("W").mean()
# Yahoo Finance for GLD Price
today = date.today()
gld = yf.download("GLD", start="2004-01-01", end=today, auto_adjust=True, progress=False)
gld = gld["Close"]
# Resample to monthly and calculate weekly return
gld = gld.resample("W").mean()
gld["Weekly Return"] = gld["GLD"].pct_change()
# Extend the spot price based on GLD returns to-date
# Find the last known value of Gold Spot Price
last_spot_price = gold_spot['Gold Price'].iloc[-1]
# Create a new DataFrame to store the extended prices
extended_gold = gold_spot.copy()
for date, row in gld.loc[gold_spot.index[-1]:].iterrows():
    # If the date is already in the spot price data, skip it
    if date in extended_gold.index:
        continue
    # Calculate the next week's spot price based on the previous spot price and GLD weekly return
    weekly_return = row['Weekly Return']
    last_spot_price = last_spot_price * (1 + weekly_return)
    # Append the calculated spot price to the extended dataframe
    extended_gold.loc[date] = last_spot_price
# Sort the extended DataFrame by date
extended_gold = extended_gold.sort_index()
# Add to dictionary
all_data["gold"] = extended_gold
logging.info("Gold data fetched.")


# Dollar Reserves (IMF)
imf_url = "https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/COFER/%2B/G001.AFXRA.CI_USD.SHRO_PT.Q?dimensionAtObservation=TIME_PERIOD&attributes=dsd&measures=all&includeHistory=false"
dollar_reserves = None
# Fetch the data
response = requests.get(imf_url)
# Check for successful response
if response.status_code == 200:
    imf_data = response.json()
    # Grab the values from the response
    values_dict = imf_data["data"]["dataSets"][0]["series"]["0:0:0:0:0"]["observations"]
    values = []
    for k, l in values_dict.items():
        values.append(float(l[0]))
    # Grab the dates
    quarters = []
    quarter_list = imf_data["data"]["structures"][0]["dimensions"]["observation"][0]["values"]
    for i in range(len(quarter_list)):
        quarters.append(quarter_list[i]["value"])
    # Convert to quarter end dates
    dates = [pd.Period(q, freq='Q').end_time.normalize() for q in quarters]
    # Create dataframe
    dollar_reserves = pd.DataFrame(data={"Dollar % Reserves": values}, index=dates)
    dollar_reserves.index.name = "Date"
else:
    logging.error(f"Failed to retrieve data: {response.status_code}")
# Add to dictionary
if dollar_reserves is not None:
    all_data["dollar_reserves"] = dollar_reserves
    logging.info("Dollar Reserves data fetched.")
    
    
# International Debt Securities (BIS)
urls = {} # Create dict for urls
urls["Total"] = "https://stats.bis.org/api/v1/data/WS_DEBT_SEC2_PUB/Q.3P.3P.1.1.C.A.A.TO1.A.A.A.A.A.I/all?startPeriod=1967"
urls["USD"] = "https://stats.bis.org/api/v1/data/WS_DEBT_SEC2_PUB/Q.3P.3P.1.1.C.A.A.USD.A.A.A.A.A.I/all?startPeriod=1967"
ns = {'message': 'http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message'}
# Create empty dataframe
debt_securities = pd.DataFrame()
# Loop through the urls
for type, url in urls.items():
    # Make the request
    response = requests.get(url)
    root = ET.fromstring(response.content)
    dataset = root.find('message:DataSet', ns)
    # Extract observations from the XML tree
    debt_data = []
    # Loop through all <Series> elements
    for series in dataset.findall('Series'):
        # Loop through all <Obs> entries
        for obs in series.findall('Obs'):
            tp = obs.attrib.get('TIME_PERIOD')
            value = obs.attrib.get('OBS_VALUE')
            if value is not None:
                debt_data.append({
                    'Time': tp,
                    'Value': float(value),})
    # Convert to DataFrame
    temp_df = pd.DataFrame(debt_data)
    temp_df.columns = ["Date", f"{type} Debt"]
    # Merge on 'Date'
    if debt_securities.empty:
        debt_securities = temp_df
    else:
        debt_securities = pd.merge(debt_securities, temp_df, on='Date', how='outer')
# Fix dates & convert to billions
debt_securities["Date"] = pd.PeriodIndex(debt_securities["Date"], freq="Q").to_timestamp(how="end").normalize()
debt_securities = debt_securities.set_index("Date")
debt_securities = debt_securities / 1000
# Add to dictionary
if not debt_securities.empty:
    all_data["debt_securities"] = debt_securities
    logging.info("Debt Securities data fetched.")


# European Indices
tickers = ["^GDAXI", "^FCHI"]
# Loop through each ticker and download the data
european_indices = pd.DataFrame()
for ticker in tickers:
    # Download the close prices
    temp_yf = yf.download(ticker, start="2000-01-01", end=today, interval="1d", auto_adjust=True, progress=False)["Close"]
    # Rename the column to the ticker name
    temp_yf.rename(columns={"Close": ticker}, inplace=True)
    # Merge into the main dataframe
    if european_indices.empty:
        european_indices = temp_yf
    else:
        european_indices = european_indices.merge(temp_yf, left_index=True, right_index=True, how="outer")
european_indices = european_indices.resample("W-FRI").last()
european_indices = european_indices.rename(columns={"^GDAXI":"DAX","^FCHI":"CAC40"})
# Add to dictionary
all_data["european_indices"] = european_indices
logging.info("European Indices data fetched.")


# Financial Conditions
fci_dict = {
    "USD": "DTWEXBGS",
    "WTI Crude": "DCOILWTICO",
    "US 10YR": "DGS10",
    "HY Credit Spreads": "BAMLH0A0HYM2",
    "Yield Curve": "T10Y2Y",}
# Separate dict for the Fed FCI given this is weekly data
fed_fci_dict = {
    "Chicago Fed NFCI": "NFCI",
    "FCI Leverage": "NFCILEVERAGE",
    "FCI Credit": "NFCICREDIT",
    "FCI Risk": "NFCIRISK"}
# Create empty dataframes
fci_df = pd.DataFrame()
fed_fci_df = pd.DataFrame()
# Loop through both dictionaries and fetch data
for series_name, series_id in fci_dict.items():
    fci_df[series_name] = fred.get_series(series_id)
for series_name, series_id in fed_fci_dict.items():
    fed_fci_df[series_name] = fred.get_series(series_id)
# Name the date columns
fci_df.index.name = "Date"
fed_fci_df.index.name = "Date"
# Add to all_data dictionary
all_data["financial_conditions"] = fci_df
all_data["fed_fci"] = fed_fci_df
logging.info("Financial Conditions data fetched.")


# Economic Variables (Monthly)
economy_dict = {
    # Leading Indicators
    "Building Permits": "PERMIT",
    "Total Vehicle Sales": "TOTALSA",
    "Heavy Truck Sales": "HTRUCKSSAAR",
    "Consumer Sentiment": "UMCSENT",
    "New Home Sales": "HSN1F",
    # Lagging indicators
    "Unemployment": "UNRATE",
    "Industrial Production": "INDPRO",
    "Labor Force Participation Rate": "CIVPART",
}
# Create empty dataframe and loop through variables
economy_df = pd.DataFrame()
for series_name, series_id in economy_dict.items():
    economy_df[series_name] = fred.get_series(series_id)
economy_df.index.name = "Date"
# Data automatically assumes 1st of month -> change to month end
economy_df.index = economy_df.index + pd.offsets.MonthEnd(0)
# Add Initial Job Claims separately as this is weekly data
job_claims = fred.get_series("ICSA")
job_claims = job_claims.resample("ME").mean()
economy_df["Initial Job Claims"] = job_claims
# Shorten to data after 1977 to reduce missing values
economy_df = economy_df[economy_df.index > "1977-12-31"]
all_data["economic_data"] = economy_df
logging.info("Economic Conditions data fetched.")


# Banking
bank_weekly = {
    "All Loans & Leases": "TOTLL",
    "Total Bank Assets": "TLAACBW027SBOG",
    "Bank Securities": "SBCACBW027SBOG",
}
banking_df = pd.DataFrame()
for series_name, series_id in bank_weekly.items():
    banking_df[series_name] = fred.get_series(series_id)
banking_df.index.name = "Date"
# Convert weekly data to monthly
banking_df = banking_df.resample("ME").mean()
# Monthly bank data
bank_monthly = {
    "Consumer Credit": "TOTALSL",
    "Commercial/Industrial Loans": "BUSLOANS",
}
bank_temp = pd.DataFrame()
for series_name, series_id in bank_monthly.items():
    bank_temp[series_name] = fred.get_series(series_id)
bank_temp.index.name = "Date"
bank_temp.index = bank_temp.index + pd.offsets.MonthEnd(0)
# Merge dataframes
banking_df = pd.merge(banking_df, bank_temp, on='Date', how='left')
banking_df["Consumer Credit"] = banking_df["Consumer Credit"]/1000
# Add to all_data dictionary
all_data["banking"] = banking_df
logging.info("Banking data fetched.")


# Interest Rates
rates_dict = {
    "Effective Fed Funds": "DFF",
    "SOFR": "SOFR",
    "ECB Deposit Rate": "ECBDFR",
}
# Create empty dataframe and loop through variables
rates_df = pd.DataFrame()
for series_name, series_id in rates_dict.items():
    rates_df[series_name] = fred.get_series(series_id)
rates_df.index.name = "Date"
# Resample from daily to monthly data
rates_df = rates_df[rates_df.index > "1998-01-01"]
#rates_df = rates_df.resample("ME").mean()
all_data["interest_rates"] = rates_df
logging.info("Interest Rate data fetched.")


# r star (r*)
# Define the NY Fed URL for retrieving the rstar data and read the file
fed_url = "https://www.newyorkfed.org/medialibrary/media/research/economists/williams/data/Laubach_Williams_current_estimates.xlsx"
data_file = pd.read_excel(fed_url, sheet_name="data")
# Loop through to find starting row for the data
for i in range(0, len(data_file)):
    if data_file.iloc[i, 0] == "Date" and data_file.iloc[i, 2] == "rstar":
        start_row = i + 1
        break
# If successfully found the data then proceed
if start_row:
    # Define dates and rstar value series
    dates = data_file.iloc[start_row:, 0]
    values = data_file.iloc[start_row:, 2]
    # Convert dates to datetime values and create the dataframe
    dates = pd.to_datetime(dates)
    r_star = pd.DataFrame(data={"r*": values})
    # Set and adjust the date index, move to quarter's end since these are quarterly estimates
    r_star.index = dates
    r_star.index.name = "Date"
    r_star.index = r_star.index + pd.offsets.QuarterEnd(0)
    # Add to all_date dictionary
    all_data["rstar"] = r_star
    logging.info("rstar data fetched.")
else:
    # If no start_row then there must be a change in the structure of the file
    logging.info("rstar data not found, file structure must have changed. Please investigate!")


# Inflation
inflation_dict = {
    "Core PCE (Index)": "PCEPILFE",
    "Consumer Price Index": "CPIAUCSL",
    "Producer Price Index": "PPIACO",
    "Prices Paid: Diffusion Index (NY)": "PPCDISA066MSFRBNY",
    "Prices Paid: Diffusion Index (Philly)": "PPCDFSA066MSFRBPHI",
}
# Create empty dataframe and loop through variables
inflation_df = pd.DataFrame()
for series_name, series_id in inflation_dict.items():
    inflation_df[series_name] = fred.get_series(series_id)
inflation_df.index.name = "Date"
# Data automatically assumes 1st of month -> change to month end
inflation_df.index = inflation_df.index + pd.offsets.MonthEnd(0)
all_data["inflation"] = inflation_df
logging.info("Inflation data fetched.")


# Government Spending (Quarterly)
govt_dict = {
    "Total Federal Spending": "FGEXPND",
    "Federal Govt Debt": "GFDEBTN",
    "Interest on Debt": "A091RC1Q027SBEA",
    "Social Benefits Total": "B087RC1Q027SBEA",
    "Defense Spending": "FDEFX",
    "Federal Tax & Other Receipts": "FGRECPT",
}
# Create empty dataframe and loop through variables
govt_df = pd.DataFrame()
for series_name, series_id in govt_dict.items():
    govt_df[series_name] = fred.get_series(series_id) 
# Set index name, move to quarter-end and drop NaN
govt_df.index.name = "Date"
govt_df.index = govt_df.index + pd.offsets.QuarterEnd(0)
govt_df = govt_df[govt_df.index > "1966-03-01"]
govt_df["Federal Govt Debt"] = govt_df["Federal Govt Debt"] / 1000 # Convert to billions
# Add to dictionary
all_data["government_spending"] = govt_df
logging.info("Government Spending data fetched.")


# Other Quarterly Datasets
quarterly_data = {
    "US GDP": "GDP",
    "Real GDP": "GDPC1",
    "Current Account": "IEABC",
    "Household Debt Payments % Disposable Income": "TDSP",
    "Delinquency Rate Credit Card Loans": "DRCCLACBS",
    "Delinquency Rate Consumer Loans": "DRCLACBS",
    "Delinquency Rate All Loans": "DRALACBN",
    "Charge-Off Rate Business Loans": "CORBLACBS",
    "Charge-Off Rate Consumer Loans": "CORCACBS",
    "Margin Loans": "BOGZ1FL663067003Q",
    "Credit Cards: % Accounts Making Minimum Payment": "RCCCBSHRMIN",
    "Net % Banks Tightening: Industrial": "DRTSCILM",
    "Net % Banks Tightening: Credit Card": "DRTSCLCC",
    "Total Mortgage Debt": "ASTMA",
    "Total Private Credit": "CRDQUSAPABIS",
    "Private Residential Fixed Investment": "PRFI", 
    "Real Gross Private Domestic Investment": "GPDIC1",
    "Corporate Debt": "BCNSDODNS",
    "Household Debt": "BOGZ1FL194190005Q",
    "Financial Sector Debt": "DODFS",
}
# Create empty dataframe and loop through variables
quarterly_df = pd.DataFrame()
for series_name, series_id in quarterly_data.items():
    quarterly_df[series_name] = fred.get_series(series_id)
# Set index name, change to quarter-end and shorten dataframe
quarterly_df.index.name = "Date"
quarterly_df.index = quarterly_df.index + pd.offsets.QuarterEnd(0)
quarterly_df = quarterly_df[quarterly_df.index > "1980-01-01"]
# Add to dictionary
all_data["quarterly_data"] = quarterly_df
logging.info("Quarterly data fetched.")


# Other Monthly Datasets
monthly_data = {
    "Future New Orders (Philadelphia)": "NOFDFSA066MSFRBPHI",
    "Future Business Activity (Texas)": "FBACTSAMFRBDAL",
    "New Homes for Sale": "HNFSEPUSSA",
    "Case-Shiller Home Price Index": "CSUSHPINSA",
    "EU Business Confidence Survey": "BSCICP02EZM460S",
    "US Composite Leading Indicator": "USALOLITOAASTSAM",
    "Employment Level": "CE16OV",
    "US Population": "POPTHM",
    "Labour Force Participation 65+": "LNU01375379",
    "US M2": "M2SL",
}
# Create empty dataframe and loop through variables
monthly_df = pd.DataFrame()
for series_name, series_id in monthly_data.items():
    monthly_df[series_name] = fred.get_series(series_id) 
# Set index name, change to month-end and shorten dataframe
monthly_df.index.name = "Date"
monthly_df.index = monthly_df.index + pd.offsets.MonthEnd(0)
monthly_df = monthly_df[monthly_df.index > "1980-01-01"]
# Add to dictionary
all_data["monthly_data"] = monthly_df
logging.info("Monthly data fetched.")


# Annual Data
annual_data = {
    "US % Population 65+": "SPPOP65UPTOZSUSA",
    "US Fertility Rate": "SPDYNTFRTINUSA",
    "Japan % Population 65+": "SPPOP65UPTOZSJPN",
    "Korea Fertility Rate": "SPDYNTFRTINKOR",
}
# Create empty dataframe and loop through variables
annual_df = pd.DataFrame()
for series_name, series_id in annual_data.items():
    annual_df[series_name] = fred.get_series(series_id)
# Set index name, move to year-end and drop NaN
annual_df.index.name = "Date"
annual_df.index = annual_df.index + pd.offsets.YearEnd(0)
annual_df = annual_df.dropna()
# Add to dictionary
all_data["annual_data"] = annual_df
logging.info("Annual data fetched.")


# Fed Supply Chain Index Data
supply_url = "https://www.newyorkfed.org/medialibrary/research/interactives/gscpi/downloads/gscpi_data.xlsx"
supply = pd.read_excel(supply_url, sheet_name="GSCPI Monthly Data")
supply = supply[["Date", "GSCPI"]].dropna()
supply = supply.set_index("Date")
supply.index = pd.to_datetime(supply.index, format='mixed')
# Add to dictionary
all_data["fed_supply_chain"] = supply
logging.info("Supply Chain data fetched.")


# Shiller CAPE
shiller_url = "https://img1.wsimg.com/blobby/go/e5e77e0b-59d1-44d9-ab25-4763ac982e53/downloads/b152b405-8563-4eec-b5c0-b49f95f4e8cf/ie_data.xls?ver=1746381879934"
# Initialize shiller
shiller = None
try:
    shiller_df = pd.read_excel(shiller_url, sheet_name="Data")
    # Take dates from first column and convert to datetime
    shiller_dates = shiller_df["Unnamed: 0"][355:]
    shiller_dates = shiller_dates.dropna()
    shiller_dates = [f"{int(x)}.{int(round((x - int(x)) * 100)):02d}" for x in shiller_dates]
    shiller_dates = pd.to_datetime(shiller_dates, format="%Y.%m")
    # Real S&P 500, Real Earnings & CAPE P/E Ratio
    sp500 = shiller_df["Unnamed: 1"][355:]
    sp500 = pd.to_numeric(sp500, errors='coerce')
    sp500 = sp500.dropna()
    real_sp500 = shiller_df["Unnamed: 7"][355:]
    real_sp500 = real_sp500.dropna()
    real_earnings = shiller_df["Unnamed: 10"][355:]
    real_earnings = real_earnings.dropna()
    cape = shiller_df["Unnamed: 12"][355:]
    cape = cape.dropna()
    # Create the dataframe, set the index and move to month-end
    shiller = pd.DataFrame(data={"Date": shiller_dates, "S&P": sp500, "Real S&P": real_sp500, "Real Earnings": real_earnings, "Shiller"" CAPE P/E Ratio": cape})
    shiller = shiller.set_index("Date")
    shiller.index = shiller.index + pd.offsets.MonthEnd(0)
    # Calculate the trailing 12-month average earnings
    shiller['TTM Real Earnings'] = shiller['Real Earnings'].shift(1).rolling(window=12, min_periods=1).mean()
    # Calculate the TTM P/E Ratio
    shiller['TTM P/E Ratio'] = shiller['Real S&P'] / shiller['TTM Real Earnings']
except:
    logging.error(f"Error occurred while fetching or processing Shiller data")
# Add to dictionary
if shiller is not None:
    all_data["shiller_data"] = shiller
    logging.info("Shiller data fetched.")


# Global M2 & ISM => Read from historical data file
historical = pd.read_excel(os.path.join(os.getcwd(),"data","historical_data.xlsx"), sheet_name=None)
# Global M2
gm2 = historical["Global M2"]
gm2 = gm2.set_index("Date")
all_data["global_m2"] = gm2
# ISM
ism = historical["ISM"]
ism = ism.set_index("Date")
all_data["ism"] = ism
        

# Crypto Data
if args.initial:
    # Read historical data from Excel file
    crypto = pd.read_excel(os.path.join(os.getcwd(),"data","historical_data.xlsx"), sheet_name="Crypto")
    crypto = crypto.set_index("Date")
else:
    # Read from SQL database
    crypto = load_table("crypto")
# Get timestamps for today and start date
today_dt = datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
today_ms = int(today_dt.timestamp())
start_date = today + pd.Timedelta(weeks=-35)
start_date_dt = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)
start_date_ms = int(start_date_dt.timestamp())
# Create empty dataframe and dictionary
crypto_api = pd.DataFrame()
crypto_urls = {}
crypto_urls["BTC"] = f"https://api.coingecko.com/api/v3/coins/bitcoin/market_chart/range?vs_currency=usd&from={start_date_ms}&to={today_ms}"
crypto_urls["ETH"] = f"https://api.coingecko.com/api/v3/coins/ethereum/market_chart/range?vs_currency=usd&from={start_date_ms}&to={today_ms}"
crypto_urls["SOL"] = f"https://api.coingecko.com/api/v3/coins/solana/market_chart/range?vs_currency=usd&from={start_date_ms}&to={today_ms}"
crypto_urls["SUI"] = f"https://api.coingecko.com/api/v3/coins/sui/market_chart/range?vs_currency=usd&from={start_date_ms}&to={today_ms}"
# Loop through each token
for token, url in crypto_urls.items():
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Error downloading data for {token}")
    prices = response.json().get("prices", [])
    temp_df = pd.DataFrame(prices, columns=["Date", token])
    temp_df["Date"] = pd.to_datetime(temp_df["Date"], unit='ms')
    # Merge on 'Date'
    if crypto_api.empty:
        crypto_api = temp_df
    else:
        crypto_api = pd.merge(crypto_api, temp_df, on='Date', how='outer')
    time.sleep(1)
# Set date index
crypto_api = crypto_api.set_index("Date")
# Add the new data to the existing data
last = crypto.index[-1]
crypto_api = crypto_api[crypto_api.index > last]
crypto_merged = pd.concat([crypto, crypto_api], axis=0)
all_data["crypto"] = crypto_merged
logging.info("Crypto data fetched.")


    
# Loop through each dataframe in the dictionary and add to SQL database
for table_name, df in all_data.items():
    # If --initial argument is used, create new tables in database
    if args.initial:
        # Replace the table with the full dataset
        df.to_sql(table_name, engine, if_exists='replace', index=True)
        logging.info(f"Table '{table_name}' created.")
    else:
        # Incremental load: insert only new rows
        latest_date_query = f"""SELECT MAX("Date") FROM {table_name};"""
        latest_date = pd.read_sql(latest_date_query, engine).iloc[0, 0]

        if latest_date is not None:
            df = df[df.index > latest_date]
        
        if not df.empty:
            df.to_sql(table_name, engine, if_exists='append', index=True)
            logging.info(f"Appended {len(df)} new rows to '{table_name}'.")
        else:
            logging.info(f"No new data for '{table_name}'.")
            

# Save to Excel if in debug mode
if args.debug:
    with pd.ExcelWriter(os.path.join(os.getcwd(),"data","data_debug.xlsx"), engine="xlsxwriter") as data_writer:
        for sheet_name, df in all_data.items():
            df.to_excel(data_writer, sheet_name=sheet_name)
    logging.info("Debug data saved to Excel.")