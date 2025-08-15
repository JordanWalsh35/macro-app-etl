import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from helper import load_table, plot_datasets, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read data sources
tables = ["financial_conditions", "debt_securities", "dollar_reserves", "quarterly_data", "nasdaq"]
data = {name: load_table(name) for name in tables}


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Dollar Reserve Status")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page tracks key metrics related to the U.S. dollar’s role as the world’s reserve currency. For decades, the dollar has maintained a dominant position in foreign exchange reserves, global trade, and 
                international debt markets. However, growing debate among analysts raises the question of whether a new monetary regime could emerge within our lifetimes.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 1. Share of Reserves
    st.markdown("<h4 style='text-align: left;'>Dollar % Share of Global FX Reserves</h4>", unsafe_allow_html=True)
    st.write("""The chart below tracks the dominance of the dollar in global reserves on a quarterly basis since 1999. This data provided by the IMF shows a clear downward trend over time and many commentators 
                have pointed to this as evidence that the dollar's days of global dominance are numbered. At the very least, it looks like the trend is towards a multi-polar world where a greater percentage of FX reserves 
                are held in other currencies.""")
    fig1 = basic_plot(df=data["dollar_reserves"], series_name="Dollar % Reserves", start_date="1999-03-01")
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: USD % of Global FX Reserves</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. Share of International Debt
    st.markdown("<h4 style='text-align: left;'>Dollar % Share of International Debt Securities</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the share of international debt securities denominated in U.S. dollars from 1967 onward. In the late 1960s, dollar dominance was nearly absolute, with over 95% of global issuance priced in 
                USD — peaking at around 98.5% in 1968. This reflected the structure of the Bretton Woods system, where the dollar served as the anchor of global finance. Over the following decades, the share declined as 
                capital markets matured and alternative currencies gained traction. Still, the dollar remains the preeminent currency for global debt issuance, with its current share around 45%. 
                This figure hit a low of 28% in 2008 but has been rising since. Notably, shifts in this metric tend to correlate with the value of the dollar itself. The secular dollar bull markets from 1980 to 1985 and 
                from 2009 to the present are both reflected in the chart, each corresponding to a rise in dollar-denominated debt. This dynamic exists because debt issuance in a currency creates demand for it — particularly 
                in times of crisis — while at the same time, global demand for a currency encourages new debt issuance in that denomination.""")
    data["debt_securities"]["% Debt USD"] = (data["debt_securities"]["USD Debt"] / data["debt_securities"]["Total Debt"]) * 100
    fig2 = basic_plot(df=data["debt_securities"], series_name="% Debt USD", start_date="1967-03-01")
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: USD % of International Debt Securities</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. Plot of US Dollar Index
    st.markdown("<h4 style='text-align: left;'>US Dollar Index</h4>", unsafe_allow_html=True)
    st.write("""The chart below shows the Nominal Broad U.S. Dollar Index, which reflects the dollar’s value against a weighted basket of foreign currencies. As discussed above, the dollar has been in a secular bull market 
                since 2009, despite the decline in the dollar's share of FX reserves. As mentioned one explanation for this could be the increase in dollar-denominated debt over the same time period, creating a demand for 
                dollars to service these debts. Another is the strong demand for U.S. financial assets, as global investors seek higher returns and perceived safety in U.S. markets.""")
    fig3 = basic_plot(df=data["financial_conditions"], series_name="USD", start_date="2016-01-01")
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: Nominal Broad U.S. Dollar Index</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. Current Account
    st.markdown("<h4 style='text-align: left;'>Current Account as a % of GDP</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the U.S. current account balance as a percentage of GDP, a key indicator of the country’s net trade and income flows with the rest of the world. Persistent current account deficits reflect 
                the fact that the U.S. imports more goods, services, and capital than it exports—something made possible by the dollar’s status as the global reserve currency. This status allows the U.S. to finance deficits 
                by issuing dollar-denominated assets that are in high demand globally. However, sustained deficits also imply a growing reliance on foreign capital inflows, which ties the stability of financial markets to 
                the continued global confidence in the dollar and U.S. assets.""")
    data["quarterly_data"]["Current Account"] = data["quarterly_data"]["Current Account"] / 1000
    data["quarterly_data"]["Current Account / GDP"] = (data["quarterly_data"]["Current Account"] / data["quarterly_data"]["US GDP"]) * 100
    fig4 = basic_plot(df=data["quarterly_data"], series_name="Current Account / GDP", start_date="1999-03-01")
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: US Current Account as a % of GDP</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 5. Current Account YoY% vs Nasdaq YoY%
    st.markdown("<h4 style='text-align: left;'>Current Account YoY% vs Nasdaq YoY%</h4>", unsafe_allow_html=True)
    st.write("""Here we see evidence of a relationship between the current account and equity market returns, supporting the idea that one reason the U.S. runs persistent current account deficits is due to foreign capital 
                flowing in to chase U.S. market performance. The chart compares the year-over-year returns of the Nasdaq with the year-over-year percentage change in the current account balance. A positive % change indicates 
                that the deficit is widening (becoming more negative), while a negative change reflects an improving balance. Notably, the relationship reveals that Nasdaq returns tend to lead changes in the current account, 
                which is why the current account data has been shifted backward by six months on the chart. This suggests that market gains come first, followed by capital inflows from abroad reacting to those returns.""")
    current_account = data["quarterly_data"].copy()
    current_account["Current Account YoY%"] = current_account["Current Account"].pct_change(periods=4, fill_method=None) * 100
    current_account.index = current_account.index + pd.DateOffset(months=-6)
    fig5 = plot_datasets(primary_df=current_account, secondary_df=data["nasdaq"], primary_series="Current Account YoY%", secondary_series="Nasdaq YoY%", start_date="2003-07-01", primary_range=[-75, 100], secondary_range=[-60, 100])
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: Change in Current Account vs Nasdaq Returns</h6>", unsafe_allow_html=True)