# Commerce EDA dashboard

Interactive Streamlit dashboard for the sales data explored in `EDA__Class_test.ipynb`.

## Run

1. Activate the project environment in PowerShell: `.\.venv\Scripts\Activate.ps1`
2. Start the app: `streamlit run app.py`
3. Upload `ecommerce_sales_data.csv` in the sidebar. If that CSV is placed beside `app.py`, the app loads it automatically.

The source CSV is not included in this project. The app expects the notebook's columns: `Year`, `Month`, `Category`, `Region`, `Units_Sold`, `Revenue`, `Profit`, `Customer_Rating`, and `Ad_Spend`.
