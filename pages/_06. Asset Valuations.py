import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from helper import load_table, plot_datasets, plot_with_constant, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read Shiller data
shiller = load_table("shiller_data")
shiller_full = shiller.copy()
shiller = shiller[shiller.index > "1980-01-01"]
shiller["S&P YoY%"] = shiller["Real S&P"].pct_change(periods=12) * 100
shiller["Earnings YoY%"] = shiller["Real Earnings"].pct_change(periods=12, fill_method=None) * 100
# Gold
gold = load_table("gold")
gold = gold.resample("ME").mean()
gold["S&P"] = shiller["S&P"]
gold["S&P / Gold"] = gold["S&P"] / gold["Gold Price"]
# Gold / M2
monthly_data = load_table("monthly_data")
gold["M2"] = monthly_data["US M2"]
gold = gold.dropna()
gold["Gold / M2"] = (gold["Gold Price"] / gold["M2"]) * 100
# European Indices & Nasdaq
european_indices = load_table("european_indices")
nasdaq = load_table("nasdaq")
european_indices["Nasdaq"] = nasdaq["Nasdaq"]
for col in european_indices.columns:
    european_indices[col + ' Normalized'] = european_indices[col] / european_indices[col].iloc[0]
european_indices["Nasdaq / Dax"] = european_indices["Nasdaq Normalized"] / european_indices["DAX Normalized"]
european_indices["Nasdaq / CAC40"] = european_indices["Nasdaq Normalized"] / european_indices["CAC40 Normalized"]
# Shiller Housing
houses = monthly_data[["Case-Shiller Home Price Index"]]
houses["Houses YoY%"] = houses["Case-Shiller Home Price Index"].pct_change(periods=12, fill_method=None) * 100
houses = houses.dropna()
# New Homes
economic_data = load_table("economic_data")
new_sales = economic_data[["New Home Sales"]]
new_sales = new_sales[new_sales.index > "1980-01-01"]
for_sale = monthly_data[["New Homes for Sale"]]


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Asset Valuations")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page monitors performance and valuations for different asset classes - including some US & European equity indices, gold and housing. For S&P500 earnings, data was taken from Robert Shiller's 
                work on S&P valuations and the CAPE Shiller P/E ratio. Housing performance also uses Shiller's work, namely the Case-Shiller US National Home Price Index.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. Shiller Real Earnings vs Real S&P500
    st.markdown("<h4 style='text-align: left;'>Real Earnings vs Real S&P500</h4>", unsafe_allow_html=True)
    st.write("""This chart compares inflation-adjusted corporate earnings with the real price of the S&P 500, helping to evaluate whether the stock market is supported by fundamental earnings growth. A strong positive 
                relationship indicates that rising real earnings are driving stock prices, while a divergence may signal overvaluation or changing market sentiment.""")
    fig1 = plot_datasets(primary_df=shiller, secondary_df=shiller, primary_series="Real Earnings", secondary_series="Real S&P", primary_range=[0, 450], secondary_range=[0, 6200])
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: Real Earnings vs Real Price of S&P500 Index</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. Shiller CAPE P/E Ratio
    st.markdown("<h4 style='text-align: left;'>Shiller CAPE P/E Ratio</h4>", unsafe_allow_html=True)
    st.write("""The Cyclically Adjusted Price-to-Earnings (CAPE) Ratio, developed by Robert Shiller, measures the price of the S&P 500 relative to its average real earnings over the previous 10 years. This long-term 
                smoothing helps reduce the impact of business cycle fluctuations, providing a more stable indicator of valuation levels compared to traditional P/E ratios. A high CAPE ratio suggests that stocks are 
                expensively valued relative to historical norms, potentially signaling overvaluation, while a low CAPE ratio may indicate undervaluation. Investors use the CAPE ratio to assess the long-term risk and 
                return profile of the stock market.""")
    fig2 = basic_plot(df=shiller_full, series_name="Shiller CAPE P/E Ratio")
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: Shiller CAPE P/E Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. Earnings YoY% vs S&P YoY%
    st.markdown("<h4 style='text-align: left;'>Earnings YoY% vs S&P YoY%</h4>", unsafe_allow_html=True)
    st.write("""This comparison shows the year-over-year percentage change in both corporate earnings and the S&P 500 index. A positive correlation suggests that equity prices rise when earnings improve, reflecting 
                fundamental strength. Conversely, a decoupling between the two may indicate market speculation or changing risk perceptions.""")
    shiller = shiller[shiller.index > "1990-01-01"]
    fig3 = plot_datasets(primary_df=shiller, secondary_df=shiller, primary_series="Earnings YoY%", secondary_series="S&P YoY%", primary_range=[-90, 90], secondary_range=[-60, 60])
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: Real Earnings YoY% vs Real S&P YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. S&P / Gold Ratio
    st.markdown("<h4 style='text-align: left;'>S&P / Gold Ratio</h4>", unsafe_allow_html=True)
    st.write("""This ratio measures the relative performance of equities (S&P 500) to gold, acting as a gauge of risk appetite versus safe-haven preference. A rising ratio indicates stronger stock market performance 
                relative to gold, often seen during economic expansion, while a falling ratio signals risk aversion, economic uncertainty or monetary debasement.""")
    fig4 = basic_plot(df=gold, series_name="S&P / Gold")
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: S&P / Gold Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 5. Gold / M2 Ratio
    st.markdown("<h4 style='text-align: left;'>Gold / M2 Ratio</h4>", unsafe_allow_html=True)
    st.write("""This ratio compares the price of gold to the money supply (M2), providing insight into whether gold is keeping pace with monetary debasement. If this ratio is low, when compared to its history, then it could be argued that gold is cheap. On the 
                other hand if this is high relative to its historical average then gold is arguably expensive or overbought.""")
    gold = gold[gold.index > "1990-01-01"]
    fig5 = basic_plot(df=gold, series_name="Gold / M2")
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: Gold / M2 Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Index Performance Heading
    st.markdown("<h2 style='text-align: center;'>Nasdaq vs Other Indices</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 6. Normalized Performance of Indices
    st.markdown("<h4 style='text-align: left;'>Nasdaq vs DAX vs CAC40</h4>", unsafe_allow_html=True)
    st.write("""This chart compares the performance of the Nasdaq (US), DAX (German), and CAC 40 (French) stock indices from the start of the millennium, with each index normalized to 1 on January 1, 2000. By standardizing 
                the starting point, it clearly highlights the relative growth trajectories of these major stock indices over time, illustrating the divergence or convergence of returns across the US and European markets.""")
    fig6 = make_subplots(specs=[[{"secondary_y": True}]])
    fig6.add_trace(go.Scatter(x=european_indices.index, y=european_indices["Nasdaq Normalized"], name="Nasdaq Normalized"), secondary_y=False)
    fig6.add_trace(go.Scatter(x=european_indices.index, y=european_indices["DAX Normalized"], name="DAX Normalized", line=dict(color="orange")), secondary_y=False)
    fig6.add_trace(go.Scatter(x=european_indices.index, y=european_indices["CAC40 Normalized"], name="CAC40 Normalized", line=dict(color="green")), secondary_y=False)
    fig6.update_layout(width=1000, height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center",x=0.5), margin=dict(t=10, b=20, l=20, r=20))
    st.plotly_chart(fig6, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 6: Nasdaq vs DAX vs CAC40, Normalized at 01/01/2000</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 7. NASDAQ / DAX Ratio
    st.markdown("<h4 style='text-align: left;'>NASDAQ / DAX Ratio</h4>", unsafe_allow_html=True)
    st.write("""This ratio measures the relative performance of the Nasdaq compared to the DAX. A rising ratio indicates that US tech stocks (Nasdaq) are outperforming German equities (DAX), while a declining ratio 
                suggests stronger performance from German stocks. This metric is useful for assessing regional equity market trends and risk appetite differences between the US and Europe.""")
    fig7 = basic_plot(df=european_indices, series_name="Nasdaq / Dax")
    st.plotly_chart(fig7, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 7: NASDAQ / DAX Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 8. NASDAQ / CAC40 Ratio
    st.markdown("<h4 style='text-align: left;'>NASDAQ / CAC40 Ratio</h4>", unsafe_allow_html=True)
    st.write("""Similar to the Nasdaq/DAX ratio, this chart tracks the performance gap between US tech stocks and French equities. An increasing ratio suggests that Nasdaq-listed companies are outperforming French large 
                caps, reflecting investor preference for growth and technology sectors over more traditional European industries.""")
    fig8 = basic_plot(df=european_indices, series_name="Nasdaq / CAC40")
    st.plotly_chart(fig8, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 8: NASDAQ / CAC40 Ratio</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Housing Heading
    st.markdown("<h2 style='text-align: center;'>Housing</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 9. Shiller Home Price Index YoY%
    st.markdown("<h4 style='text-align: left;'>Case-Shiller US National Home Price Index YoY%</h4>", unsafe_allow_html=True)
    st.write("""This indicator shows the year-over-year change in the Shiller Home Price Index, reflecting the annual rate of change in US residential property values. It is an essential gauge of housing market dynamics, 
                helping to identify periods of rapid price appreciation or potential downturns. Changes in this metric often correlate with shifts in credit conditions and consumer wealth.""")
    fig9 = plot_with_constant(df=houses, series_name="Houses YoY%", constant_y=0)
    st.plotly_chart(fig9, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 9: Case-Shiller Home Price Index YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 10. Housing - Inventory vs Sales
    st.markdown("<h4 style='text-align: left;'>New Home Sales vs New Homes for Sale (Inventory)</h4>", unsafe_allow_html=True)
    st.write("""This chart compares the rate of new home sales with the inventory of unsold new homes. An increasing gap between these two series can signal that there may be a shift coming in the housing market. For example, 
                as can be seen in the chart below new sales have stopped growing for quite some time while inventories have been building steadily. It's important to watch this as it could be signalling a downturn to come.""")
    fig10 = plot_datasets(primary_df=new_sales, secondary_df=for_sale, primary_series="New Home Sales", secondary_series="New Homes for Sale", primary_range=[200, 1600], secondary_range=[100, 600])
    st.plotly_chart(fig10, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 10: Housing Inventory (For Sale) vs New Home Sales</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)