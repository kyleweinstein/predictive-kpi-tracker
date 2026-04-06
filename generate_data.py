import csv
import random
from datetime import datetime, timedelta

# Define our mock product catalog
products = [
    {"sku": "LAPT-X1", "category": "Electronics", "base_price": 899.99, "base_inv": 150},
    {"sku": "COFF-MUG", "category": "Home Goods", "base_price": 14.99, "base_inv": 500},
    {"sku": "HEAD-PRO", "category": "Electronics", "base_price": 199.50, "base_inv": 200}
]

merchants = ["Target", "BestBuy", "Amazon"]
start_date = datetime.now() - timedelta(days=30)

# Create and open the CSV file
with open('ecommerce_inventory.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the Schema Headers
    writer.writerow(['date', 'sku', 'merchant_id', 'category', 'price', 'inventory_qty'])

    # Generate 30 days of data
    for day_offset in range(30):
        current_date = (start_date + timedelta(days=day_offset)).strftime('%Y-%m-%d')
        
        for product in products:
            for merchant in merchants:
                # Add slight daily random fluctuations to price and inventory
                daily_price = round(product["base_price"] * random.uniform(0.95, 1.05), 2)
                daily_inv = int(product["base_inv"] * random.uniform(0.8, 1.1))

                # THE ANOMALY: A sudden supply shock hits laptops on Day 26
                if day_offset >= 26 and product["sku"] == "LAPT-X1":
                    daily_inv = int(daily_inv * 0.1) # Inventory plummets by 90%
                    daily_price = round(daily_price * 1.2, 2) # Price surges by 20% due to shortage

                # Write the row to the CSV
                writer.writerow([
                    current_date, 
                    product["sku"], 
                    merchant, 
                    product["category"], 
                    daily_price, 
                    daily_inv
                ])

print("✅ Success! Generated ecommerce_inventory.csv with 30 days of tracking data.")