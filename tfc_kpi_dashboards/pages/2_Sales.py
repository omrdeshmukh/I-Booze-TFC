
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_fact, coerce_num, kpi_row, add_round_week_filters, add_dimension_filter, ensure_cols

st.set_page_config(page_title="Sales Dashboard", page_icon="🧾", layout="wide")
st.title("🧾 Sales — Service Level & Shelf Life → Customer ROI & Revenue")

df = load_fact()
if df.empty:
    st.stop()

df = add_round_week_filters(df)

# Filters
customers = add_dimension_filter(df, "Customer(s)", "customer")
products = add_dimension_filter(df, "Product(s)", "product")

mask = pd.Series([True]*len(df))
if customers: mask &= df.get("customer", pd.Series("")).isin(customers)
if products: mask &= df.get("product", pd.Series("")).isin(products)
df = df[mask]

# KPI cards
num_cols = ["service_level_pct","shelf_life_days","forecast_error_pct","obsolescence_value",
            "revenue","operating_profit","roi_pct"]
df = coerce_num(df, [c for c in num_cols if c in df.columns])

kpis = []
if "service_level_pct" in df.columns:
    kpis.append(("Service Level", df["service_level_pct"].mean(skipna=True), "%"))
if "shelf_life_days" in df.columns:
    kpis.append(("Shelf Life (days)", df["shelf_life_days"].mean(skipna=True), ""))
if "forecast_error_pct" in df.columns:
    kpis.append(("Forecast Error", df["forecast_error_pct"].mean(skipna=True), "%"))
if "obsolescence_value" in df.columns:
    kpis.append(("Obsolescence Value", df["obsolescence_value"].sum(skipna=True), ""))
if "operating_profit" in df.columns:
    kpis.append(("Operating Profit", df["operating_profit"].sum(skipna=True), ""))
if "roi_pct" in df.columns:
    kpis.append(("ROI", df["roi_pct"].mean(skipna=True), "%"))
if kpis: kpi_row(kpis)

# Customer prioritization table
group_cols = ensure_cols(df, ["customer"])
score_cols = ensure_cols(df, ["revenue","operating_profit","roi_pct","service_level_pct","shelf_life_days","forecast_error_pct","obsolescence_value"])
if group_cols and score_cols:
    prio = df[group_cols + score_cols].groupby(group_cols, dropna=True).agg(
        {"revenue":"sum","operating_profit":"sum","roi_pct":"mean",
         "service_level_pct":"mean","shelf_life_days":"mean","forecast_error_pct":"mean",
         "obsolescence_value":"sum"}).reset_index()
    st.subheader("Customer Prioritization")
    st.dataframe(prio.sort_values(by="operating_profit", ascending=False))

# Scatter: Service Level vs ROI
if "service_level_pct" in df.columns and "roi_pct" in df.columns and "revenue" in df.columns and "customer" in df.columns:
    st.subheader("Service Level vs Customer ROI (bubble size = Revenue)")
    bubble = df.groupby("customer", dropna=True).agg(
        service_level_pct=("service_level_pct","mean"),
        roi_pct=("roi_pct","mean"),
        revenue=("revenue","sum")
    ).reset_index()
    fig = px.scatter(bubble, x="service_level_pct", y="roi_pct", size="revenue", hover_name="customer",
                     title="Service Level vs ROI by Customer")
    st.plotly_chart(fig, use_container_width=True)

# Product lens
if "product" in df.columns and "shelf_life_days" in df.columns:
    st.subheader("Product Shelf Life and Service Level")
    prod = df.groupby("product", dropna=True).agg(
        shelf_life_days=("shelf_life_days","mean"),
        service_level_pct=("service_level_pct","mean"),
        operating_profit=("operating_profit","sum")
    ).reset_index()
    fig = px.scatter(prod, x="shelf_life_days", y="service_level_pct", size="operating_profit", hover_name="product",
                     title="Shelf Life vs Service Level by Product (size = Operating Profit)")
    st.plotly_chart(fig, use_container_width=True)

# Drilldown table
st.subheader("Drilldown")
cols = ensure_cols(df, ["round","week","customer","product","revenue","operating_profit","roi_pct",
                        "service_level_pct","shelf_life_days","forecast_error_pct","obsolescence_value"])
st.dataframe(df[cols].sort_values(by=ensure_cols(df, ["round","week"]), na_position='last'))
