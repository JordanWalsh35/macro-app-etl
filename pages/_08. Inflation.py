import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from helper import load_table, plot_datasets, plot_with_constant

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Inflation data
inflation = load_table("inflation")
inflation["CPI YoY%"] = inflation["Consumer Price Index"].pct_change(periods=12) * 100
inflation["PPI YoY%"] = inflation["Producer Price Index"].pct_change(periods=12, fill_method=None) * 100
inflation = inflation.dropna()
# Supply Chain Index
gscpi = load_table("fed_supply_chain")


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Inflation")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page tracks inflation by monitoring the Consumer Price Index (CPI), the Producer Price Index (PPI), two diffusion indices that can act as leading indicators for CPI and finally the Federal 
                Reserve's supply chain pressure index in case supply chain disruptions occur and lead to inflationary pressures.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 1. US CPI YoY%
    st.markdown("<h4 style='text-align: left;'>US Consumer Price Index YoY%</h4>", unsafe_allow_html=True)
    st.write("""This chart tracks the year-over-year percentage change in the Consumer Price Index (CPI), providing a measure of inflation from the consumer's perspective. It reflects how much prices have increased or 
                decreased compared to the same period a year earlier, indicating the cost-of-living trends and purchasing power changes.""")
    fig1 = plot_with_constant(df=inflation, series_name="CPI YoY%", constant_y=0)
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: US CPI YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. PPI vs CPI
    st.markdown("<h4 style='text-align: left;'>US PPI vs CPI</h4>", unsafe_allow_html=True)
    st.write("""This chart compares the Producer Price Index (PPI) for commodities against the Consumer Price Index (CPI) on a year-over-year basis to assess whether changes in producer prices lead to shifts in consumer inflation. Since PPI 
                measures input costs and CPI measures retail prices, any sustained divergence might indicate margin pressures or delayed inflation transmission. Sometimes we can use PPI as a leading indicator to predict the 
                direction of CPI.""")
    fig2 = plot_datasets(primary_df=inflation, secondary_df=inflation, primary_series="CPI YoY%", secondary_series="PPI YoY%", primary_range=[-5, 15], secondary_range=[-20, 40])
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: US CPI YoY% vs PPI YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. Prices Paid: Diffusion Index (NY)
    st.markdown("<h4 style='text-align: left;'>Prices Paid: Diffusion Index (NY)</h4>", unsafe_allow_html=True)
    st.write("""This index, derived from the New York Fed’s regional surveys, measures the percentage of businesses reporting increased input prices minus those reporting decreases. A reading above zero indicates rising 
                prices, signaling upward cost pressures faced by businesses in the New York region. As seen in the chart, this is a very good leading indicator on the direction of the CPI.""")
    fig3 = plot_datasets(primary_df=inflation, secondary_df=inflation, primary_series="CPI YoY%", secondary_series="Prices Paid: Diffusion Index (NY)", primary_range=[-5, 15], secondary_range=[-35, 135])
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: US CPI vs Prices Paid Diffusion Index for New York</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. Prices Paid: Diffusion Index (Philly)
    st.markdown("<h4 style='text-align: left;'>Prices Paid: Diffusion Index (Philly)</h4>", unsafe_allow_html=True)
    st.write("""Similar to the NY index, this measure from the Philadelphia Fed indicates input cost pressures among manufacturers in the Philadelphia region. Persistent readings above zero highlight inflationary 
                pressures within the regional supply chain.""")
    fig4 = plot_datasets(primary_df=inflation, secondary_df=inflation, primary_series="CPI YoY%", secondary_series="Prices Paid: Diffusion Index (Philly)", primary_range=[-5, 15], secondary_range=[-45, 135])
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: US CPI vs Prices Paid Diffusion Index for Philadelphia</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 5. Fed Supply Chain Pressure Index
    st.markdown("<h4 style='text-align: left;'>Fed Global Supply Chain Pressure Index (GSCPI)</h4>", unsafe_allow_html=True)
    st.write(""" This index captures disruptions and bottlenecks in the global supply chain, incorporating factors like freight costs, shipping times, and supplier delivery delays. Spikes in the index above 0 often correlate 
                with supply chain stress, which can drive cost-push inflation and contribute to higher PPI and CPI readings.""")
    fig5 = plot_with_constant(df=gscpi, series_name="GSCPI", constant_y=0)
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: NY Fed's Global Supply Chain Pressure Index</h6>", unsafe_allow_html=True)