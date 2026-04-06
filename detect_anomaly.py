import sqlite3
import csv

# 1. Spin up an in-memory SQL database
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 2. Define our table schema
cursor.execute('''
    CREATE TABLE inventory (
        date TEXT,
        sku TEXT,
        merchant_id TEXT,
        category TEXT,
        price REAL,
        inventory_qty INTEGER
    )
''')

# 3. Load our Kaggle CSV data into the SQL database
with open('ecommerce_inventory.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader) # Skip the header row
    cursor.executemany('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)', reader)

# 4. THE SQL QUERY: Find supply shocks using CTEs and Window Functions
sql_query = '''
WITH DailyTotalInventory AS (
    -- Step A: Sum up the inventory across all merchants for each SKU, every day
    SELECT 
        date,
        sku,
        category,
        SUM(inventory_qty) as total_qty
    FROM inventory
    GROUP BY date, sku, category
),
RollingAverages AS (
    -- Step B: Calculate the 7-day rolling average for each SKU using a Window Function
    SELECT 
        date,
        sku,
        category,
        total_qty as current_qty,
        AVG(total_qty) OVER (
            PARTITION BY sku 
            ORDER BY date 
            ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING
        ) as previous_7d_avg
    FROM DailyTotalInventory
)
-- Step C: Only return rows where today's inventory dropped by more than 50%
SELECT 
    date, 
    sku, 
    category,
    current_qty, 
    ROUND(previous_7d_avg, 2) as previous_avg
FROM RollingAverages
WHERE current_qty < (0.5 * previous_7d_avg) 
  AND previous_7d_avg IS NOT NULL;
'''

print("🔍 Running SQL Anomaly Detection...")
cursor.execute(sql_query)
anomalies = cursor.fetchall()

# 5. Output the results so our AI can read them later
if anomalies:
    print("\n🚨 ANOMALIES DETECTED 🚨")
    for row in anomalies:
        print(f"Date: {row[0]} | SKU: {row[1]} | Current Inv: {row[3]} | Previous 7-Day Avg: {row[4]}")
else:
    print("\n✅ No anomalies found.")