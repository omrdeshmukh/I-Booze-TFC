
import streamlit as st
import pandas as pd
import plotly.express as px
from utils_dual import load_dual_sources, coerce_num, add_filters

st.set_page_config(page_title="Finance (Dual Excel)", page_icon="💹", layout="wide")
st.title("💹 Finance — KPI Bridge (Dual Source)")

dual = load_dual_sources()
if not dual["B"]:
    st.error("FinanceReport (3).xlsx not found. Place it in repo root or /data, or upload on Home.")
    st.stop()

framesB = []
for s, df in dual["B"].items():
    need = ["revenue","cogs","indirect_cost","operating_profit","roi_pct","round","week","customer","product","supplier","component","plant","warehouse"]
    if any([(c in df.columns) for c in need]):
        framesB.append(df)
finB = pd.concat(framesB, ignore_index=True, sort=False) if framesB else pd.DataFrame()
if finB.empty:
    st.warning("No finance-like columns found in FinanceReport (3).xlsx")
    st.stop()

finB = add_filters(finB)
finB = coerce_num(finB, ["revenue","cogs","indirect_cost","operating_profit","roi_pct"])

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Revenue", f"{finB['revenue'].sum(skipna=True):,.0f}" if "revenue" in finB.columns else "NA")
c2.metric("COGS", f"{finB['cogs'].sum(skipna=True):,.0f}" if "cogs" in finB.columns else "NA")
ind = finB["indirect_cost"].sum(skipna=True) if "indirect_cost" in finB.columns else 0.0
c3.metric("Indirect", f"{ind:,.0f}")
op = finB["operating_profit"].sum(skipna=True) if "operating_profit" in finB.columns else (finB.get("revenue",0)-finB.get("cogs",0)-ind)
c4.metric("Operating Profit", f"{op:,.0f}")
if "roi_pct" in finB.columns:
    c5.metric("ROI %", f"{finB['roi_pct'].mean(skipna=True):.2f}%")
else:
    c5.metric("ROI %", "NA")

# Trends
if "week" in finB.columns:
    st.subheader("Weekly Trends")
    agg = finB.groupby("week", dropna=True).agg(
        revenue=("revenue","sum") if "revenue" in finB.columns else ("week","count"),
        cogs=("cogs","sum") if "cogs" in finB.columns else ("week","count"),
        indirect_cost=("indirect_cost","sum") if "indirect_cost" in finB.columns else ("week","count"),
        operating_profit=("operating_profit","sum") if "operating_profit" in finB.columns else ("week","count"),
    ).reset_index()
    for metric in [m for m in ["revenue","cogs","indirect_cost","operating_profit"] if m in agg.columns]:
        fig = px.line(agg, x="week", y=metric, title=f"{metric.replace('_',' ').title()} by Week")
        st.plotly_chart(fig, use_container_width=True)

# Breakdown
st.subheader("Top Contributors")
dim = st.selectbox("Break down by", [c for c in ["customer","product","supplier","component","plant","warehouse"] if c in finB.columns])
metric = st.selectbox("Metric", [c for c in ["revenue","operating_profit","cogs"] if c in finB.columns])
grp = finB.groupby(dim, dropna=True)[metric].sum().reset_index().sort_values(metric, ascending=False).head(20)
fig = px.bar(grp, x=dim, y=metric)
st.plotly_chart(fig, use_container_width=True)
st.dataframe(grp)
