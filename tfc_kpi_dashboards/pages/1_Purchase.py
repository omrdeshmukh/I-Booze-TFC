
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_fact, coerce_num, kpi_row, add_round_week_filters, add_dimension_filter, ensure_cols

st.set_page_config(page_title="Purchase Dashboard", page_icon="🛒", layout="wide")
st.title("🛒 Purchase — Supplier Performance → ROI & Financial Impact")

df = load_fact()
if df.empty:
    st.stop()

df = add_round_week_filters(df)

# Filters
suppliers = add_dimension_filter(df, "Supplier(s)", "supplier")
components = add_dimension_filter(df, "Component(s)", "component")

mask = pd.Series([True]*len(df))
if suppliers: mask &= df.get("supplier", pd.Series("")).isin(suppliers)
if components: mask &= df.get("component", pd.Series("")).isin(components)
df = df[mask]

# KPI cards
num_cols = ["delivery_reliability_pct","rejection_pct","component_obsolete_pct","raw_material_cost_pct",
            "revenue","cogs","indirect_cost","operating_profit","roi_pct"]
df = coerce_num(df, [c for c in num_cols if c in df.columns])

kpis = []
if "delivery_reliability_pct" in df.columns:
    kpis.append(("Delivery Reliability", df["delivery_reliability_pct"].mean(skipna=True), "%"))
if "rejection_pct" in df.columns:
    kpis.append(("Rejection Rate", df["rejection_pct"].mean(skipna=True), "%"))
if "component_obsolete_pct" in df.columns:
    kpis.append(("Component Obsolete", df["component_obsolete_pct"].mean(skipna=True), "%"))
if "raw_material_cost_pct" in df.columns:
    kpis.append(("RM Cost %", df["raw_material_cost_pct"].mean(skipna=True), "%"))
if "operating_profit" in df.columns:
    kpis.append(("Operating Profit", df["operating_profit"].sum(skipna=True), ""))
if "roi_pct" in df.columns:
    kpis.append(("ROI", df["roi_pct"].mean(skipna=True), "%"))
if kpis: kpi_row(kpis)

# Supplier scorecard
group_cols = ensure_cols(df, ["supplier"])
score_cols = ensure_cols(df, ["delivery_reliability_pct","rejection_pct","component_obsolete_pct","raw_material_cost_pct",
                              "revenue","cogs","operating_profit","roi_pct"])
if group_cols and score_cols:
    score = df[group_cols + score_cols].groupby(group_cols, dropna=True).mean(numeric_only=True).reset_index()
    st.subheader("Supplier Scorecard (averages)")
    st.dataframe(score)

# Impact charts
left, right = st.columns(2)
if "supplier" in df.columns and "operating_profit" in df.columns:
    with left:
        fig = px.bar(df.groupby("supplier", dropna=True)["operating_profit"].sum().reset_index(),
                     x="supplier", y="operating_profit", title="Operating Profit by Supplier")
        st.plotly_chart(fig, use_container_width=True)
if "supplier" in df.columns and "roi_pct" in df.columns:
    with right:
        fig = px.box(df.dropna(subset=["roi_pct"]), x="supplier", y="roi_pct", points="all",
                     title="ROI % by Supplier (distribution)")
        st.plotly_chart(fig, use_container_width=True)

# Drilldown table
st.subheader("Drilldown")
cols = ensure_cols(df, ["round","week","supplier","component","revenue","cogs","indirect_cost","operating_profit","roi_pct",
                        "delivery_reliability_pct","rejection_pct","component_obsolete_pct","raw_material_cost_pct"])
st.dataframe(df[cols].sort_values(by=ensure_cols(df, ["round","week"]), na_position='last'))
