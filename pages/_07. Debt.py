import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from helper import load_table, plot_datasets, plot_with_constant, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read debt data
quarterly_data = load_table("quarterly_data")
debt = quarterly_data[["Corporate Debt", "Household Debt", "Financial Sector Debt", "US GDP", "Household Debt Payments % Disposable Income"]]
debt = debt.dropna()
debt["Household Debt"] = debt["Household Debt"] / 1000
debt["Corporate Debt / GDP"] = (debt["Corporate Debt"] / debt["US GDP"]) * 100
debt["Household Debt / GDP"] = (debt["Household Debt"] / debt["US GDP"]) * 100
debt["Financial Debt / GDP"] = (debt["Financial Sector Debt"] / debt["US GDP"]) * 100
# Margin Loans
margin_loans = quarterly_data[["Margin Loans", "US GDP"]]
margin_loans["Margin Loans"] = margin_loans["Margin Loans"] / 1000
margin_loans["Margin Debt / GDP"] = (margin_loans["Margin Loans"] / margin_loans["US GDP"]) * 100


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Debt")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page tracks some important debt metrics to monitor the health of the economy based on its burden of debt. An overburden of debt can lead to economic weakness and financial crises are almost always 
                preceded by a large build-up in the levels of debt.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. Corporate Debt / GDP
    st.markdown("<h4 style='text-align: left;'>Corporate Debt as a % of GDP</h4>", unsafe_allow_html=True)
    st.write("""This ratio measures the level of non-financial corporate debt relative to the size of the economy, providing insight into the leverage of non-financial businesses. A rising ratio indicates that companies 
                are increasing their debt burden faster than economic growth, which can signal financial risk if revenue growth does not keep pace. Tracking this metric helps gauge the sustainability of corporate borrowing 
                and the potential for debt-driven financial stress. The ratio went to completely unsustainable levels during Covid, but since then the rate of increase of corporate debt has come down and has at least been slower 
                than the growth in GDP - bringing this ratio down substantially. However, it is still at a high level on a historical basis, so it's important to monitor how this situation plays out.""")
    fig1 = basic_plot(df=debt, series_name="Corporate Debt / GDP")
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: Non-financial Corporate Debt as % of GDP</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. Household Debt / GDP
    st.markdown("<h4 style='text-align: left;'>Household Debt as a % of GDP</h4>", unsafe_allow_html=True)
    st.write("""This ratio reflects the total debt owed by households as a percentage of the nation’s economic output. It highlights the level of consumer leverage and is a key indicator of financial vulnerability, 
                particularly when debt growth outpaces GDP. A high ratio can indicate that households are over-leveraged, which may reduce consumer spending and increase the risk of defaults during economic downturns. 
                This has come down significantly since the GFC and the average household is in far better shape than it was back then.""")
    fig2 = basic_plot(df=debt, series_name="Household Debt / GDP")
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: Household Debt Payments as % of GDP</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. Household Debt Payments % Disposable Income
    st.markdown("<h4 style='text-align: left;'>Household Debt Payments as a % Disposable Income</h4>", unsafe_allow_html=True)
    st.write("""This metric measures the share of disposable personal income used to service household debt, including mortgages, credit cards, and other loans. A high percentage indicates that households are spending a 
                large portion of their income on debt payments, leaving less room for savings or discretionary spending. Monitoring this ratio helps assess financial stress and household debt sustainability. The data here 
                is in agreement with Figure 2 in showing that the average household has a much more manageable debt burden than in the years leading up to the financial crisis.""")
    fig3 = basic_plot(df=debt, series_name="Household Debt Payments % Disposable Income")
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: Household Debt Payments as a % Disposable Income</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. Financial Sector Debt / GDP
    st.markdown("<h4 style='text-align: left;'>Financial Sector Debt as a % of GDP</h4>", unsafe_allow_html=True)
    st.write("""Financial Sector Debt to GDP measures the total debt held by financial institutions (such as banks, credit unions, and non-bank financial entities) as a percentage of the country’s GDP. This ratio provides 
                insight into the leverage within the financial system, highlighting the extent to which financial firms are reliant on debt to finance their operations. A rising ratio may indicate increased financial risk, 
                as high leverage can amplify vulnerabilities during economic downturns. Monitoring this metric helps assess the stability of the financial sector and its potential impact on the broader economy. Similar to 
                households, this sector has also had a significant deleveraging since the global financial crisis.""")
    fig4 = basic_plot(df=debt, series_name="Financial Debt / GDP")
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: Financial Sector Debt as % of GDP</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 5. Margin Debt / GDP
    st.markdown("<h4 style='text-align: left;'>Margin Debt as a % of GDP</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the ratio of margin debt to Gross Domestic Product (GDP), providing insight into the scale of leverage within the financial markets relative to the overall economy. Margin debt represents 
                the amount of money that investors have borrowed to buy securities, often reflecting risk appetite and speculative activity. A rising ratio indicates that margin debt is growing faster than the economy, 
                suggesting increased leverage and potential vulnerability during market downturns. Conversely, a declining ratio may indicate deleveraging or reduced speculation. Tracking this ratio helps assess systemic 
                risk and potential financial instability, especially when it reaches historically high levels.""")
    fig5 = basic_plot(df=margin_loans, series_name="Margin Debt / GDP")
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: Margin Debt as % of GDP</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)