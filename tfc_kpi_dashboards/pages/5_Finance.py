
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_fact, coerce_num, kpi_row, add_round_week_filters, ensure_cols

st.set_page_config(page_title="Finance Dashboard", page_icon="💹", layout="wide")
st.title("💹 Finance — KPI Bridge (Revenue → COGS → Indirect → Operating Profit → ROI)")

df = load_fact()
if df.empty:
    st.stop()

df = add_round_week_filters(df)

# Aggregates
num_cols = ["revenue","cogs","indirect_cost","operating_profit","roi_pct"]
df = coerce_num(df, [c for c in num_cols if c in df.columns])

tot_revenue = df["revenue"].sum(skipna=True) if "revenue" in df.columns else 0.0
tot_cogs = df["cogs"].sum(skipna=True) if "cogs" in df.columns else 0.0
tot_indirect = df["indirect_cost"].sum(skipna=True) if "indirect_cost" in df.columns else 0.0
tot_profit = df["operating_profit"].sum(skipna=True) if "operating_profit" in df.columns else (tot_revenue - tot_cogs - tot_indirect)
avg_roi = df["roi_pct"].mean(skipna=True) if "roi_pct" in df.columns else float('nan')

kpi_row([
    ("Revenue", tot_revenue, ""),
    ("COGS", tot_cogs, ""),
    ("Indirect Cost", tot_indirect, ""),
    ("Operating Profit", tot_profit, ""),
    ("ROI %", avg_roi if not pd.isna(avg_roi) else 0.0, "%")
])

# Trends
if "week" in df.columns:
    st.subheader("Trends Over Time")
    agg = df.groupby("week", dropna=True).agg(
        revenue=("revenue","sum") if "revenue" in df.columns else ("week","count"),
        cogs=("cogs","sum") if "cogs" in df.columns else ("week","count"),
        indirect_cost=("indirect_cost","sum") if "indirect_cost" in df.columns else ("week","count"),
        operating_profit=("operating_profit","sum") if "operating_profit" in df.columns else ("week","count"),
    ).reset_index()
    for metric in [c for c in ["revenue","cogs","indirect_cost","operating_profit"] if c in agg.columns]:
        fig = px.line(agg, x="week", y=metric, title=f"{metric.replace('_',' ').title()} by Week")
        st.plotly_chart(fig, use_container_width=True)

# Breakdown selector
st.subheader("Contribution by Dimension")
dimension = st.selectbox("Break down by", [c for c in ["customer","product","supplier","component","plant","warehouse"] if c in df.columns])
metric = st.selectbox("Metric", [c for c in ["revenue","operating_profit","cogs"] if c in df.columns])

if dimension and metric:
    grp = df.groupby(dimension, dropna=True)[metric].sum().reset_index().sort_values(by=metric, ascending=False).head(20)
    fig = px.bar(grp, x=dimension, y=metric, title=f"Top {dimension.title()} by {metric.replace('_',' ').title()}")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(grp)

# Drilldown
st.subheader("Drilldown")
cols = ensure_cols(df, ["round","week","customer","product","supplier","component","plant","warehouse",
                        "revenue","cogs","indirect_cost","operating_profit","roi_pct"])
st.dataframe(df[cols].sort_values(by=ensure_cols(df, ["round","week"]), na_position='last'))
