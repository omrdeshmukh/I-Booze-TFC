# TFC KPI Dashboards — Dual Excel Source (NO consolidation)

This app reads **both** of your original Excel exports directly:
- `TFC_-2_6.xlsx`  (operational/SCM/Sales/Procurement metrics)
- `FinanceReport (3).xlsx` (finance KPIs)

You can place them either in repo root **or** inside the `data/` folder,
or upload them via the Home page. The dashboards stitch KPIs at runtime.

## Run locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Deploy
Upload this folder to GitHub, add both Excel files at repo root **or** in `data/`,
then deploy on Streamlit Cloud with `streamlit_app.py` as the main file.
