import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from helper import load_table, plot_with_constant, basic_plot

# Set the page layout
st.set_page_config(page_title="Macro App", layout="wide")

# Read data source
banking = load_table("Banking")
quarterly_data = load_table("quarterly_data")
all_assets = banking[["Total Bank Assets"]].copy()
banking = banking.dropna()
# Loop through column to make YoY% for each
for col in banking.columns:
    banking[col + ' YoY%'] = banking[col].pct_change(periods=12) * 100
banking = banking[banking.index > "2000-01-01"]
# Delinquencies
delinquency_all = quarterly_data[["Delinquency Rate All Loans"]]
delinquency_all = delinquency_all.dropna()
delinquency_credit_card = quarterly_data[["Delinquency Rate Credit Card Loans"]]
delinquency_credit_card = delinquency_credit_card.dropna()
# Credit Cards Minimum Payment
min_payment = quarterly_data[["Credit Cards: % Accounts Making Minimum Payment"]]
min_payment = min_payment.dropna()
# Charge-Off Rates
charge_off_consumer = quarterly_data[["Charge-Off Rate Consumer Loans"]]
charge_off_consumer = charge_off_consumer.dropna()
charge_off_business = quarterly_data[["Charge-Off Rate Business Loans"]]
charge_off_business = charge_off_business.dropna()
# Net % Banks Tightening
net_tight_industrial = quarterly_data[["Net % Banks Tightening: Industrial"]]
net_tight_industrial = net_tight_industrial.dropna()
net_tight_credit_card = quarterly_data[["Net % Banks Tightening: Credit Card"]]
net_tight_credit_card = net_tight_credit_card.dropna()
# All Assets/GDP
gdp = quarterly_data[["US GDP"]]
all_assets["GDP"] = gdp["US GDP"]
all_assets = all_assets.dropna()
all_assets["Bank Assets/GDP"] = (all_assets["Total Bank Assets"] / all_assets["GDP"])*100


