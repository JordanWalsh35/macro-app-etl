import os
import pandas as pd
import streamlit as st
from helper import load_table, plot_datasets, plot_with_constant

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Load tables
tables = ["ism", "nasdaq", "monthly_data", "quarterly_data", "global_m2_btc" "model_1", "model_2", "economic_data", "financial_conditions"]
data = {name: load_table(name) for name in tables}

# Read the ISM data & adjust
ism_df = data["ism"]
ism_df["New Orders - Inventories"] = ism_df["ISM New Orders"] - ism_df["ISM Inventories"]
ism = ism_df[ism_df.index > "2007-01-01"].copy()
# NASDAQ data
nasdaq_yoy = data["nasdaq"][["Nasdaq YoY%"]]
nasdaq_yoy = nasdaq_yoy[nasdaq_yoy.index > "2007-01-01"]
# Future New Orders
future_orders = data["monthly_data"][["Future New Orders (Philadelphia)"]]
future_orders = future_orders[future_orders.index > "2007-01-01"]
# Future Business Activity
future_business_activity = data["monthly_data"][["Future Business Activity (Texas)"]]
future_business_activity = future_business_activity[future_business_activity.index > "2007-01-01"]
# Residential & Domestic Fixed Investment
residential = data["quarterly_data"][["Private Residential Fixed Investment"]]
domestic = data["quarterly_data"][["Real Gross Private Domestic Investment"]]
# Modelling ISM
model_1 = data["model_1"]
model_2 = data["model_2"]
ism1 = ism_df[ism_df.index >= model_1.index[0]].copy()
ism2 = ism_df[ism_df.index >= model_2.index[0]].copy()
# Read Building Permit data
permits = data["economic_data"][["Building Permits"]]
permits["Permits YoY%"] = permits["Building Permits"].pct_change(periods=12) * 100
permits_yoy = permits[["Permits YoY%"]].dropna()
permits_yoy = permits_yoy[permits_yoy.index > "2007-01-01"]
# Yield Curve data
yield_curve = data["financial_conditions"][["Yield Curve"]]
yc = yield_curve[yield_curve.index > "2010-01-01"].copy()
# Composite Leading Indicator
CLI = data["monthly_data"][["US Composite Leading Indicator"]]
CLI = CLI[CLI.index > "2007-01-01"]
# Read Banks Tightening data
tightening = data["quarterly_data"][["Net % Banks Tightening: Industrial"]]
tightening = tightening[tightening.index > "2007-01-01"]
tightening = tightening * -1
# EU Business Confidence
eu_business_confidence = data["monthly_data"][["EU Business Confidence Survey"]]
eu_business_confidence = eu_business_confidence.dropna()


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])
with col2:
    # Create the title for the page
    st.title("The Business Cycle")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""Business cycle analysis is crucial to understanding the economy and financial assets, since there is some amount of cyclicality in every market. In this analysis the business cycle is represented by the ISM Manufacturing PMI (Purchasing Managers' Index). 
                This is a key economic indicator that tracks the health of the US manufacturing sector. It's a monthly survey of purchasing and supply executives in industrial companies, compiled by the Institute for Supply Management (ISM). 
                A reading above 50 indicates expansion, while below 50 signals contraction. Because the PMI reliably leads changes in GDP and corporate earnings, it plays a critical role in shaping expectations for asset price returns, with markets often responding sharply to shifts in momentum captured by this indicator.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Asset Returns heading
    st.markdown("<h2 style='text-align: center;'>Business Cycle & Asset Returns</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 1. Plot ISM vs Nasdaq YoY%
    st.markdown("<h4 style='text-align: left;'>ISM PMI vs Nasdaq YoY%</h4>", unsafe_allow_html=True)
    st.write("""This first chart shows how closely year-over-year returns of the Nasdaq are correlated with the ISM PMI. The same chart can of course be replicated for the S&P 500 which follows the same pattern. 
                This is because stock returns are correlated with corporate earnings, and the natural cyclicality of earnings is tied to the business cycle.""")
    fig1 = plot_datasets(primary_df=ism, secondary_df=nasdaq_yoy, primary_series="ISM", secondary_series="Nasdaq YoY%", secondary_range=[-60, 80])
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: ISM PMI vs YoY% Returns of NASDAQ Composite Index</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)


    # 2. Plot ISM vs BTC YoY%
    st.markdown("<h4 style='text-align: left;'>ISM PMI vs Bitcoin YoY%</h4>", unsafe_allow_html=True)
    st.write("""Bitcoin has also followed a similar pattern so far in its short lifespan, which makes sense for two key reasons. 
                First, as the business cycle strengthens, investor confidence tends to rise, pushing capital further out the risk curve - a dynamic that benefits speculative assets like Bitcoin. 
                More importantly, as discussed in Section 3 (Liquidity), Bitcoin is highly sensitive to shifts in the money supply. Because liquidity itself tends to expand and contract with the business cycle, 
                Bitcoin's correlation with the ISM reflects its deeper link to macroeconomic conditions.""")
    btc_df = data["global_m2_btc"][["BTC Price"]]
    btc_monthly = btc_df.resample("ME").mean()
    btc_monthly["BTC YoY%"] = btc_monthly["BTC Price"].pct_change(periods=12) * 100
    btc_monthly = btc_monthly.drop(columns=["BTC Price"]).dropna(subset=["BTC YoY%"])
    ism_btc = ism[ism.index > btc_monthly.index[0]]
    # Create and show the plot
    fig2 = plot_datasets(primary_df=ism_btc, secondary_df=btc_monthly, primary_series="ISM", secondary_series="BTC YoY%", primary_range=[40, 70], secondary_range=[-150, 700])
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: ISM vs YoY% Returns of Bitcoin</h6>", unsafe_allow_html=True)
    
    
    # Brief comment on other assets
    st.write("""In fact, many assets have a similarly strong correlation with the ISM. Section 2 (Financial Conditions) shows the correlation between the ISM and the dollar, oil prices, 10-year Treasury yields 
                and high yield credit spreads. Industrial commodities like copper also follow a similar pattern.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Leading Indicators heading
    st.markdown("<h2 style='text-align: center;'>Leading Indicators</h2>", unsafe_allow_html=True)
    st.write("""Now that the correlation between the ISM and asset returns has been established, the next logical step is to see if we can find other indicators that lead the business cycle itself. 
                These leading indicators might give us some idea of where the ISM is going (at least directionally) over the next 3-9 months, depending on which indicator we use. 
                While precise market timing is not the goal - as this is extremely difficult, this approach will at least give us a better probabilistic understanding of when returns are likely approaching a cyclical peak or trough.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 3. ISM PMI vs ISM New Orders Minus Inventories
    st.markdown("<h4 style='text-align: left;'>ISM New Orders Minus Inventories</h4>", unsafe_allow_html=True)
    st.write("""The ISM New Orders Minus Inventories spread is a composite indicator derived from the ISM Manufacturing PMI that tracks the difference between the New Orders Index and the Inventories Index. 
                This spread is particularly valuable because it reflects the balance between demand (new orders) and supply (inventories) within the manufacturing sector. A positive spread indicates that new orders are growing faster than inventories, 
                suggesting robust demand and likely future production increases. Conversely, a negative spread indicates that inventories are accumulating faster than new orders, signaling potential slowdowns or excess supply. Historically, 
                this indicator tends to lead the broader ISM PMI because changes in orders relative to inventories often precede adjustments in production levels. As such, monitoring the ISM New Orders Minus Inventories spread can provide early insights into economic momentum and manufacturing cycle shifts.""")
    new_orders_inventories = ism_df[["New Orders - Inventories"]].copy()
    new_orders_inventories = new_orders_inventories.dropna()
    new_orders_inventories["New Orders - Inventories (Smoothed)"] = new_orders_inventories["New Orders - Inventories"].rolling(window=2, center=False).mean()
    new_orders_inventories.index = new_orders_inventories.index + pd.DateOffset(months=3)
    new_orders_inventories = new_orders_inventories[new_orders_inventories.index > "2000-01-01"]
    ism3 = ism_df[ism_df.index > "2000-01-01"].copy()
    fig3 = plot_datasets(primary_df=ism3, secondary_df=new_orders_inventories, primary_series="ISM", secondary_series="New Orders - Inventories (Smoothed)", primary_range=[35, 70], secondary_range=[-22, 32])
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: ISM PMI vs ISM New Orders minus ISM Inventories (Pushed 3 Months)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. ISM vs Future Business Activity (Texas)
    st.markdown("<h4 style='text-align: left;'>Future Business Activity (Texas)</h4>", unsafe_allow_html=True)
    st.write("""The Future Business Activity Index, published by the Federal Reserve Bank of Dallas as part of its Texas Manufacturing Outlook Survey, is a diffusion index that gauges manufacturers' expectations for overall business conditions over the next six months. 
                As a forward-looking measure, it reflects how firms anticipate changes in production, demand, and economic conditions in the Texas region. An increase in the index indicates optimism and planned expansion, while a decline signals caution or concerns about future business prospects. 
                Since manufacturers often adjust their expectations before actual shifts in output or orders, this index tends to lead broader economic indicators like the ISM Manufacturing PMI (which is why the data is pushed 3 months). 
                The raw dataset is quite noisy so this a smoothed 2-month moving average.""")
    future_business_activity["Future Business Activity (Smoothed)"] = future_business_activity["Future Business Activity (Texas)"].rolling(window=2, center=False).mean()
    future_business_activity.index = future_business_activity.index + pd.DateOffset(months=3)
    fig4 = plot_datasets(primary_df=ism, secondary_df=future_business_activity, primary_series="ISM", secondary_series="Future Business Activity (Smoothed)", primary_range=[35, 70], secondary_range=[-44, 60])
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: ISM vs Future Business Activity for Texas District (Pushed 3 Months)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 5. ISM vs Future New Orders (Philadelphia District)
    st.markdown("<h4 style='text-align: left;'>Future New Orders (Philadelphia)</h4>", unsafe_allow_html=True)
    st.write("""The Future New Orders Index, published by the Federal Reserve Bank of Philadelphia, is a diffusion index that measures manufacturers’ expectations for new orders over the next six months within the Philadelphia district. 
                As a forward-looking indicator, it reflects business sentiment and planned production changes, making it highly sensitive to shifts in economic confidence. Historically, increases in the index suggest that firms expect stronger demand and are likely to ramp up production, 
                while declines signal caution or anticipated slowdowns. Since changes in new orders typically precede actual shifts in manufacturing output, this index often leads broader economic indicators like the ISM Manufacturing PMI. 
                As such, monitoring the Future New Orders Index can provide early signals of turning points in the business cycle and guide expectations for manufacturing activity. Similar to above, this is also a smoothed 
                2-month average.""")
    future_orders["Future New Orders (Smoothed)"] = future_orders["Future New Orders (Philadelphia)"].rolling(window=2, center=False).mean()
    future_orders.index = future_orders.index + pd.DateOffset(months=6)
    fig5 = plot_datasets(primary_df=ism, secondary_df=future_orders, primary_series="ISM", secondary_series="Future New Orders (Smoothed)", primary_range=[35, 70], secondary_range=[-25, 80])
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: ISM vs Future New Orders for Philadelphia District (Pushed 6 Months)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    
    # 6. ISM vs Residential Investment
    st.markdown("<h4 style='text-align: left;'>Residential Investment as a % of Total Private Investment (YoY% Change)</h4>", unsafe_allow_html=True)
    st.write("""Residential Fixed Investment (RFI) as a percentage of Fixed Private Investment (FPI) is one of the best leading indicators of the business cycle. It reflects the share of private sector investment directed toward housing and related construction. 
                Fixed Private Investment encompasses all non-government investment in fixed assets. Since residential investment is highly sensitive to interest rates and consumer sentiment, changes in RFI as a share of FPI often signal shifts in economic momentum. 
                A decline in this ratio typically precedes economic slowdowns, as households become more cautious about large purchases, while an increase suggests renewed confidence and rising housing demand. It typically leads the business cycle by about 9 months, 
                which gives us considerable insight into how things are likely to play out over a longer timeframe.""")
    # Add domestic investment to main dataframe and calculate residential/domestic ratio
    residential["Domestic Investment"] = domestic["Real Gross Private Domestic Investment"]
    residential["Residential % Domestic"] = residential["Private Residential Fixed Investment"] / residential["Domestic Investment"]
    # Get the YoY% change in Residential as % of Domestic
    residential["Residential/Domestic YoY%"] = residential["Residential % Domestic"].pct_change(periods=4) * 100
    residential = residential[residential.index > "1990-01-01"]
    residential.index = residential.index + pd.DateOffset(months=9)
    # Alter ISM timeframe to 1990
    ism_res = ism_df[ism_df.index > "1990-09-01"]
    fig6 = plot_datasets(primary_df=ism_res, secondary_df=residential, primary_series="ISM", secondary_series="Residential/Domestic YoY%", primary_range=[33, 70], secondary_range=[-27, 30])
    st.plotly_chart(fig6, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 6: ISM vs Residential/Domestic Fixed Investment YoY% (Pushed 9 months)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Creating a model heading
    st.markdown("<h2 style='text-align: center;'>Creating Composite Models to Predict ISM</h2>", unsafe_allow_html=True)
    st.write("""It is possible to construct a regression-based model to forecast the ISM over a specified horizon, with the forecast window (X months ahead) determined by the chosen lead time. This involves assembling a 
                dataset of leading indicators, shifting each variable forward in time by the appropriate number of months, regressing the training data against historical ISM values, and then generating out-of-sample 
                forecasts. The indicators tested include those highlighted above—ISM Orders minus Inventories, Future Business Activity, Future New Orders, and Residential Investment as a Share of Domestic Private 
                Investment—as well as two financial conditions variables: WTI crude oil prices and the U.S. dollar index. To assess predictive validity, Granger causality tests were conducted across various lags for each 
                variable. Based on this analysis, two final models were developed, with results presented below.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 7. Model 1: Future New Orders & Residential % Domestic
    st.markdown("<h4 style='text-align: left;'>Model 1: Future New Orders & Residential/Domestic Investment</h4>", unsafe_allow_html=True)
    st.write("""This model incorporates two key variables: Future New Orders and Residential Investment as a Percentage of Domestic Private Investment. Future New Orders is shifted forward by six months and Residential 
                Investment by nine months, allowing the model to effectively capture longer-term cyclical trends in the ISM. The training period begins in January 2000, with an 80:20 train-test split. The model achieves a 
                strong out-of-sample R² of approximately 0.70, and generates forecasts for the ISM six months ahead.""")
    fig7 = plot_datasets(primary_df=ism1, secondary_df=model_1, primary_series="ISM", secondary_series="ISM Predicted", primary_range=[40, 65], secondary_range=[42, 63])
    st.plotly_chart(fig7, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 7: Predicting ISM - Model 1 Performance</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 8. Model 2: Orders - Inventories & Future Business Activity
    st.markdown("<h4 style='text-align: left;'>Model 2: Orders minus Inventories & Future Business Activity</h4>", unsafe_allow_html=True)
    st.write("""This model utilizes Orders Minus Inventories and Future Business Activity, producing a higher out-of-sample R² of 0.76. However, the available data for Future Business Activity only begins in 2004, limiting 
                the training window. Designed to forecast the ISM four months into the future, this model focuses on capturing shorter-term dynamics, as the Orders–Inventories spread tends to lead ISM by a shorter lag 
                compared to other macro indicators.""")
    fig8 = plot_datasets(primary_df=ism2, secondary_df=model_2, primary_series="ISM", secondary_series="ISM Predicted", primary_range=[40, 65], secondary_range=[42, 63])
    st.plotly_chart(fig8, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 8: Predicting ISM - Model 2 Performance</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Other relationships heading
    st.markdown("<h2 style='text-align: center;'>Other Significant Relationships</h2>", unsafe_allow_html=True)
    st.write("""There are many other economic variables that have noteworthy relationships with the ISM, they may not correlate as strongly as those mentioned already but they are worth monitoring nevertheless.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 9. ISM vs Building Permits
    st.markdown("<h4 style='text-align: left;'>Building Permits YoY%</h4>", unsafe_allow_html=True)
    st.write("""Building permits are a leading indicator of the business cycle because they reflect future construction activity and developers' confidence in economic conditions. 
                Issued before construction begins, building permits signal intentions to start new residential projects, making them highly sensitive to changes in interest rates, credit availability, and consumer demand. 
                When building permits increase, it indicates optimism about housing demand and economic stability, while a decline suggests caution or reduced confidence.""")
    permits_yoy.index = permits_yoy.index + pd.DateOffset(months=3)
    fig9 = plot_datasets(primary_df=ism, secondary_df=permits_yoy, primary_series="ISM", secondary_series="Permits YoY%", primary_range=[40, 70], secondary_range=[-45, 70])
    st.plotly_chart(fig9, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 9: ISM vs Building Permits YoY% (Pushed 3 Months)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    
    # 10. ISM vs Yield Curve
    st.markdown("<h4 style='text-align: left;'>The Yield Curve</h4>", unsafe_allow_html=True)
    st.write("""The yield curve, specifically the spread between the 10-year and 2-year Treasury yields, has historically shown a strong correlation with the ISM Manufacturing PMI and the broader business cycle. 
                This relationship exists because the yield curve reflects market expectations of future economic conditions. When the curve inverts (short-term rates higher than long-term rates), 
                it signals that investors expect slower growth or a recession, prompting the Federal Reserve to eventually cut rates. This inversion typically precedes a downturn in the ISM PMI by several months, 
                as tighter financial conditions and declining confidence gradually filter through to the real economy. As a result, the yield curve is considered a leading indicator, providing an early warning of economic slowdowns and cyclical downturns.""")
    yc.index = yc.index + pd.DateOffset(months=6)
    ism_yc = ism_df[ism_df.index > "2010-01-01"].copy()
    fig10 = plot_datasets(primary_df=ism_yc, secondary_df=yc, primary_series="ISM", secondary_series="Yield Curve", primary_range=[35, 70], secondary_range=[-2, 3.5])
    st.plotly_chart(fig10, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 10: ISM vs Yield Curve (Pushed 6 months)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 11. ISM vs OECD Composite Leading Indicator
    st.markdown("<h4 style='text-align: left;'>OECD Composite Leading Indicator</h4>", unsafe_allow_html=True)
    st.write("""The OECD Composite Leading Indicator (CLI) for the United States is a forward-looking economic indicator designed to anticipate turning points in the business cycle. Constructed by the Organisation for Economic Co-operation and Development (OECD), 
                the CLI combines various economic variables that tend to change before the overall economy, such as production, new orders, and consumer sentiment. This indicator does not give us as much predictive power over the future direction of the ISM when compared with previous indicators, 
                but since it's smoothed at the peaks and troughs we might be able to get some additional confirmation of when the business cycle is turning by monitoring this chart.""")
    fig11 = plot_datasets(primary_df=ism, secondary_df=CLI, primary_series="ISM", secondary_series="US Composite Leading Indicator", primary_range=[33, 70], secondary_range=[93, 106])
    st.plotly_chart(fig11, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 11: ISM PMI vs OECD Composite Leading Indicator</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 12. ISM vs Net % Banks Tightening Lending Standards
    st.markdown("<h4 style='text-align: left;'>Net % of Banks Tightening Lending Standards (Inverted)</h4>", unsafe_allow_html=True)
    st.write("""The Net Percentage of Banks Tightening Lending Standards is a key indicator of credit conditions that often correlates with the ISM Manufacturing PMI. 
                Derived from the Senior Loan Officer Opinion Survey (SLOOS), this metric reflects how willing banks are to extend credit, particularly for commercial and industrial loans. 
                This can sometimes lead the business cycle but since the relationship can also be coincident or even lagging during financial panics (e.g. see during Covid in the chart), we will place a lower importance on this metric. 
                However, it's still good practice to monitor this as it's a very important variable for the financial system.""")
    fig12 = plot_datasets(primary_df=ism, secondary_df=tightening, primary_series="ISM", secondary_series="Net % Banks Tightening: Industrial", primary_range=[35, 70], secondary_range=[-75, 50])
    st.plotly_chart(fig12, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 12: ISM vs Net % of Banks Tightening Lending Standards (Industrial Loans, Inverted)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Europe Heading
    st.markdown("<h2 style='text-align: center;'>Europe</h2>", unsafe_allow_html=True)
    st.write("""We can also track business cycle survey data for other parts of the world, for example see below to monitor European business confidence.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 13. EU Business Confidence Survey
    st.markdown("<h4 style='text-align: left;'>EU Business Confidence Survey</h4>", unsafe_allow_html=True)
    st.write("""The EU Business Confidence Survey is a diffusion index that measures the sentiment of businesses across the European Union regarding current economic conditions and expectations for the future. Values above 
                0 generally indicate improving business conditions and positive sentiment, while values below 0 suggest deteriorating conditions and pessimism. However, the index's long-term average is often slightly 
                below 0, reflecting a historical tendency for business sentiment to lean negative, especially during periods of economic uncertainty or slow growth. Therefore, while the 0 level serves as a theoretical 
                expansion/contraction line, it’s essential to interpret the index within the context of historical averages and cyclical patterns.""")
    fig13 = plot_with_constant(df=eu_business_confidence, series_name="EU Business Confidence Survey", constant_y=0)
    st.plotly_chart(fig13, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 13: EU Business Confidence Survey</h6>", unsafe_allow_html=True)