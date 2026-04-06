import sqlite3
import csv

# 1. Spin up the database and load our Kaggle data
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE inventory (
        date TEXT, sku TEXT, merchant_id TEXT, category TEXT, price REAL, inventory_qty INTEGER
    )
''')

with open('ecommerce_inventory.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader) 
    cursor.executemany('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)', reader)

print("\n📊 CAPITAL ONE SHOPPING: DAILY KPI DASHBOARD 📊\n")

# ---------------------------------------------------------
# KPI 1: COMPETITOR PRICE SPREAD (Volatility)
# PM Value: If the spread is huge, our extension provides massive value to the user.
# ---------------------------------------------------------
print("--- KPI 1: HIGHEST PRICE SPREAD BY SKU ---")
cursor.execute('''
    SELECT 
        date, 
        sku, 
        MAX(price) as highest_price, 
        MIN(price) as lowest_price, 
        ROUND(MAX(price) - MIN(price), 2) as price_spread
    FROM inventory
    GROUP BY date, sku
    ORDER BY price_spread DESC 
    LIMIT 5;
''')
for row in cursor.fetchall():
    print(f"Date: {row[0]} | SKU: {row[1]} | Spread: ${row[4]} (High: ${row[2]}, Low: ${row[3]})")

print("\n")

# ---------------------------------------------------------
# KPI 2: CRITICAL MERCHANT STOCK-OUTS
# PM Value: If a merchant has 0 inventory, we must route users to a different merchant.
# ---------------------------------------------------------
print("--- KPI 2: MERCHANT ZERO-INVENTORY ALERTS ---")
cursor.execute('''
    SELECT 
        date, 
        merchant_id, 
        sku 
    FROM inventory 
    WHERE inventory_qty = 0 
    ORDER BY date DESC 
    LIMIT 5;
''')
for row in cursor.fetchall():
    print(f"Date: {row[0]} | Merchant: {row[1]} | SKU: {row[2]} is OUT OF STOCK.")

print("\n")

# ---------------------------------------------------------
# KPI 3: CATEGORY AVERAGE PRICING
# PM Value: Tracking macroeconomic inflation or deflation across product sectors.
# ---------------------------------------------------------
print("--- KPI 3: AVERAGE PRICE BY CATEGORY ---")
cursor.execute('''
    SELECT 
        category, 
        ROUND(AVG(price), 2) as avg_category_price
    FROM inventory
    GROUP BY category
    ORDER BY avg_category_price DESC;
''')
for row in cursor.fetchall():
    print(f"Category: {row[0]} | Average Price: ${row[1]}")

print("\n✅ Dashboard Generation Complete.")