import os
import pandas as pd
import streamlit as st
from helper import load_table, plot_datasets, plot_with_constant, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read Economic data
economic_df = load_table("economic_data")
economic_df = economic_df[economic_df.index > "1990-01-01"]
# GDP
quarterly = load_table("quarterly_data")
gdp = quarterly[["US GDP", "Real GDP"]]
gdp["GDP YoY%"] = gdp["US GDP"].pct_change(periods=4) * 100
gdp["Real GDP YoY%"] = gdp["Real GDP"].pct_change(periods=4) * 100
gdp = gdp.dropna()

# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    # Create the title for the page
    st.title("Economic Conditions")
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("""This page tracks several economic datasets to gauge the health of the U.S. economy. The page covers leading, lagging and coincident indicators. Leading indicators can help give us an idea of where the 
                economy is heading in the near future and provide early warning signs of recessions while lagging indicators often hit their worst point several months after a recession or crisis has ended. Coincident 
                indicators are those that move in line with the business cycle.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Leading Indicators heading
    st.markdown("<h2 style='text-align: center;'>Leading Indicators</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 1. Plot of Building Permits
    st.markdown("<h4 style='text-align: left;'>Building Permits</h4>", unsafe_allow_html=True)
    st.write("""Building permits track the number of new housing units authorized by permits in a given period. As a forward-looking indicator, it reflects future construction activity, which in turn signals expectations for economic growth. 
                A rising trend in permits suggests confidence among builders and strong housing demand, while a decline can indicate caution or weakening economic conditions.""")
    permits = economic_df[["Building Permits"]].copy()
    fig1 = basic_plot(df=permits, series_name="Building Permits")
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: Building Permits (PERMIT)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 2. Plot of Total Vehicle Sales
    st.markdown("<h4 style='text-align: left;'>Total Vehicle Sales</h4>", unsafe_allow_html=True)
    st.write("""This indicator captures the total number of new domestic and imported vehicles sold in the U.S., including cars and light trucks. It’s a key barometer of consumer spending and business investment, particularly because auto purchases are large-ticket items often financed by credit. 
                Strong sales typically reflect consumer confidence and economic strength, while declines may point to tightening financial conditions or waning demand.""")
    vehicles = economic_df[["Total Vehicle Sales"]].copy()
    fig2 = basic_plot(df=vehicles, series_name="Total Vehicle Sales")
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: Total Vehicle Sales (TOTALSA)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 3. Plot of Heavy Truck Sales
    st.markdown("<h4 style='text-align: left;'>Heavy Truck Sales</h4>", unsafe_allow_html=True)
    st.write("""This represents the number of large trucks sold and are often used as a proxy for business investment and freight demand. 
                Since heavy trucks are used primarily for commercial transport and logistics, higher sales levels suggest robust economic activity and confidence among businesses in the industrial and distribution sectors.""")
    trucks = economic_df[["Heavy Truck Sales"]].copy()
    fig3 = basic_plot(df=trucks, series_name="Heavy Truck Sales")
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: Heavy Truck Sales (HTRUCKSSAAR)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 4. Plot of Consumer Sentiment
    st.markdown("<h4 style='text-align: left;'>Consumer Sentiment</h4>", unsafe_allow_html=True)
    st.write("""Measured by the University of Michigan’s monthly survey, this index gauges consumers’ outlook on the economy, personal finances, and buying conditions. 
                It’s a valuable leading indicator because shifts in sentiment often precede changes in consumer behavior. 
                When sentiment is high, spending tends to rise, supporting economic growth; when it declines, it may signal caution and slowing demand. """)
    consumer = economic_df[["Consumer Sentiment"]].copy()
    fig4 = basic_plot(df=consumer, series_name="Consumer Sentiment")
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: Consumer Sentiment (UMCSENT)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 5. Plot of New Home Sales
    st.markdown("<h4 style='text-align: left;'>New Home Sales</h4>", unsafe_allow_html=True)
    st.write("""New Home Sales tracks the number of newly constructed single-family homes sold during the month. It reflects both consumer demand and broader health in the housing market. 
                Because home purchases involve long-term financial commitment, rising sales often indicate optimism about future income and economic conditions, while a slowdown may suggest weakening consumer confidence or tighter credit.""")
    homes = economic_df[["New Home Sales"]].copy()
    fig5 = basic_plot(df=homes, series_name="New Home Sales")
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: New Home Sales (HSN1F)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 6. Plot of Initial Job Claims
    st.markdown("<h4 style='text-align: left;'>Initial Job Claims</h4>", unsafe_allow_html=True)
    st.write("""The final leading indicator, Initial Jobless Claims, is a weekly statistic which measures the number of people filing for unemployment benefits for the first time. It’s one of the timeliest indicators of labor market health. 
                Rising claims can signal increasing layoffs and potential economic weakness, while low or declining claims are typically consistent with a strong labor market and economic expansion.""")
    claims = economic_df[["Initial Job Claims"]].copy()
    fig6 = basic_plot(df=claims, series_name="Initial Job Claims", series_range=[0, 1300000])
    st.plotly_chart(fig6, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 6: Initial Job Claims (ICSA)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    

    # Lagging Indicators heading
    st.markdown("<h2 style='text-align: center;'>Lagging Indicators</h2>", unsafe_allow_html=True)
    
    # 7. Plot of Unemployment
    st.markdown("<h4 style='text-align: left;'>Unemployment Rate</h4>", unsafe_allow_html=True)
    st.write("""The unemployment rate measures the percentage of the labor force that is actively seeking but unable to find work. As a lagging indicator, it tends to confirm trends rather than predict them, often rising after a recession has begun and falling after a recovery is well underway. 
                While not predictive, it provides essential insight into the health of the labor market and overall economy, influencing monetary policy and consumer confidence.""")
    unemployment = economic_df[["Unemployment"]].copy()
    fig7 = basic_plot(df=unemployment, series_name="Unemployment")
    st.plotly_chart(fig7, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 7: Unemployment Rate (UNRATE)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 8. Plot of Industrial Production YoY%
    st.markdown("<h4 style='text-align: left;'>Industrial Production</h4>", unsafe_allow_html=True)
    st.write("""This metric tracks the real output of the manufacturing, mining, and utilities sectors. It reflects actual production activity, making it a useful gauge of economic performance, particularly in the goods-producing side of the economy. 
                Because businesses often adjust production in response to shifts in demand, industrial production tends to trail broader economic cycles, confirming trends in GDP and business investment.""")
    industrial = economic_df[["Industrial Production"]].copy()
    industrial["Industrial Production YoY%"] = industrial["Industrial Production"].pct_change(periods=12) * 100
    industrial = industrial.dropna()
    fig8 = plot_with_constant(df=industrial, series_name="Industrial Production YoY%", constant_y=0)
    st.plotly_chart(fig8, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 8: Industrial Production YoY% (INDPRO)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 9. Plot of Labour Force Participation
    st.markdown("<h4 style='text-align: left;'>Labor Force Participation Rate</h4>", unsafe_allow_html=True)
    st.write("""The labor force participation rate measures the proportion of the working-age population that is either employed or actively looking for work. 
                Unlike the unemployment rate, it captures longer-term structural shifts in the labor market, such as demographic changes or economic discouragement. 
                It lags the business cycle because people often return to or exit the labor force based on conditions that have already shifted. Tracking this rate is important for understanding the true availability of labor and potential economic capacity.""")
    labor_force = economic_df[["Labor Force Participation Rate"]].copy()
    fig9 = basic_plot(df=labor_force, series_name="Labor Force Participation Rate")
    st.plotly_chart(fig9, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 9: Labour Force Participation (CIVPART)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    
    # Coincident Indicators heading
    st.markdown("<h2 style='text-align: center;'>Coincident Indicators</h2>", unsafe_allow_html=True)
    
    
    # 10. US GDP YoY%
    st.markdown("<h4 style='text-align: left;'>US GDP YoY%</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the annual growth rate of the nominal Gross Domestic Product, reflecting the total dollar value of goods and services produced in the United States without adjusting for inflation. This 
                metric provides insight into the overall economic expansion or contraction, capturing changes in production, consumption, investment, and government spending. Since it is expressed in current prices, 
                periods of high inflation can artificially boost nominal GDP growth.""")
    fig10 = plot_with_constant(df=gdp, series_name="GDP YoY%", constant_y=0)
    st.plotly_chart(fig10, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 10: US GDP YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    
    
    # 11. US Real GDP YoY%
    st.markdown("<h4 style='text-align: left;'>US Real GDP YoY%</h4>", unsafe_allow_html=True)
    st.write("""Real GDP adjusts the GDP growth rate for inflation, offering a more accurate view of the economy’s actual growth. By using constant dollars, it isolates the volume of economic output from price changes, 
                allowing for better comparison across periods. Real GDP YoY is crucial for assessing long-term economic performance and is often used to gauge the health of the economy without the distortion of inflationary 
                effects.""")
    fig11 = plot_with_constant(df=gdp, series_name="Real GDP YoY%", constant_y=0)
    st.plotly_chart(fig11, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 11: US Real GDP YoY%</h6>", unsafe_allow_html=True)