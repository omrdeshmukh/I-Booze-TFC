
import streamlit as st
import pandas as pd
import plotly.express as px
from utils_dual import load_dual_sources, coerce_num, add_filters

st.set_page_config(page_title="Sales (Dual Excel)", page_icon="🧾", layout="wide")
st.title("🧾 Sales — Service Level & Shelf Life → Customer ROI & Revenue (Dual Source)")

dual = load_dual_sources()
if not dual["A"] and not dual["B"]:
    st.stop()

# Pull Sales KPIs from A, finance from B
framesA = []
for s, df in dual["A"].items():
    need = ["customer","product","service_level_pct","shelf_life_days","forecast_error_pct","obsolescence_value","round","week"]
    if any([(c in df.columns) for c in need]):
        framesA.append(df)
salesA = pd.concat(framesA, ignore_index=True, sort=False) if framesA else pd.DataFrame()

framesB = []
for s, df in dual["B"].items():
    need = ["customer","revenue","operating_profit","roi_pct","round","week"]
    if any([(c in df.columns) for c in need]):
        framesB.append(df)
finB = pd.concat(framesB, ignore_index=True, sort=False) if framesB else pd.DataFrame()

if not salesA.empty:
    salesA = add_filters(salesA)
if not finB.empty:
    finB = add_filters(finB)

# Customer & Product filters
custs = sorted(pd.concat([salesA.get("customer", pd.Series(dtype=str)),
                          finB.get("customer", pd.Series(dtype=str))], ignore_index=True).dropna().unique().tolist())
prods = sorted(salesA.get("product", pd.Series(dtype=str)).dropna().unique().tolist())

sel_cust = st.multiselect("Customer(s)", custs, default=custs)
sel_prod = st.multiselect("Product(s)", prods, default=prods)

def filt(df):
    if df.empty: return df
    m = pd.Series(True, index=df.index)
    if "customer" in df.columns and sel_cust:
        m &= df["customer"].isin(sel_cust)
    if "product" in df.columns and sel_prod:
        m &= df["product"].isin(sel_prod)
    return df[m]

salesA = filt(salesA)
finB = filt(finB)

# KPI tiles
salesA = coerce_num(salesA, ["service_level_pct","shelf_life_days","forecast_error_pct","obsolescence_value"])
finB = coerce_num(finB, ["revenue","operating_profit","roi_pct"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
if "service_level_pct" in salesA.columns:
    c1.metric("Service Level %", f"{salesA['service_level_pct'].mean():.2f}%")
if "shelf_life_days" in salesA.columns:
    c2.metric("Shelf Life (days)", f"{salesA['shelf_life_days'].mean():.1f}")
if "forecast_error_pct" in salesA.columns:
    c3.metric("Forecast Error %", f"{salesA['forecast_error_pct'].mean():.2f}%")
if "obsolescence_value" in salesA.columns:
    c4.metric("Obsolescence Value", f"{salesA['obsolescence_value'].sum():,.0f}")
if "operating_profit" in finB.columns:
    c5.metric("Operating Profit", f"{finB['operating_profit'].sum():,.0f}")
if "roi_pct" in finB.columns:
    c6.metric("ROI %", f"{finB['roi_pct'].mean():.2f}%")

# Graphs
if "customer" in finB.columns and "operating_profit" in finB.columns:
    st.subheader("Profit by Customer")
    grp = finB.groupby("customer", dropna=True)["operating_profit"].sum().reset_index()
    fig = px.bar(grp, x="customer", y="operating_profit")
    st.plotly_chart(fig, use_container_width=True)

if "service_level_pct" in salesA.columns and "roi_pct" in finB.columns and "customer" in finB.columns:
    st.subheader("Service Level vs ROI (by Customer)")
    a = salesA.groupby("customer", dropna=True)["service_level_pct"].mean()
    b = finB.groupby("customer", dropna=True)["roi_pct"].mean()
    ab = pd.concat([a,b], axis=1).dropna().reset_index()
    fig = px.scatter(ab, x="service_level_pct", y="roi_pct", hover_name="customer")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldowns")
if not salesA.empty:
    st.markdown("**Sales KPIs (from TFC_-2_6.xlsx)**")
    st.dataframe(salesA)
if not finB.empty:
    st.markdown("**Finance KPIs (from FinanceReport (3).xlsx)**")
    st.dataframe(finB)
