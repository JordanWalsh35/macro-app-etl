import os
import pandas as pd
import streamlit as st
from helper import load_table, plot_datasets, plot_with_constant, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read data sources
ism = load_table("ism")
financial_conditions = load_table("financial_conditions")
fci = load_table("fed_fci")
fci_start_date = "2000-01-01"
# Add in ISM YoY%
ism["ISM YoY%"] = ism["ISM"].pct_change(periods=12) * 100
main_start_date = "2007-01-01"


# Define a function for preparing the data
def prep_data(data_series):
    # Define the dataframe of daily data
    daily = financial_conditions[[data_series]].dropna()
    # Convert to weekly
    weekly = daily.resample("W-FRI").mean()
    # Add column for YoY% change
    weekly[data_series+" YoY%"] = weekly[data_series].pct_change(periods=52) * 100
    # Remove NaN values and return the dataframe
    df = weekly[[data_series+" YoY%"]].dropna()
    return df


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    # Create the title for the page
    st.title("Financial Conditions")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page is split into two sections, the first of which looks at several factors that influence financial conditions and shows the correlation between financial conditions and the business cycle. 
                The latter section tracks the Chicago Fed's Financial Conditions Index (FCI) and two of its sub-components (leverage and credit). As per the previous section, the business cycle is represented by the US ISM Manufacturing PMI. 
                The financial conditions indicators shown are; the dollar, oil prices, interest rates and credit spreads.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Financial Conditions heading
    st.markdown("<h2 style='text-align: center;'>Financial Conditions & The Business Cycle</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. Plot USD YoY% (Inverted) vs ISM
    st.markdown("<h4 style='text-align: left;'>US Dollar (YoY Change) vs ISM</h4>", unsafe_allow_html=True)
    st.write("""This first chart shows the correlation between the US dollar and the ISM PMI. It uses the Nominal Broad U.S. Dollar Index (DTWEXBGS) to represent the value of the dollar against a basket of foreign currencies. 
                A strengthening dollar tightens financial conditions by making U.S. exports less competitive and increasing the cost of dollar-denominated debt abroad. Conversely, a weaker dollar eases conditions and can stimulate trade and inflation. 
                The dollar has an inverse relationship with ISM PMI: a stronger dollar can weigh on manufacturing and exports, potentially leading to lower PMI readings, especially in export-sensitive sectors. This is why the dollar YoY% series is inverted in this chart.""")
    usd = prep_data("USD")
    usd["USD YoY%"] = usd["USD YoY%"] * -1
    fig1 = plot_datasets(primary_df=ism, secondary_df=usd, primary_series="ISM YoY%", secondary_series="USD YoY%", start_date=main_start_date, primary_range=[-32, 45], secondary_range=[-20, 12])
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: US Dollar YoY% (Inverted) vs ISM YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)


    # 2. Plot WTI Crude YoY% vs ISM
    st.markdown("<h4 style='text-align: left;'>Oil Prices (YoY Change) vs ISM</h4>", unsafe_allow_html=True)
    st.write("""In the chart below oil prices are represented by WTI crude. WTI (West Texas Intermediate) crude is a benchmark for U.S. oil prices and serves as a proxy for energy market dynamics. WTI prices are positively correlated with ISM PMI. The chart below shows this strong relationship.""")
    wti = prep_data("WTI Crude")
    fig2 = plot_datasets(primary_df=ism, secondary_df=wti, primary_series="ISM YoY%", secondary_series="WTI Crude YoY%", start_date=main_start_date, primary_range=[-32, 45], secondary_range=[-70, 130])
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: WTI Crude YoY% vs ISM YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)


    # 3. Plot US 10YR YoY% (Inverted) vs ISM
    st.markdown("<h4 style='text-align: left;'>US 10-Year Bond Yields (YoY Change) vs ISM</h4>", unsafe_allow_html=True)
    st.write("""The yield on the 10-year Treasury reflects investor expectations for growth, inflation, and monetary policy. It is a key benchmark for long-term borrowing costs across the economy. 
                Rising yields can indicate optimism about growth or concerns about inflation""")
    rates = prep_data("US 10YR")
    fig3 = plot_datasets(primary_df=ism, secondary_df=rates, primary_series="ISM YoY%", secondary_series="US 10YR YoY%", start_date=main_start_date, primary_range=[-32, 45], secondary_range=[-80, 150])
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: US 10-Year YoY% vs ISM YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)


    # 4. Plot Credit Spreads (Inverted) vs ISM
    st.markdown("<h4 style='text-align: left;'>High Yield Credit Spreads (YoY Change) vs ISM</h4>", unsafe_allow_html=True)
    st.write("""High yield credit spreads measure the difference in yields between riskier corporate bonds and risk-free Treasuries. Wider spreads indicate higher perceived credit risk and tighter financial conditions, often associated with economic stress or weakening corporate fundamentals. 
                Narrowing spreads, on the other hand, signal investor confidence and easier access to credit. Credit spreads are typically inversely correlated with ISM PMI — when spreads widen, PMI tends to fall, reflecting deteriorating business conditions and risk sentiment. 
                The chart below uses the ICE BofA US High Yield Index Option-Adjusted Spread (BAMLH0A0HYM2) for credit spreads, which is inverted to show the negative correlation.""")
    spreads = prep_data("HY Credit Spreads")
    spreads["HY Credit Spreads YoY%"] = spreads["HY Credit Spreads YoY%"] * -1
    fig4 = plot_datasets(primary_df=ism, secondary_df=spreads, primary_series="ISM YoY%", secondary_series="HY Credit Spreads YoY%", start_date=main_start_date, primary_range=[-32, 38], secondary_range=[-150, 130])
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: HY Credit Spreads YoY% (Inverted) vs ISM YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    
    
    # Fed FCI heading
    st.markdown("<h2 style='text-align: center;'>Chicago Fed Financial Conditions Index</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 5. Plot Chicago Fed's National Financial Conditions Index
    st.markdown("<h4 style='text-align: left;'>National Financial Conditions Index</h4>", unsafe_allow_html=True)
    st.write("""The NFCI provides a comprehensive weekly measure of U.S. financial conditions by aggregating over 100 indicators across money markets, credit markets, and the banking system. 
                A value of zero corresponds to average financial conditions, with positive values indicating tighter-than-average conditions and negative values indicating looser ones. 
                It's useful for capturing broad financial stress and is inversely correlated with economic activity indicators like the ISM PMI — tighter conditions often precede slowdowns in manufacturing and growth.""")
    fig5 = plot_with_constant(df=fci, series_name="Chicago Fed NFCI", constant_y=0, start_date=fci_start_date)
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: Chicago Fed Financial Conditions Index (NFCI)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 6. Plot FCI Leverage Subindex
    st.markdown("<h4 style='text-align: left;'>NFCI Leverage Subindex</h4>", unsafe_allow_html=True)
    st.write("""The Leverage subindex of the NFCI measures the degree of leverage (debt relative to assets or income) in the financial and non-financial sectors. 
                Rising leverage typically reflects increased risk-taking and looser financial conditions, though excessive leverage can signal vulnerability. 
                This component tends to move more gradually and serves as a structural measure of financial buildup that can amplify economic cycles.""")
    fig6 = plot_with_constant(df=fci, series_name="FCI Leverage", constant_y=0, start_date=fci_start_date)
    st.plotly_chart(fig6, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 6: Chicago Fed FCI Leverage Subindex (NFCILEVERAGE)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 7. Plot FCI Credit Subindex
    st.markdown("<h4 style='text-align: left;'>NFCI Credit Subindex</h4>", unsafe_allow_html=True)
    st.write("""The Credit subindex reflects borrowing costs and the availability of credit across households and businesses. 
                It captures risk premiums, spreads, and other factors influencing access to financing. When the credit subindex rises, it indicates that credit is becoming more expensive or harder to obtain — 
                a sign of tightening financial conditions that often correlates with declining ISM PMI, especially as businesses face greater constraints on investment and operations. It follows a very similar pattern as the high yield credit spread index used in Figure 4.""")
    fig7 = plot_with_constant(df=fci, series_name="FCI Credit", constant_y=0, start_date=fci_start_date)
    st.plotly_chart(fig7, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 7: Chicago Fed FCI Credit Subindex (NFCICREDIT)</h6>", unsafe_allow_html=True)