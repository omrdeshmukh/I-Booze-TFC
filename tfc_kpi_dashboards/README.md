# TFC KPI Dashboards (Streamlit)

Multi-page Streamlit app that renders the final project dashboards **strictly per KPI requirements** with separate tabs for each role: Purchase, Sales, SCM, Operations, Finance.

## Folder Layout
```
.
├─ streamlit_app.py        # Home page + CSV uploader helper
├─ utils.py                # Data loader, shared filters, KPI helpers
├─ pages/
│  ├─ 1_Purchase.py
│  ├─ 2_Sales.py
│  ├─ 3_SCM.py
│  ├─ 4_Operations.py
│  └─ 5_Finance.py
├─ fact_kpis.csv           # Your consolidated dataset (place here)
├─ requirements.txt
└─ README.md
```

> ✅ **Operating Profit = Net Profit**, ✅ **COGS = Cost of goods sold** — already reflected in visuals & labels.

## Local Run
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy via GitHub → Streamlit Cloud
1. Create a new **public** GitHub repo, e.g. `tfc-kpi-dashboards`.
2. Upload all files in this folder to the repo (including `requirements.txt`).  
   - Put your **`fact_kpis.csv`** at repo root (same level as `streamlit_app.py`).  
3. Go to [share.streamlit.io](https://share.streamlit.io), connect your GitHub, and select the repo.
4. Set **Main file path** to `streamlit_app.py`.  
5. Click **Deploy**. After it boots, the **Home** page lets you optionally upload a CSV if needed.

## Data Contract
The app will use what it finds in `fact_kpis.csv`. Expected columns (case-insensitive):
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

## Notes
- Each page has its own filters (Round/Week + dimension pickers).
- All charts are **Plotly** for interactivity; tables are fully sortable and filterable in the UI.
- If `roi_pct` is missing in your data, the dashboard still works (ROI tiles will hide if column missing).
- Swap in a new `fact_kpis.csv` at any time; the app reloads automatically.
