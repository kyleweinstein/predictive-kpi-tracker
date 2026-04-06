import sqlite3
import csv
from openai import OpenAI

# 1. Set up the OpenAI Client
# Replace the string below with your actual API key
client = OpenAI(api_key="YOUR API KEY HERE")

# 2. Run the SQL Pipeline (Loading data & detecting anomalies)
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE inventory (date TEXT, sku TEXT, merchant_id TEXT, category TEXT, price REAL, inventory_qty INTEGER)''')

with open('ecommerce_inventory.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader) 
    cursor.executemany('INSERT INTO inventory VALUES (?, ?, ?, ?, ?, ?)', reader)

sql_query = '''
WITH DailyTotalInventory AS (
    SELECT date, sku, category, SUM(inventory_qty) as total_qty
    FROM inventory GROUP BY date, sku, category
),
RollingAverages AS (
    SELECT date, sku, category, total_qty as current_qty,
    AVG(total_qty) OVER (PARTITION BY sku ORDER BY date ROWS BETWEEN 7 PRECEDING AND 1 PRECEDING) as previous_7d_avg
    FROM DailyTotalInventory
)
SELECT date, sku, category, current_qty, ROUND(previous_7d_avg, 2) as previous_avg
FROM RollingAverages
WHERE current_qty < (0.5 * previous_7d_avg) AND previous_7d_avg IS NOT NULL;
'''
cursor.execute(sql_query)
anomalies = cursor.fetchall()

# 3. Format the data for the AI (Aggregating before Prompting)
if not anomalies:
    print("✅ No anomalies to report today.")
    exit()

anomaly_text = ""
for row in anomalies:
    anomaly_text += f"- On {row[0]}, {row[1]} ({row[2]}) dropped to {row[3]} units (7-day avg was {row[4]}).\n"

print("🔍 SQL Anomaly found. Sending aggregated data to OpenAI...\n")

# 4. The API Call
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are an expert Product Manager and Data Analyst for Capital One Shopping. Your job is to read database anomaly reports and write concise, urgent Slack alerts for the pricing team. Do not use emojis."},
        {"role": "user", "content": f"The database just flagged a severe inventory supply shock. Here is the SQL output:\n{anomaly_text}\nWrite a short Slack message (under 75 words) to the pricing team. Advise them on which category is at risk of price volatility and recommend pausing the predictive pricing model for that category until supply chain data stabilizes."}
    ]
)

print("🚨 AI SLACK ALERT GENERATED 🚨\n")
print(response.choices[0].message.content)