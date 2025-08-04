import os
import pandas as pd
import streamlit as st
from helper import load_table, plot_datasets, basic_plot, plot_with_constant

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read datasets
tables = ["rstar", "inflation", "interest_rates"]
data = {name: load_table(name) for name in tables}

# r-star
rstar = data["rstar"]
pce = data["Inflation"][["Core PCE (Index)"]]
fed_funds = data["Interest Rates"][["Effective Fed Funds"]]
fed_funds_monthly = fed_funds.resample("ME").mean()
# Convert PCE from index to YoY%, drop NaN values
pce["PCE YoY%"] = pce["Core PCE (Index)"].pct_change(periods=12) * 100
pce = pce[["PCE YoY%"]].dropna()
# Create dataframe were Real Fed Funds Rate = Fed Funds - PCE YoY%
rate_diff =  fed_funds_monthly["Effective Fed Funds"] - pce["PCE YoY%"]
real_rates = pd.DataFrame({"Real Fed Funds": rate_diff})
real_rates = real_rates[real_rates.index > "1998-01-01"]
rstar = rstar[rstar.index > "1998-01-01"]
# SOFR
sofr = data["Interest Rates"][["SOFR"]]
sofr = sofr.dropna()
# ECB Rate
ecb = data["Interest Rates"][["ECB Deposit Rate"]]
ecb = ecb.dropna()


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Central Banking")
    st.write("""This page is concerned with Central Bank policy. It tracks various interest rates to monitor whether monetary policy is tight or loose and if there are any overnight funding concerns.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 1. Plot r-star vs Real Fed Funds
    st.markdown("<h4 style='text-align: left;'>Neutral Rate r* vs Real Fed Funds</h4>", unsafe_allow_html=True)
    st.write("""This chart compares r* (the estimated neutral interest rate) with the Real Fed Funds rate, calculated as the Effective Fed Funds rate minus the Core PCE YoY%. The neutral rate (r*) represents the theoretical 
                equilibrium interest rate that neither stimulates nor restrains economic activity. Plotting it against the Real Fed Funds rate helps assess whether monetary policy is loose, tight, or neutral. When the Real 
                Fed Funds rate is above r*, monetary policy is considered restrictive, while being below r* indicates an accommodative stance. Tracking the gap between these two rates over time provides insights into the 
                Fed’s policy direction relative to the natural rate of interest.""")
    fig1 = plot_datasets(primary_df=rstar, secondary_df=real_rates, primary_series="r*", secondary_series="Real Fed Funds", primary_range=[-6, 8], secondary_range=[-6, 8])
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: Real Fed Funds vs the Neutral Real Rate - r*</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. Effective Fed Funds
    st.markdown("<h4 style='text-align: left;'>Effective Fed Funds Rate</h4>", unsafe_allow_html=True)
    st.write("""The Effective Federal Funds Rate is the interest rate at which depository institutions lend reserve balances to each other overnight. It reflects the cost of short-term interbank borrowing and serves as a 
                key monetary policy tool for the Federal Reserve.""")
    fed_funds_weekly = fed_funds.resample("W").mean()
    fed_funds_weekly = fed_funds_weekly[fed_funds_weekly.index > "2000-01-01"]
    fig2 = basic_plot(df=fed_funds_weekly, series_name="Effective Fed Funds")
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: Effective Fed Funds Rate</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. SOFR
    st.markdown("<h4 style='text-align: left;'>Secured Overnight Financing Rate (SOFR)</h4>", unsafe_allow_html=True)
    st.write("""The Secured Overnight Financing Rate (SOFR) is the benchmark interest rate for overnight loans collateralized by U.S. Treasury securities. It has replaced LIBOR as the primary rate for short-term, 
                risk-free lending in the U.S. financial markets.""")
    fig3 = basic_plot(df=sofr, series_name="SOFR")
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: SOFR Rate</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. ECB Deposit Rate
    st.markdown("<h4 style='text-align: left;'>ECB Deposit Rate</h4>", unsafe_allow_html=True)
    st.write("""The ECB Deposit Facility Rate is the rate at which Eurozone banks can deposit excess reserves overnight at the European Central Bank. It acts as the floor of the ECB’s interest rate corridor, 
                influencing short-term money market rates.""")
    fig4 = basic_plot(df=ecb, series_name="ECB Deposit Rate")
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: ECB Deposit Rate</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 5. SOFR - Fed Funds
    st.markdown("<h4 style='text-align: left;'>SOFR minus Fed Funds</h4>", unsafe_allow_html=True)
    st.write("""This difference represents the spread between the secured and unsecured overnight lending rates. Since SOFR is a secured lending rate (using USTs as collateral) and the Fed Funds market is unsecured lending 
                between banks, we should expect Fed Funds to be slightly higher and therefore this difference should be slightly negative. If SOFR rises above the Fed Funds Rate, it may signal tightness in secured funding 
                markets - possibly due to collateral scarcity or high demand for safe assets, or market stress or disruptions in the repo market, leading to higher secured borrowing costs.""")
    sofr["FF"] = fed_funds["Effective Fed Funds"]
    sofr["SOFR - FF"] = sofr["SOFR"] - sofr["FF"]
    sofr = sofr[sofr.index > "2020-01-01"]
    fig5 = plot_with_constant(df=sofr, series_name="SOFR - FF", constant_y=0)
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: SOFR - Fed Funds</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)