import streamlit as st
import sqlite3
import pandas as pd
import csv

# 1. Page Configuration
st.set_page_config(page_title="DealFinder KPIs", layout="wide")
st.title("📊 DealFinder: KPI Dashboard")
st.markdown("Real-time monitoring of market volatility and merchant health.")

# 2. Spin up the database and load Kaggle data
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE inventory (date TEXT, sku TEXT, merchant_id TEXT, category TEXT, price REAL, inventory_qty INTEGER)''')

with open('ecommerce_inventory.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader) 
    cursor.executemany('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)', reader)

# 3. KPI 1: Competitor Price Spread (Line Chart)
st.subheader("1. Competitor Price Spread (Volatility)")
st.markdown("Tracks the maximum price difference for the same item across different merchants.")

query1 = '''
    SELECT date, sku, MAX(price) as high_price, MIN(price) as low_price, ROUND(MAX(price) - MIN(price), 2) as price_spread
    FROM inventory
    GROUP BY date, sku
    ORDER BY date ASC
'''
df_spread = pd.read_sql_query(query1, conn)

# Filter for our volatile laptop to draw a chart
lapt_data = df_spread[df_spread['sku'] == 'LAPT-X1'].set_index('date')
st.line_chart(lapt_data['price_spread'])

with st.expander("View Raw Spread Data"):
    st.dataframe(df_spread.sort_values(by="date", ascending=False).head(10))

# 4. Two-Column Layout for the remaining KPIs
col1, col2 = st.columns(2)

with col1:
    # KPI 2: Stock-Out Alerts (Warning Table)
    st.subheader("2. Merchant Stock-Out Alerts")
    query2 = '''SELECT date, merchant_id, sku FROM inventory WHERE inventory_qty = 0 ORDER BY date DESC'''
    df_stockout = pd.read_sql_query(query2, conn)
    
    if not df_stockout.empty:
        st.error(f"🚨 {len(df_stockout)} stock-out events detected!")
        st.dataframe(df_stockout)
    else:
        st.success("✅ All merchants are fully stocked.")

with col2:
    # KPI 3: Category Average Pricing (Bar Chart)
    st.subheader("3. Category Average Pricing")
    query3 = '''SELECT category, ROUND(AVG(price), 2) as avg_category_price FROM inventory GROUP BY category'''
    df_cat = pd.read_sql_query(query3, conn)
    
    st.bar_chart(df_cat.set_index('category'))