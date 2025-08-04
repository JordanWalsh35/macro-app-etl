import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from helper import load_table, plot_datasets, plot_with_constant

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read data sources
tables = ["ism", "nasdaq", "monthly_data", "quarterly_data", "global_m2_btc", "economic_data", "gold", "shiller_data", "fed_liquidity"]
data = {name: load_table(name) for name in tables}

# BTC & Global M2
gm2_btc = data["global_m2_btc"]
gm2_btc["Global M2 YoY%"] = gm2_btc["Global M2"].pct_change(periods=52, fill_method=None) * 100
gm2 = gm2_btc.copy()
# Monthly data
gm2_btc_monthly = gm2_btc.resample("ME").mean()
gm2_btc_monthly["BTC YoY%"] = gm2_btc_monthly["BTC Price"].pct_change(periods=12, fill_method=None) * 100
gm2_btc_monthly = gm2_btc_monthly.dropna()
# Nasdaq
nasdaq = data["NASDAQ"]
nasdaq = nasdaq[nasdaq.index > "2013-05-01"]
# Gold
gold = data["gold"]
gold["Gold YoY%"] = gold["Gold Price"].pct_change(periods=52, fill_method=None) * 100
gold = gold[gold.index > "2014-05-01"]
# Shiller
shiller = data["shiller_data"]
shiller = shiller[shiller.index > "1980-01-01"]
shiller["P/E YoY%"] = shiller["TTM P/E Ratio"].pct_change(periods=12, fill_method=None) * 100
# Fed balance sheet
fed = data["fed_liquidity"][["Fed Net Liquidity"]]
fed = fed.resample("ME").mean()
fed = fed[fed.index > "2011-01-01"]
# US M2
m2 = data["monthly_data"][["US M2"]]
fed["M2"] = m2["US M2"]
fed = fed.dropna()
fed["Total Liquidity"] = fed["M2"] + fed["Fed Net Liquidity"]
fed["Liquidity YoY%"] = fed["Total Liquidity"].pct_change(periods=12, fill_method=None) * 100
fed = fed.dropna()
# Excess Liquidity
m2 = m2.resample("QE").last()
m2["M2 YoY%"] = m2["US M2"].pct_change(periods=4) * 100
gdp = data["quarterly_data"][["US GDP"]]
gdp["GDP YoY%"] = gdp["US GDP"].pct_change(periods=4) * 100
ex_liq = gdp.copy()
ex_liq["M2 YoY%"] = m2["M2 YoY%"]
ex_liq["Excess Liquidity"] = ex_liq["M2 YoY%"] - ex_liq["GDP YoY%"]
# Yield Curve
yield_curve = data["financial_conditions"][["Yield Curve"]]
yield_curve = yield_curve[yield_curve.index > "2012-01-01"]
# Private Credit
private_credit = data["quarterly_data"][["Total Private Credit"]]
private_credit["GDP"] = gdp["US GDP"]
private_credit["Change in Credit"] = private_credit["Total Private Credit"].diff(4)
private_credit["Credit Change % GDP"] = (private_credit["Change in Credit"]/private_credit["GDP"])*100
private_credit["6 Month Credit Change"] = private_credit["Total Private Credit"].diff(2)
private_credit["6 Month Flow Change"] = private_credit["6 Month Credit Change"].diff(2)
private_credit["Credit Impulse/GDP"] = (private_credit["6 Month Flow Change"] / private_credit["GDP"])*100
private_credit["Credit Impulse Smoothed"] = private_credit["Credit Impulse/GDP"].rolling(window=6, center=False).mean()
private_credit = private_credit.dropna()
# Unemployment
unemployment = data["economic_data"][["Unemployment"]]
unemployment = unemployment[unemployment.index > "1980-06-01"]
unemployment = unemployment*-1
# ISM
ism_df = data["ism"]
ism_df["ISM YoY%"] = ism_df["ISM"].pct_change(periods=12) * 100
ism_df = ism_df[ism_df.index > "1991-06-01"]
# Mortgage Credit
mortgages = data["quarterly_data"][["Total Mortgage Debt"]]
mortgages["GDP"] = gdp["US GDP"]
mortgages["Total Mortgage Debt"] = mortgages["Total Mortgage Debt"]/1000 # Convert to billions
mortgages["Credit Change"] = mortgages["Total Mortgage Debt"].diff(2)
mortgages["Rate of Change"] = mortgages["Credit Change"].diff(3)
mortgages["Credit Impulse/GDP"] = (mortgages["Rate of Change"]/mortgages["GDP"])*100
mortgages["Credit Impulse Smoothed"] = mortgages["Credit Impulse/GDP"].rolling(window=4, center=False).mean()
mortgages = mortgages[mortgages.index > "1988-01-01"]
# Case-Shiller Home Prices
houses = data["monthly_data"][["Case-Shiller Home Price Index"]]
houses["Houses YoY%"] = houses["Case-Shiller Home Price Index"].pct_change(periods=12, fill_method=None) * 100
houses = houses.dropna()


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Liquidity")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page focuses on the importance of liquidity to the economy and financial system. The word liquidity has more than one interpretation. In this context, liquidity refers to the amount of money available in the 
                financial system, including cash, easily accessible funds, and credit. It represents the capacity of the economy to finance transactions, investments, and economic activity. High liquidity means there is ample money 
                and credit available, which generally supports asset prices, business expansion, and consumer spending. Conversely, low liquidity indicates tight financial conditions, often leading to higher borrowing costs, 
                reduced investment, and potential stress in financial markets. Because liquidity is a fundamental driver of economic cycles and market performance, monitoring its levels and trends is crucial for understanding potential 
                shifts in financial conditions and the broader economy.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Liquidity vs Assets heading
    st.markdown("<h2 style='text-align: center;'>Liquidity & Asset Prices</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    

    # 1. Plot of NASDAQ vs Global M2
    st.markdown("<h4 style='text-align: left;'>Nasdaq vs Global M2</h4>", unsafe_allow_html=True)
    st.write("""This first chart shows how the level of liquidity is correlated with the Nasdaq Index. Here liquidity is represented by global M2, which is an aggregated measure of the broad money supply from multiple countries, 
                typically including the world's largest economies. It represents the total amount of money circulating in the global financial system, encompassing cash, checking deposits, savings deposits, and other near-money assets 
                (like money market funds and short-term time deposits). Global is used instead of domestic liquidity because investors around the world buy US assets, so in a sense this makes it a global asset class.""")
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    fig1.add_trace(go.Scatter(x=gm2_btc.index, y=gm2_btc["Global M2"], name="Global M2"), secondary_y=False)
    fig1.add_trace(go.Scatter(x=nasdaq.index, y=nasdaq["Nasdaq"], name="Nasdaq", line=dict(color="orange")), secondary_y=True)
    fig1.update_yaxes(title_text="Global M2", secondary_y=False, range=[0.53e14, 1.17e14])
    fig1.update_yaxes(title_text="Nasdaq", secondary_y=True, type="log")
    fig1.update_layout(width=1000, height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), margin=dict(t=10, b=20, l=20, r=20))
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: Nasdaq vs Global M2</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. Plot YoY% changes in Gold vs Global M2
    st.markdown("<h4 style='text-align: left;'>Gold YoY% vs Global M2 YoY%</h4>", unsafe_allow_html=True)
    st.write("""Gold is a monetary asset that traditionally responds to changes in the money supply while maintaining its value over time. As both investors and central banks purchase gold to hedge against monetary debasement, 
                it logically follows that gold would exhibit a strong correlation with global liquidity. The chart below compares the year-over-year percentage change in gold with the year-over-year percentage change in global M2, 
                highlighting this relationship. Of course, gold also hedges uncertainty and can be a flight-to-safety asset during times of major transition or turmoil, so the YoY correlation won't always be perfect, but over the long 
                term we should expect gold to track the money supply.""")
    fig2 = plot_datasets(primary_df=gm2_btc_monthly, secondary_df=gold, primary_series="Global M2 YoY%", secondary_series="Gold YoY%", primary_range=[-10, 27], secondary_range=[-25, 60])
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: Global M2 YoY vs Gold YoY</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)


    # 3. Plot of Global M2 vs BTC
    st.markdown("<h4 style='text-align: left;'>Bitcoin vs Global M2</h4>", unsafe_allow_html=True)
    st.write("""Bitcoin is often regarded as a digital store of value due to its fixed maximum supply and inherently low inflation rate, earning it the nickname "digital gold". As a liquidity-sensitive asset, 
                Bitcoin's price tends to correlate with changes in global M2, reflecting its responsiveness to shifts in the monetary environment. The chart below illustrates the relationship between global M2 and Bitcoin’s price 
                over the medium term, with global M2 shifted forward by 14 weeks to capture its leading effect on Bitcoin movements.""")
    shifted_m2 = gm2_btc[["Global M2"]].copy()
    shifted_m2.index = shifted_m2.index + pd.Timedelta(weeks=14)
    # Join it back with pd.merge
    combined = pd.merge(gm2_btc["BTC Price"], shifted_m2, left_index=True, right_index=True, how="outer")
    # Sample dataframe to show the most recent data
    sample = combined.iloc[-85:,:]
    # Create and show the plot
    fig3 = plot_datasets(primary_df=sample, secondary_df=sample, primary_series="Global M2", secondary_series="BTC Price", secondary_range=[40000,130000])
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: Bitcoin vs Global M2 (Pushed 14 weeks)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4 Log BTC vs Global M2
    st.markdown("<h4 style='text-align: left;'>Bitcoin vs Global M2 (Historical)</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the relationship between global M2 and Bitcoin over a longer period. Bitcoin is plotted on a logarithmic scale to account for the dramatic price movements over time, as a linear scale would 
                not adequately capture the relationship. The chart clearly illustrates how each Bitcoin bull market coincided with an expansion of the money supply. In the earlier years, Bitcoin's relatively small market 
                cap led to speculative manias and subsequent crashes. However, in more recent data, the correlation between Bitcoin and global M2 appears much tighter, suggesting that Bitcoin is maturing as a macro asset. 
                If this trend continues, we may see fewer speculative bubbles and a more stable correlation between Bitcoin and the money supply.""")
    fig4 = make_subplots(specs=[[{"secondary_y": True}]])
    fig4.add_trace(go.Scatter(x=gm2_btc.index, y=gm2_btc["Global M2"], name="Global M2"), secondary_y=False)
    fig4.add_trace(go.Scatter(x=gm2_btc.index, y=gm2_btc["BTC Price"], name="BTC Price", line=dict(color="orange")), secondary_y=True)
    fig4.update_yaxes(title_text="Global M2", secondary_y=False, range=[0.5e14, 1.17e14])
    fig4.update_yaxes(title_text="BTC Price", secondary_y=True, type="log")
    fig4.update_layout(width=1000, height=600, legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5), margin=dict(t=10, b=20, l=20, r=20))
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: Bitcoin (log scale) vs Global M2</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)


    # 5. Plot YoY% Change in Global M2 & BTC
    st.markdown("<h4 style='text-align: left;'>Bitcoin YoY% vs Global M2 YoY%</h4>", unsafe_allow_html=True)
    st.write("""Here is the same relationship one more time but tracking the YoY% returns of each dataset.""")
    df_yoy = gm2_btc_monthly.dropna(subset=["BTC YoY%", "Global M2 YoY%"])
    # Create and show the plot
    fig5 = plot_datasets(primary_df=df_yoy, secondary_df=df_yoy, primary_series="Global M2 YoY%", secondary_series="BTC YoY%", primary_range=[-4, 30], secondary_range=[-100, 1000])
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: Global M2 YoY vs Bitcoin YoY</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 6. Plot of Excess Liquidity vs S&P P/E YoY
    st.markdown("<h4 style='text-align: left;'>Excess Liquidity vs YoY Change in S&P P/E Ratio</h4>", unsafe_allow_html=True)
    st.write("""Excess liquidity is another useful concept in liquidity analysis. This is calculated by taking the year-over-year change in the money supply and subtracting the year-over-year change in GDP. It's interpreted as the extra 
                money supply created in excess of what was needed to grow the economy. The chart below illustrates how this impacts the change in the 12-month trailing P/E ratio of the S&P. As excess liquidity expands, this acts as a 
                leading indicator for expanding P/E ratios of stocks, when it declines it leads a move to lower P/Es. In post-crash periods this becomes a lagging instead of leading indicator, as the market rebounds on newfound optimism.""")
    fig6 = plot_datasets(primary_df=ex_liq, secondary_df=shiller, primary_series="Excess Liquidity", secondary_series="P/E YoY%", primary_range=[-15, 30], secondary_range=[-85, 170])
    st.plotly_chart(fig6, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 6: Excess Liquidity YoY% vs S&P TTM P/E Ratio YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 7. Plot of Domestic Liquidity vs Yield Curve
    st.markdown("<h4 style='text-align: left;'>Yield Curve vs Domestic Liquidity</h4>", unsafe_allow_html=True)
    st.write("""There is also a notable relationship between the yield curve (10-2 spread) and liquidity, although the strength and timing of the correlation vary across economic cycles. Typically, an inverted yield curve (negative spread) 
                signals tightening liquidity conditions. Conversely, a steep yield curve (positive spread) usually aligns with expanding liquidity, reflecting looser monetary policy and stronger growth expectations. While the yield curve 
                often leads liquidity changes by several months, especially during downturns, rapid policy shifts or market disruptions can temporarily weaken this relationship. So, while we should avoid relying too heavily on this 
                correlation to predict future trends, it does have some value under the right circumstances. In this chart domestic liquidity for the US is the sum of M2 and the Fed's balance sheet.""")
    fig7 = plot_datasets(primary_df=fed, secondary_df=yield_curve, primary_series="Liquidity YoY%", secondary_series="Yield Curve", primary_range=[-9, 35], secondary_range=[-1.3, 5.5])
    st.plotly_chart(fig7, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 7: Yield Curve vs Domestic Liquidity YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    
    # Credit heading
    st.markdown("<h2 style='text-align: center;'>Credit Creation</h2>", unsafe_allow_html=True)
    st.write("""An essential aspect of liquidity analysis is tracking credit creation within the private sector. Credit can originate from both banks and non-bank institutions, but banks play a particularly crucial role because they 
                generate new money supply when issuing loans. As a result, bank lending has a substantial impact on overall liquidity levels in the economy.""")
    st.markdown("<br>", unsafe_allow_html=True)


    # 8. Private Credit Change vs Unemployment
    st.markdown("<h4 style='text-align: left;'>Change in Private Credit vs Unemployment</h4>", unsafe_allow_html=True)
    st.write("""The next chart compares the change in private credit as a percentage of GDP with the unemployment rate (inverted), highlighting the relationship between credit growth and labor market conditions. 
                Since increased credit creation typically signals economic expansion and rising demand, it often correlates with lower unemployment. By inverting the unemployment rate, the chart more clearly shows how periods 
                of robust credit growth tend to coincide with stronger labor markets, while contractions in private credit are often associated with rising joblessness. This dynamic underscores the role of credit availability in 
                supporting economic activity and employment. The covid spike in unemployment is a unique exception, as you would expect, given that the rise in unemployment was caused by an exogenous shock rather than any change in credit
                creation. Therefore, it's fair to ignore this anomaly when analyzing this relationship.""")
    fig8 = plot_datasets(primary_df=unemployment, secondary_df=private_credit, primary_series="Unemployment", secondary_series="Credit Change % GDP", primary_range=[-17, -3], secondary_range=[-10, 25])
    st.plotly_chart(fig8, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 8: Change in Private Credit as % of GDP vs Unemployment</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 9. Credit Impulse vs ISM
    st.markdown("<h4 style='text-align: left;'>Private Credit Impulse vs ISM</h4>", unsafe_allow_html=True)
    st.write("""This chart displays the credit impulse — calculated as the second derivative of private credit divided by GDP — plotted against the ISM Manufacturing PMI. This comparison highlights the relationship between changes 
                in credit momentum and business cycle dynamics. The credit impulse measures the acceleration or deceleration of new credit creation over a 6 month period, making it a leading indicator of economic activity in most economic 
                conditions. The chart reveals a strong correlation between credit impulse and the ISM, indicating that shifts in credit growth often precede changes in manufacturing sentiment. This relationship underscores how the 
                pace of new credit issuance can significantly influence business conditions and economic confidence. The data is a smoothed moving average in order to remove some of the noise common to these credit impulse charts.""")
    pc = private_credit.copy()
    pc = pc[pc.index > "1991-01-01"]
    fig9 = plot_datasets(primary_df=ism_df, secondary_df=pc, primary_series="ISM", secondary_series="Credit Impulse Smoothed", primary_range=[30, 70], secondary_range=[-2.6, 2.2])
    st.plotly_chart(fig9, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 9: Credit Impulse (Smoothed) / GDP vs ISM PMI</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 10. Mortgage Credit Impulse vs ISM
    st.markdown("<h4 style='text-align: left;'>Mortgage Credit Impulse vs Housing YoY</h4>", unsafe_allow_html=True)
    st.write("""The chart below compares the mortgage credit impulse — calculated as the second derivative of mortgage credit divided by GDP — with the year-over-year percentage change in the Case-Shiller Home Price Index. This chart 
                highlights the relationship between changes in mortgage lending momentum and housing price dynamics. As mortgage credit accelerates, increased availability of funds typically fuels housing demand, leading to rising home 
                prices. Conversely, when the credit impulse slows or turns negative, housing price growth often moderates or declines. The chart demonstrates a clear correlation, indicating that shifts in mortgage credit momentum can 
                act as a leading indicator for movements in housing prices.""")
    fig10 = plot_datasets(primary_df=mortgages, secondary_df=houses, primary_series="Credit Impulse Smoothed", secondary_series="Houses YoY%", primary_range=[-2.8, 2.2], secondary_range=[-17, 25])
    st.plotly_chart(fig10, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 10: Mortgage Credit Impulse (Smoothed) / GDP vs Case-Shiller Home Price Index YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Monitoring heading
    st.markdown("<h2 style='text-align: center;'>Monitoring YoY Liquidity</h2>", unsafe_allow_html=True)
    st.write("""The following section is just for monitoring some liquidity metrics on a weekly time-frame to track the year-on-year changes in real time and plot the constant at 0% for visual purposes.""")
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 11. Global M2 Weekly YoY
    st.markdown("<h4 style='text-align: left;'>Global M2 YoY%</h4>", unsafe_allow_html=True)
    st.write("""Here we have year-over-year changes in global M2 again but with weekly data to give a more granular outlook, and a dashed horizontal line at the zero level to better see when global M2 is expanding or contracting YoY.""")
    fig11 = plot_with_constant(df=gm2, series_name="Global M2 YoY%", constant_y=0, series_range=[-20, 30])
    st.plotly_chart(fig11, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 11: Global M2 YoY% (Weekly)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 12. Fed Net Liquidity
    st.markdown("<h4 style='text-align: left;'>Fed Net Liquidity YoY%</h4>", unsafe_allow_html=True)
    st.write("""The chart below shows Fed Net Liquidity, calculated as the Fed's Balance Sheet minus the Treasury General Account (TGA) and the Reverse Repo (RRP) facility. The TGA is the account where the Federal Government holds its 
                funds at the Fed after collecting taxes or issuing bonds. When the government spends from the TGA, it releases liquidity into the economy, thereby increasing M2. In contrast, the RRP facility is a tool used by the Fed 
                to absorb excess liquidity from money markets by offering a rate of return, effectively reducing the money supply available for lending and investment.""")
    fed_liquidity = data["fed_liquidity"][["Fed Net Liquidity"]]
    fed_liquidity["Fed Liquidity YoY%"] = fed_liquidity["Fed Net Liquidity"].pct_change(periods=52) * 100
    fed_liquidity_yoy = fed_liquidity.drop(columns=["Fed Net Liquidity"]).dropna()
    fed_liquidity_yoy = fed_liquidity_yoy[fed_liquidity_yoy.index > "2011-01-01"]
    fig12 = plot_with_constant(df=fed_liquidity_yoy, series_name="Fed Liquidity YoY%", constant_y=0, series_range=[-20, 75])
    st.plotly_chart(fig12, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 12: Fed Net Liquidity YoY%</h6>", unsafe_allow_html=True)