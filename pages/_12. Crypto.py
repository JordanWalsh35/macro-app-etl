import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from helper import load_table, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read crypto data
crypto = load_table("crypto")

# Create ratios
crypto["ETH/BTC"] = crypto["ETH"] / crypto["BTC"]
crypto["SOL/BTC"] = crypto["SOL"] / crypto["BTC"]
crypto["SOL/ETH"] = crypto["SOL"] / crypto["ETH"]
crypto["SUI/SOL"] = crypto["SUI"] / crypto["SOL"]


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Crypto")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page tracks relative performance of various crypto tokens in relation to each other. It's important to track these ratios instead of only looking at the $ price so we can make our asset allocation more 
                efficient.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. ETH/BTC Ratio
    st.markdown("<h4 style='text-align: left;'>ETH/BTC Ratio</h4>", unsafe_allow_html=True)
    st.write("""The ETH/BTC ratio measures the relative strength of Ethereum (ETH) against Bitcoin (BTC). When the ratio rises, Ethereum is outperforming Bitcoin, often indicating growing interest in altcoins or decentralized 
                applications. Conversely, a declining ETH/BTC ratio typically signals Bitcoin dominance and a more risk-off environment.""")
    eth_btc = crypto[["ETH/BTC"]].copy().dropna()
    fig1 = basic_plot(df=eth_btc, series_name="ETH/BTC")
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: ETH/BTC Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. SOL/BTC Ratio
    st.markdown("<h4 style='text-align: left;'>SOL/BTC Ratio</h4>", unsafe_allow_html=True)
    st.write("""The SOL/BTC ratio compares Solana’s performance to Bitcoin’s. This ratio in theory should provide us with a similar signal as the ETH/BTC chart above. However, comparing these charts we can see a clear 
                difference in the relative performances. SOL has been much stronger against BTC over this recent cycle than ETH has been, which we can see more clearly in the SOL/ETH chart below. If SOL is becoming 
                a better indicator of market interest in smart contract platforms due to lack of interest in ETH this cycle, then this ratio is arguably a better gauge of risk-on vs risk-off sentiment. Therefore, SOL/BTC 
                rising would be reflective of investors going out the risk curve while the ratio going down reflects a flight to safety and higher bitcoin dominance.""")
    sol_btc = crypto[["SOL/BTC"]].copy().dropna()
    fig2 = basic_plot(df=sol_btc, series_name="SOL/BTC")
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: SOL/BTC Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. SOL/ETH Ratio
    st.markdown("<h4 style='text-align: left;'>SOL/ETH Ratio</h4>", unsafe_allow_html=True)
    st.write("""Here we have the price of SOL relative to ETH. As discussed above, this chart has been incredibly bullish over this cycle which indicates the SOL is massively outperforming ETH. This has also been reflected 
                in blockchain fundamentals with Solana gaining market share in DeFi & other applications, higher revenue earned by the chain and a decline in the revenue earned by Ethereum since moving execution to Layer 2s.""")
    sol_eth = crypto[["SOL/ETH"]].copy().dropna()
    fig3 = basic_plot(df=sol_eth, series_name="SOL/ETH")
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: SOL/ETH Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. SUI/SOL Ratio
    st.markdown("<h4 style='text-align: left;'>SUI/SOL Ratio</h4>", unsafe_allow_html=True)
    st.write("""SUI is a newer competitor in the L1 space but has had very strong fundamentals this cycle and many are claiming it will be to this cycle what Solana was to the 2021 cycle. Therefore, it may be valuable to 
                track the relative performance of SUI compared to SOL to see which asset outperforms this cycle.""")
    sui_sol = crypto[["SUI/SOL"]].copy().dropna()
    fig4 = basic_plot(df=sui_sol, series_name="SUI/SOL")
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: SUI/SOL Ratio</h6>", unsafe_allow_html=True)