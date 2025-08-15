import os
import pandas as pd
import streamlit as st
from helper import load_table, plot_datasets, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read datasets
tables = ["government_spending", "quarterly_data", "economic_data", "annual_data"]
data = {name: load_table(name) for name in tables}

# Start date
govt_start_date = "1980-01-01"


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Government Spending")
    st.write("""The finances of most governments worldwide are on an unsustainable trajectory. If one analyses the data it becomes clear that a) this is a global and systemic problem, and b) the issue will likely be resolved either through a wave of sovereign 
                defaults or a combination of inflation and financial repression. Given the magnitude of this challenge, it is crucial to closely monitor government spending, its various components, and the key factors that will 
                continue to drive the growth in expenditures, particularly the issue of deteriorating demographics.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 1. Govt Debt/GDP
    st.markdown("<h4 style='text-align: left;'>Federal Government Debt-to-GDP</h4>", unsafe_allow_html=True)
    st.write("""This first chart shows the total Federal debt outstanding divided by GDP. This has been at worryingly high levels for many years now, particularly post-GFC. The highest level it had reached before then was 
                around 106% after World War II. After the financial crisis it came close to breaking that level, which it eventually did when Covid brought it to new highs of 132%. Studies and empirical research generally 
                indicate that when a country's debt-to-GDP ratio exceeds 90-100%, it becomes increasingly difficult to reverse and can significantly constrain economic growth.""")
    data["government_spending"]["Debt/GDP"] = (data["government_spending"]["Federal Govt Debt"] / data["quarterly_data"]["US GDP"]) * 100
    fig1 = basic_plot(df=data["government_spending"], series_name="Debt/GDP", start_date=govt_start_date)
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: Federal Debt as a % of GDP</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. Spending vs Receipts
    st.markdown("<h4 style='text-align: left;'>Total Federal Spending vs Total Receipts</h4>", unsafe_allow_html=True)
    st.write("""This chart shows total federal spending (annualized) charted against total federal receipts. Total receipts include tax receipts and non-tax income for the Federal Government. As can be seen in the chart, 
                the gap between receipts and spending is widening over time, and is already at unsustainable levels. Since 2023 there has been a gap of nearly $2 trillion between receipts and spending.""")
    fig2 = plot_datasets(primary_df=data["government_spending"], secondary_df=data["government_spending"], primary_series="Total Federal Spending", secondary_series="Federal Tax & Other Receipts", start_date=govt_start_date, primary_range=[450, 10000], secondary_range=[450, 10000])
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: Total Federal Spending vs Tax Receipts</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. Interest Payments / Receipts
    st.markdown("<h4 style='text-align: left;'>Interest on Debt as % of Total Receipts</h4>", unsafe_allow_html=True)
    st.write("""Figure 3 shows the interest on the federal debt divided by total receipts. With the sudden growth in debt since Covid and higher interest rates, interest on the debt has spiked to dangerous levels. 
                While it is true that this ratio was higher in the 1980s due to much higher interest rates at the time, as we saw in Figure 1 the total debt-to-GDP was much lower (around 40-60%) - which is completely 
                different to the current situation. Issuing more debt to simply pay your interest payments to existing bondholders can be justified much easier at a debt level of 50% of GDP than at 120% of GDP.""")
    data["government_spending"]["Interest/Receipts"] = (data["government_spending"]["Interest on Debt"] / data["government_spending"]["Federal Tax & Other Receipts"]) * 100
    fig3 = basic_plot(df=data["government_spending"], series_name="Interest/Receipts", start_date=govt_start_date, series_range=[10, 35])
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: Interest on Debt as % of Tax Receipts</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. Social Benefits / Receipts
    st.markdown("<h4 style='text-align: left;'>Social Transfer Payments as % of Total Receipts</h4>", unsafe_allow_html=True)
    st.write("""This series is crucial to understanding the difficult situation that the US government faces and why this trajectory is not easily reversible. The chart shows social transfer payments as a % of total receipts. 
                Social transfer payments includes: social security (pensions), Medicare, Medicaid, unemployment insurance, veterans benefits, disability benefits among others. As can be seen from the chart, these payments 
                now make up over 60% of total government receipts and is averaging higher over time. The reason this trend is likely to continue is because of the demographics problem, which is discussed in more detail 
                further down this page. As demographics continue to decline and a larger percentage of the population is retired, social security and health payments will continue to grow and are very hard to walk back. 
                Furthermore, as economic growth continues to weaken over time due to the larger debt burden, or if there is another recession, more of these payments (unemployment insurance for example) will kick in 
                automatically. We saw this already in the GFC when this series spiked from 50% to 74% and then again in Covid when it hit 130%.""")
    data["government_spending"]["Social Benefits/Receipts"] = (data["government_spending"]["Social Benefits Total"] / data["government_spending"]["Federal Tax & Other Receipts"]) * 100
    fig4 = basic_plot(df=data["government_spending"], series_name="Social Benefits/Receipts", start_date=govt_start_date, series_range=[35, 80])
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: Social Benefits as % of Tax Receipts</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 5. Defense Spending / Receipts
    st.markdown("<h4 style='text-align: left;'>Defense Spending as % of Total Receipts</h4>", unsafe_allow_html=True)
    st.write("""Defense spending often gets a lot of criticism in the media but we can see in the chart below that defense as a % of receipts has actually seen a steady decline over time. This was as high as 93% in the 1950s, 
                fell to 40% by the 1980s and is currently around 20%.""")
    data["government_spending"]["Defense/Receipts"] = (data["government_spending"]["Defense Spending"] / data["government_spending"]["Federal Tax & Other Receipts"]) * 100
    fig5 = basic_plot(df=data["government_spending"], series_name="Defense/Receipts", start_date=govt_start_date)
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: Defense Spending as % of Tax Receipts</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 6. Interest on Debt / Defense Spending
    st.markdown("<h4 style='text-align: left;'>Interest on Debt as % of Defense Spending</h4>", unsafe_allow_html=True)
    st.write("""This chart shows interest on Federal debt as a % of defense spending. It was added with specific reference to Ferguson's law, which states that any great power that spends more on debt servicing than on defense 
                risks ceasing to be a great power. This has become relevant again recently given that the chart shows this value to now be once again over 100%, which means more is being spend on interest payments than defense. 
                This did already break 100% in 1998 and fell to as low as 44% in 2010 which shows that it has been reversed in the past. However, given everything else already mentioned earlier, the current situation is far 
                more precarious.""")
    data["government_spending"]["Interest/Defense"] = (data["government_spending"]["Interest on Debt"] / data["government_spending"]["Defense Spending"]) * 100
    fig6 = basic_plot(df=data["government_spending"], series_name="Interest/Defense", start_date=govt_start_date)
    st.plotly_chart(fig6, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 6: Interest on Debt as % of Defense Spending</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Demographics heading
    st.markdown("<h2 style='text-align: center;'>Demographics</h2>", unsafe_allow_html=True)
    st.write("""As briefly mentioned earlier, demographic collapse is a major issue facing most countries across the western world. Fertility rates have been falling precipitously for several decades and are now below replacement level 
                in almost all western countries. The level to keep a population constant (known as the replacement level) is 2.1 births per woman. In the US, as will be shown below in Figure 8, it has hit 1.6 and continues to 
                fall. Every EU country is below replacement. In 2023 the EU average was 1.39, with some countries much lower than this such as Italy at 1.2 and Spain at 1.12. Some more examples are Canada at 1.26, Japan was 1.2 
                and South Korea as low as 0.72. As the baby boomer generation continues to retire and the birth rate continues to fall, a larger and larger percentage of the population will need to be supported by a 
                declining working population. This demographic collapse has effectively turned government-run pension schemes into ponzi schemes that are bankrupting every country.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 7. Labour Force Participation vs Govt Debt/GDP (Inverted)
    st.markdown("<h4 style='text-align: left;'>Labour Force Participation Rate vs Debt-to-GDP Ratio</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the labour force participation rate (percentage of the population that is working) against debt-to-gdp, which is inverted for this chart. It shows that there is a fascinating correlation 
                between these two datasets. Labour force participation has been declining steadily for several decades, which is arguably caused by the decline in demographics mentioned above. The baby boomer generation were 
                the largest generation, and as shown below the fertility rate has had a steady decline. Of course, another argument that some make is that another reason for labour force participation declining is due to the 
                decline in economic growth over time, caused by an overreaching government and inflationary monetary system. Regardless of the cause, the chart shows how lower labour force participation rates correspond to 
                a greater government debt burden.""")
    fig7 = plot_datasets(primary_df=data["economic_data"], secondary_df=data["government_spending"] * -1, primary_series="Labor Force Participation Rate", secondary_series="Debt/GDP", start_date="1990-01-01", primary_range=[59.5, 70], secondary_range=[-140, -25])
    st.plotly_chart(fig7, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 7: Labour Force Participation vs Debt/GDP (Inverted)</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 8. US Fertility Rate
    st.markdown("<h4 style='text-align: left;'>US Fertility Rate</h4>", unsafe_allow_html=True)
    st.write("""Here we have the US fertility rate mentioned earlier, which is now far below replacement level and falling steadily since 2007.""")
    fig8 = basic_plot(df=data["annual_data"], series_name="US Fertility Rate", start_date=data["annual_data"].index[0])
    st.plotly_chart(fig8, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 8: US Fertility Rate</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 9. US - % of Population 65+
    st.markdown("<h4 style='text-align: left;'>% of US Population Aged 65+</h4>", unsafe_allow_html=True)
    st.write("""A result of the issues mentioned already is that a larger percentage of the population is now above retirement age. In many countries this has risen steadily since 2010, which could be seen as when the baby 
                boomer generation started to retire. The chart below shows the percentage of US population aged 65+. It is now above 17% and rising. In Japan, this figure is a high as 30% and seems to be finding a plateau around 
                there. Japan may be a guide of how far this issue will go for other countries facing the same problem. If the US continues to follow in Japan's footsteps, is there any way to avoid a debt crisis when nearly a 
                third of the population needs to be supported by a falling working population? In the 1950s, there were about 16.5 workers per retiree, in 2000 this had fallen to 3.4, in 2022 it was 2.8 and by 2035 it is 
                projected to hit 2.1. In Japan this is even worse, in 2015 there were 1.8 working age individuals (ages 15-64) per person aged 65+, this is projected to fall to 1.3 by 2050.""")
    fig9 = basic_plot(df=data["annual_data"], series_name="US % Population 65+", start_date=data["annual_data"].index[0])
    st.plotly_chart(fig9, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 9: Percentage of Population Aged 65+</h6>", unsafe_allow_html=True)