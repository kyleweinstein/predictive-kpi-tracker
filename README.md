# Predictive KPI Tracker: E-Commerce Supply Shock Detection

## Project Goal
This project is a proof-of-concept backend data pipeline and AI alert system. It is designed to automatically detect structural supply chain anomalies (data drift) and use an LLM to alert the pricing strategy team before consumer-facing predictive pricing models fail.

## The Business Value (Product Strategy)
In e-commerce, predictive pricing algorithms anticipate standard seasonal price drops. However, when a sudden geopolitical event or supply shock occurs, inventory plummets and wholesale replacement costs surge. If the algorithm relies purely on lagging indicators or historical seasonality, it will push inaccurate "price drop" alerts to users, resulting in poor UX and lost revenue.

This pipeline solves that by monitoring the **structural inputs** (daily merchant inventory) rather than the model's outputs:
1. **Mitigates Data Drift:** Catches sudden anomalies using rolling statistical thresholds.
2. **Cost-Efficient AI:** Uses an "Aggregate Before Prompting" architecture. Instead of sending millions of database rows to an LLM, SQL does the heavy math, and the AI only processes the flagged anomalies.
3. **Actionable Automation:** Translates raw database dumps into urgent, human-readable Slack alerts so the team can pause broken pricing models immediately.

## The Tech Stack
* **Language:** Python
* **Data Processing:** SQL (SQLite3)
* **AI Integration:** OpenAI API (`gpt-4o-mini`)
* **Concepts Demonstrated:** RAG (Retrieval-Augmented Generation), SQL Window Functions, Common Table Expressions (CTEs), API Integration, Concept Drift mitigation.

## Architecture & Pipeline Flow
1. **The Data Foundation (`ecommerce_inventory.csv`):** Simulates a massive daily snapshot of product prices and inventory across multiple merchants (e.g., Target, BestBuy). Includes a programmed "supply shock" event for testing.
2. **The SQL Detector:** Uses a CTE to aggregate total daily inventory across all merchants for a single SKU. It then applies a **Window Function** to calculate a 7-day rolling average, flagging any product where current inventory drops more than 50% below its historical average.
3. **The Python Orchestrator:** Fetches the flagged anomalies and formats them into a strictly controlled System/User prompt.
4. **The AI Alert:** The LLM acts as a Product Analyst, reading the SQL data and outputting a concise, formatted Slack message recommending an immediate pause on the predictive model for the affected category.

## How to Run Locally
**Prerequisites:**
* Python 3.x installed
* An active OpenAI Developer API Key

**Setup:**
1. Clone the repository: `git clone https://github.com/YourUsername/predictive-kpi-tracker.git`
2. Navigate to the directory: `cd predictive-kpi-tracker`
3. Install the OpenAI library: `pip install openai`
4. Open `generate_alert.py` and replace `"YOUR_API_KEY"` with your OpenAI key.
5. Run the pipeline: `python generate_alert.py`

*(Note: A mocked AI response option is available in the code comments for testing without API credits).*

## Edge Cases & Troubleshooting
* **API Rate Limits / Downtime:** If the LLM API is unreachable or rate-limited (e.g., Error 429), the system will fallback to a localized text alert containing the raw SQL output. This ensures the pricing team still gets the critical data while DevOps investigates the API connection.
* **Corrupted Data Ingestion:** If the upstream CSV feed contains null values or strings in the `inventory_qty` column, the SQLite `CREATE TABLE` schema enforces strict typing. The pipeline will isolate the corrupted rows before they can pollute the 7-day rolling average calculation.
* **Mitigating Alert Fatigue:** The anomaly trigger deliberately tracks *Inventory Quantity* (structural data) rather than *Price Spread* (market noise). This prevents the AI from spamming the team every time a competitor runs a flash sale.