# Split the container into columns to manage content
col1, col2, col3 = st.columns([1, 4, 1])  # 3-column layout: center column is widest
with col2:
    # Create the title for the page
    st.title("Banking")
    st.markdown("<br>", unsafe_allow_html=True)
    # Page introduction
    st.write("""This page examines the banking sector, a critical component of the overall economy. Given that commercial banks are the primary creators of new money, tracking credit creation is essential for understanding macroeconomic dynamics. 
                In Section 3 on Liquidity, it was demonstrated that credit creation correlates strongly with the business cycle and asset prices, highlighting its significance. The first section of this page presents the year-over-year 
                changes in various types of bank credit. Following that, several charts detail underperforming loans, including delinquency rates and charge-off rates. The next section covers the net tightening of lending standards, 
                and the final part focuses on the size of the banking sector.""")
    st.markdown("<br><br>", unsafe_allow_html=True)
    

    # Credit Growth Heading
    st.markdown("<h2 style='text-align: center;'>Credit Growth</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 1. All Loans & Leases YoY
    st.markdown("<h4 style='text-align: left;'>All Loans & Leases in Bank Credit</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the year-over-year percentage change in total loans and leases held by commercial banks. An increase indicates expanding credit availability, typically reflecting economic optimism and business investment. 
                A decline suggests tightening credit conditions or reduced lending activity, often seen during downturns.""")
    fig1 = plot_with_constant(df=banking, series_name="All Loans & Leases YoY%", constant_y=0, series_range=[-10, 20])
    st.plotly_chart(fig1, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 1: All Loans & Leases in Bank Credit YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 2. Consumer Credit YoY
    st.markdown("<h4 style='text-align: left;'>Consumer Credit Owned & Securitized</h4>", unsafe_allow_html=True)
    st.write("""This one tracks the year-over-year growth rate of consumer credit, including both bank-owned and securitized loans. Positive growth indicates rising household borrowing, while negative values may signal consumer 
                deleveraging or tightened lending standards. Sharp movements can reflect securitization adjustments or debt write-offs.""")
    fig2 = plot_with_constant(df=banking, series_name="Consumer Credit YoY%", constant_y=0, series_range=[-10, 20])
    st.plotly_chart(fig2, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 2: Consumer Credit Owned & Securitized YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 3. Commercial/Industrial Credit YoY
    st.markdown("<h4 style='text-align: left;'>Commercial & Industrial Loans</h4>", unsafe_allow_html=True)
    st.write("""Figure 3 displays the change in commercial and industrial (C&I) loans, reflecting business borrowing activity. An upward trend suggests increased corporate investment and working capital demand, while a decline may 
                indicate business caution or credit tightening. This metric is sensitive to economic cycles and business confidence.""")
    fig3 = plot_with_constant(df=banking, series_name="Commercial/Industrial Loans YoY%", constant_y=0, series_range=[-25, 35])
    st.plotly_chart(fig3, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 3: Commercial & Industrial Loans YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 4. Bank Credit in Securities YoY
    st.markdown("<h4 style='text-align: left;'>Securities in Bank Credit</h4>", unsafe_allow_html=True)
    st.write("""This is the change in the value of securities held by banks, including Treasuries and mortgage-backed securities. An increase suggests banks are shifting toward safer, liquid assets, while a decline may indicate reduced 
                security holdings as banks expand direct lending. This metric often moves inversely to loan growth during economic transitions. Just as with any other type of loan, when banks buy securities they create new money supply.""")
    fig4 = plot_with_constant(df=banking, series_name="Bank Securities YoY%", constant_y=0, series_range=[-25, 35])
    st.plotly_chart(fig4, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 4: Bank Credit in Securities YoY%</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Underperforming Heading
    st.markdown("<h2 style='text-align: center;'>Underperforming Loans</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)


    # 5. Delinquency Rate All Loans
    st.markdown("<h4 style='text-align: left;'>Delinquency Rate for all Bank Loans</h4>", unsafe_allow_html=True)
    st.write("""The delinquency rate is the percentage of loans that are past due and not yet charged off. A rising delinquency rate indicates growing financial stress among borrowers, often preceding higher charge-offs. 
                Declining rates suggest improved credit quality and stronger borrower repayment capacity. This chart shows the rate for all bank loans.""")
    fig5 = basic_plot(df=delinquency_all, series_name="Delinquency Rate All Loans", series_range=[0, 10])
    st.plotly_chart(fig5, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 5: Delinquency Rate on all Bank Loans</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 6. Delinquency Rate Credit Card Loans
    st.markdown("<h4 style='text-align: left;'>Delinquency Rate for Credit Card Loans</h4>", unsafe_allow_html=True)
    st.write("""This one tracks the delinquency rate specifically for credit card debt, reflecting the financial health of consumers. An increase typically signals household financial strain or rising consumer debt burdens, 
                while a decrease indicates more stable repayment behavior. It is often a leading indicator of consumer distress.""")
    fig6 = basic_plot(df=delinquency_credit_card, series_name="Delinquency Rate Credit Card Loans", series_range=[0, 10])
    st.plotly_chart(fig6, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 6: Delinquency Rate on Credit Card Loans</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 7. Credit Cards: % Accounts Making Minimum Payment
    st.markdown("<h4 style='text-align: left;'>Credit Cards: % Accounts Making Minimum Payment</h4>", unsafe_allow_html=True)
    st.write("""This chart shows the percentage of credit card accounts that only make the minimum required payment. A higher percentage indicates potential financial pressure among consumers, as paying the minimum can signal difficulty 
                managing debt. Persistent increases can be a warning sign of future delinquencies. This data series is relatively new so the history is limited, but it will still be valuable to track.""")
    fig7 = basic_plot(df=min_payment, series_name="Credit Cards: % Accounts Making Minimum Payment", series_range=[7, 13])
    st.plotly_chart(fig7, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 7: Credit Cards: % Accounts Making Minimum Payment</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 8. Charge-Off Rate Consumer Loans
    st.markdown("<h4 style='text-align: left;'>Charge-Off Rate on Consumer Loans</h4>", unsafe_allow_html=True)
    st.write("""The charge-off rate is the percentage of loans that banks have written off as uncollectable. This chart shows the rate specifically for consumer loans. An increase indicates rising defaults, often associated with 
                economic downturns or financial instability. Decreasing charge-off rates suggest improved consumer credit health and better repayment behavior.""")
    fig8 = basic_plot(df=charge_off_consumer, series_name="Charge-Off Rate Consumer Loans", series_range=[0, 8])
    st.plotly_chart(fig8, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 8: Charge-Off Rate on Consumer Loans</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 9. Charge-Off Rate Business Loans
    st.markdown("<h4 style='text-align: left;'>Charge-Off Rate on Business Loans</h4>", unsafe_allow_html=True)
    st.write("""This chart displays the rate at which banks charge off uncollectible business loans, reflecting corporate credit risk. A rising charge-off rate signals financial distress in the business sector, possibly linked to 
                weaker earnings or economic slowdowns. Lower rates indicate stronger business solvency and credit quality.""")
    fig9 = basic_plot(df=charge_off_business, series_name="Charge-Off Rate Business Loans", series_range=[-1, 4])
    st.plotly_chart(fig9, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 9: Charge-Off Rate on Business Loans</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # Lending Standards Heading
    st.markdown("<h2 style='text-align: center;'>Lending Standards</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    
    # 10. Net % of Banks Tightening Lending Standards - Industrial
    st.markdown("<h4 style='text-align: left;'>Net % of Banks Tightening Lending Standards: Industrial Loans</h4>", unsafe_allow_html=True)
    st.write("""Here we have the net percentage of banks reporting tighter lending standards for commercial and industrial (C&I) loans. An increase indicates that banks are becoming more cautious about extending credit to businesses, 
                often due to economic uncertainty or perceived credit risk. A decrease suggests easing credit conditions, typically seen in expanding economies. This data was already shown in Section 1, when inverted it correlates with 
                the business cycle (ISM PMI).""")
    fig10 = plot_with_constant(df=net_tight_industrial, series_name="Net % Banks Tightening: Industrial", constant_y=0, series_range=[-40, 100])
    st.plotly_chart(fig10, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 10: Net % of Banks Tightening Lending Standards: Industrial Loans</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    
    # 11. Net % of Banks Tightening Lending Standards - Credit Card
    st.markdown("<h4 style='text-align: left;'>Net % of Banks Tightening Lending Standards: Credit Card Loans</h4>", unsafe_allow_html=True)
    st.write("""This is the same as above but for lending standards relating to credit card debt instead of industrial loans. A rise in this metric indicates that banks are restricting access to customers taking on more debt on their credit cards.""")
    fig11 = plot_with_constant(df=net_tight_credit_card, series_name="Net % Banks Tightening: Credit Card", constant_y=0, series_range=[-40, 100])
    st.plotly_chart(fig11, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 11: Net % of Banks Tightening Lending Standards: Credit Card Loans</h6>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    
    # Bank Sector Size Heading
    st.markdown("<h2 style='text-align: center;'>Size of Banking Sector</h2>", unsafe_allow_html=True)

    # 12. Bank Assets/GDP
    st.markdown("<h4 style='text-align: left;'> </h4>", unsafe_allow_html=True)
    st.write("""This chart shows the ratio of total bank assets to GDP, providing a measure of the relative size of the banking sector within the economy. An increasing ratio indicates that banking activity is growing faster than the 
                overall economy, which may suggest financial sector expansion or credit-driven growth. A declining ratio can indicate deleveraging or reduced banking influence on economic activity.""")
    fig12 = basic_plot(df=all_assets, series_name="Bank Assets/GDP", series_range=[45, 110])
    st.plotly_chart(fig12, use_container_width=False)
    st.markdown("<h6 style='text-align: center;'>Figure 12: Total Bank Assets as % of GDP</h6>", unsafe_allow_html=True)