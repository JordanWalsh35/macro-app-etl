import os
import pandas as pd
import streamlit as st

from dotenv import load_dotenv
from fredapi import Fred
from helper import load_table
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sqlalchemy import create_engine


# Initialize FRED API
load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")
fred = Fred(api_key=FRED_API_KEY)

# Read data sources
tables = ["ism", "monthly_data", "quarterly_data", "financial_conditions"]
data = {name: load_table(name) for name in tables}
ism_df = load_table("ism")
# Add column to ISM df for Orders minus Inventories
ism_df["Orders - Inventories"] = ism_df["ISM New Orders"] - ism_df["ISM Inventories"]


# USD
usd = data["financial_conditions"][["USD"]].copy()
usd = usd.resample("ME").mean()
# WTI Crude
wti = pd.DataFrame(data=fred.get_series("DCOILWTICO"), columns=["WTI"])
wti.index.name = "Date"
wti = wti.resample("ME").mean()
wti.index = wti.index + pd.offsets.MonthEnd(0)
# Future Business Activity
future_business_activity = data["monthly_data"][["Future Business Activity (Texas)"]].copy()
future_business_activity = future_business_activity.dropna()
future_business_activity["Future Business Activity (Smoothed)"] = future_business_activity["Future Business Activity (Texas)"].rolling(window=6, center=False).mean()
# Future New Orders
future_orders = data["monthly_data"][["Future New Orders (Philadelphia)"]].copy()
future_orders["Future New Orders (Smoothed)"] = future_orders["Future New Orders (Philadelphia)"].rolling(window=6, center=False).mean()
# Residential/Domestic Investment
residential = data["quarterly_data"][["Private Residential Fixed Investment"]].copy()
domestic = data["quarterly_data"][["Real Gross Private Domestic Investment"]].copy()
residential["Domestic Investment"] = domestic["Real Gross Private Domestic Investment"]
residential["Residential % Domestic"] = residential["Private Residential Fixed Investment"] / residential["Domestic Investment"]
residential = residential.resample('ME').interpolate(method='cubic')
residential.index = residential.index + pd.offsets.MonthEnd(3)
# New Orders minus Inventories
orders_inventories = ism_df[["Orders - Inventories"]].copy().dropna()
orders_inventories["Orders - Inventories (Smoothed)"] = orders_inventories["Orders - Inventories"].rolling(window=3, center=False).mean()
# Combine input variables
inputs = pd.DataFrame()
inputs["Future New Orders"] = future_orders["Future New Orders (Smoothed)"]
inputs["Future Business Activity"] = future_business_activity["Future Business Activity (Smoothed)"]
inputs["Residential % Domestic"] = residential["Residential % Domestic"]
inputs["USD"] = usd["USD"]
inputs["WTI"] = wti["WTI"]
inputs["Orders - Inventories"] = orders_inventories["Orders - Inventories (Smoothed)"]  
    
    

# Function to make predictions of ISM 
def make_predictions(input_df, data_lag, start_date, variables):
    input_data = input_df.copy()
    # Adjust the timeline
    input_data.index = input_data.index + pd.offsets.MonthEnd(data_lag)
    input_data = input_data[input_data.index > start_date]
    
    # Modelling
    ism = ism_df.copy()
    ism = ism[ism.index > start_date]
    ism_y = ism["ISM"]
    inputs_todate = input_data.loc[ism.index]
    inputs_todate = inputs_todate[variables]
    X_train, X_test, y_train, y_test = train_test_split(inputs_todate, ism_y, test_size=0.2, shuffle=False)
    # Create and fit the model
    model = LinearRegression(fit_intercept=True)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    print("Out-of-sample R²:", r2_score(y_test, y_pred))

    # Full dataset predictions
    input_data = input_data[variables].dropna()
    full_pred = model.predict(input_data)
    prediction_df = pd.DataFrame(data=full_pred, index=input_data.index, columns=["ISM Predicted"])
    # Return the dataframe of ISM predictions
    return prediction_df



# Get the prediction dfs for each model
model_1 = make_predictions(input_df=inputs, data_lag=6, start_date="2000-01-01", variables=["Future New Orders", "Residential % Domestic"])
model_2 = make_predictions(input_df=inputs, data_lag=4, start_date="2005-03-01", variables=["Orders - Inventories", "Future Business Activity"])

# Define the SQL engine
POSTGRES_PW = os.getenv("POSTGRES_PW")
engine = create_engine(f"postgresql://postgres:{POSTGRES_PW}@localhost:5432/macro_data")

# Create dictionary and save to SQL
predictions = {"model_1": model_1, "model_2": model_2}
for table_name, df in predictions.items():
    df.to_sql(table_name, engine, if_exists='replace', index=True)