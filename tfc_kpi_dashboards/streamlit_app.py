
import streamlit as st
import pandas as pd
from utils import load_fact

st.set_page_config(page_title="TFC KPI Dashboards", page_icon="📊", layout="wide")

st.title("🍊 The Fresh Connection — Final Project Dashboards")
st.caption("Multi-page Streamlit app with KPI dashboards for Purchase, Sales, SCM, Operations, and Finance.")

st.markdown("""
**How to use**
1. Place **`fact_kpis.csv`** in the same folder as this app (or upload it below).  
2. Use the tabs in the left sidebar to navigate to each dashboard.  
3. Filters exist on each page; visuals update instantly and reflect the **exact KPIs in your guidelines**.

**Data contract (columns expected)** — the app will use what it finds:
- `round`, `week`, `date`
- `customer`, `product`, `component`, `supplier`
- `plant`, `warehouse`
- `order_qty`, `delivered_qty`, `backorder_qty`
- `revenue`, `cogs`, `indirect_cost`, `operating_profit`, `roi_pct`
- `service_level_pct`, `shelf_life_days`, `forecast`, `forecast_error_pct`
- `obsolescence_qty`, `obsolescence_value`
- `component_availability_pct`, `product_availability_pct`
- `delivery_reliability_pct`, `rejection_pct`, `component_obsolete_pct`, `raw_material_cost_pct`
- `inbound_cube_util_pct`, `outbound_cube_util_pct`, `mixing_util_pct`, `bottling_util_pct`, `plan_adherence_pct`
- optional derived: `gross_margin`, `operating_margin`, `obsolescence_rate_pct`
""")

# Optional CSV uploader (for quick testing on Streamlit Cloud)
with st.expander("⬆️ Upload a CSV (optional)"):
    up = st.file_uploader("Upload fact_kpis.csv", type=["csv"])
    if up is not None:
        df = pd.read_csv(up)
        df.to_csv("fact_kpis.csv", index=False)
        st.success("Saved `fact_kpis.csv` to app folder. You can navigate to dashboards now.")

df = load_fact()
if df.empty:
    st.info("Once `fact_kpis.csv` is present, open a dashboard page from the left sidebar.")
else:
    st.success(f"Data loaded: {len(df):,} rows, {len(df.columns)} columns.")
    st.dataframe(df.head(50))
