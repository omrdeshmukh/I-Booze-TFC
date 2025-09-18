
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_fact, coerce_num, kpi_row, add_round_week_filters, add_dimension_filter, ensure_cols

st.set_page_config(page_title="SCM Dashboard", page_icon="🔗", layout="wide")
st.title("🔗 SCM — Availability → Revenue & ROI")

df = load_fact()
if df.empty:
    st.stop()

df = add_round_week_filters(df)

# Filters
components = add_dimension_filter(df, "Component(s)", "component")
products = add_dimension_filter(df, "Product(s)", "product")

mask = pd.Series([True]*len(df))
if components: mask &= df.get("component", pd.Series("")).isin(components)
if products: mask &= df.get("product", pd.Series("")).isin(products)
df = df[mask]

# KPIs
num_cols = ["component_availability_pct","product_availability_pct","revenue","roi_pct","backorder_qty"]
df = coerce_num(df, [c for c in num_cols if c in df.columns])

kpis = []
if "product_availability_pct" in df.columns:
    kpis.append(("Product Availability", df["product_availability_pct"].mean(skipna=True), "%"))
if "component_availability_pct" in df.columns:
    kpis.append(("Component Availability", df["component_availability_pct"].mean(skipna=True), "%"))
if "revenue" in df.columns:
    kpis.append(("Revenue", df["revenue"].sum(skipna=True), ""))
if "roi_pct" in df.columns:
    kpis.append(("ROI", df["roi_pct"].mean(skipna=True), "%"))
if kpis: kpi_row(kpis)

# Heatmap by Product over time
if "product" in df.columns and "product_availability_pct" in df.columns:
    st.subheader("Product Availability Heatmap")
    heat = df.groupby(["week","product"], dropna=True)["product_availability_pct"].mean().reset_index()
    if not heat.empty:
        fig = px.density_heatmap(heat, x="week", y="product", z="product_availability_pct",
                                 title="Product Availability by Week & Product", histfunc="avg")
        st.plotly_chart(fig, use_container_width=True)

# Impact chart: Availability vs Revenue
if "product_availability_pct" in df.columns and "revenue" in df.columns and "product" in df.columns:
    st.subheader("Availability vs Revenue")
    impact = df.groupby("product", dropna=True).agg(
        product_availability_pct=("product_availability_pct","mean"),
        revenue=("revenue","sum")
    ).reset_index()
    fig = px.scatter(impact, x="product_availability_pct", y="revenue", hover_name="product",
                     title="Product Availability vs Revenue")
    st.plotly_chart(fig, use_container_width=True)

# Bottlenecks by Component
if "component" in df.columns and "component_availability_pct" in df.columns:
    st.subheader("Component Bottlenecks")
    comp = df.groupby("component", dropna=True)["component_availability_pct"].mean().reset_index()
    comp = comp.sort_values(by="component_availability_pct")
    fig = px.bar(comp, x="component", y="component_availability_pct", title="Lowest Availability Components")
    st.plotly_chart(fig, use_container_width=True)

# Drilldown
st.subheader("Drilldown")
cols = ensure_cols(df, ["round","week","component","product","product_availability_pct","component_availability_pct",
                        "revenue","roi_pct","backorder_qty"])
st.dataframe(df[cols].sort_values(by=ensure_cols(df, ["round","week"]), na_position='last'))
