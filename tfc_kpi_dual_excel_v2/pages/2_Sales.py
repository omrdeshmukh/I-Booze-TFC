
import streamlit as st, pandas as pd, plotly.express as px
from utils_dual_v2 import load_sources, coerce_num, add_time_filters

st.set_page_config(page_title="Sales", page_icon="🧾", layout="wide")
st.title("🧾 Sales — Service Level, Shelf Life, Forecast Error, Obsolescence → Profit/ROI")

data = load_sources(None, None, st.session_state.get("ops_up"), st.session_state.get("fin_up"))
sA = pd.concat([df for df in data["OPS"].values()], ignore_index=True, sort=False) if data["OPS"] else pd.DataFrame()
fB = pd.concat([df for df in data["FIN"].values()], ignore_index=True, sort=False) if data["FIN"] else pd.DataFrame()

if not sA.empty: sA = add_time_filters(sA)
if not fB.empty: fB = add_time_filters(fB)

customers = sorted(pd.concat([sA.get("customer", pd.Series(dtype=str)), fB.get("customer", pd.Series(dtype=str))], ignore_index=True).dropna().unique().tolist())
products = sorted(sA.get("product", pd.Series(dtype=str)).dropna().unique().tolist())
sel_c = st.multiselect("Customer(s)", customers, default=customers)
sel_p = st.multiselect("Product(s)", products, default=products)

def filt(df):
    if df.empty: return df
    m = pd.Series(True, index=df.index)
    if "customer" in df.columns and sel_c: m &= df["customer"].isin(sel_c)
    if "product" in df.columns and sel_p: m &= df["product"].isin(sel_p)
    return df[m]

sA, fB = filt(sA), filt(fB)

sA = coerce_num(sA, ["service_level_pct","shelf_life_days","forecast_error_pct","obsolescence_value"])
fB = coerce_num(fB, ["revenue","operating_profit","roi_pct"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
if "service_level_pct" in sA.columns: c1.metric("Service Level %", f"{sA['service_level_pct'].mean():.2f}%")
if "shelf_life_days" in sA.columns: c2.metric("Shelf Life (days)", f"{sA['shelf_life_days'].mean():.1f}")
if "forecast_error_pct" in sA.columns: c3.metric("Forecast Error %", f"{sA['forecast_error_pct'].mean():.2f}%")
if "obsolescence_value" in sA.columns: c4.metric("Obsolescence Value", f"{sA['obsolescence_value'].sum():,.0f}")
if "operating_profit" in fB.columns: c5.metric("Operating Profit", f"{fB['operating_profit'].sum():,.0f}")
if "roi_pct" in fB.columns: c6.metric("ROI %", f"{fB['roi_pct'].mean():.2f}%")

# KPI charts
left,right = st.columns(2)
if "customer" in sA.columns and "service_level_pct" in sA.columns:
    with left:
        fig = px.box(sA, x="customer", y="service_level_pct", points="all", title="Service Level % by Customer")
        st.plotly_chart(fig, use_container_width=True)
if "product" in sA.columns and "shelf_life_days" in sA.columns:
    with right:
        fig = px.box(sA, x="product", y="shelf_life_days", points="all", title="Shelf Life (days) by Product")
        st.plotly_chart(fig, use_container_width=True)

left,right = st.columns(2)
if "customer" in sA.columns and "forecast_error_pct" in sA.columns:
    with left:
        fe = sA.groupby("customer")["forecast_error_pct"].mean().reset_index()
        fig = px.bar(fe, x="customer", y="forecast_error_pct", title="Avg Forecast Error % by Customer")
        st.plotly_chart(fig, use_container_width=True)
if "customer" in sA.columns and "obsolescence_value" in sA.columns:
    with right:
        ob = sA.groupby("customer")["obsolescence_value"].sum().reset_index()
        fig = px.bar(ob, x="customer", y="obsolescence_value", title="Obsolescence Value by Customer")
        st.plotly_chart(fig, use_container_width=True)

if "customer" in fB.columns and "operating_profit" in fB.columns:
    fig = px.bar(fB.groupby("customer")["operating_profit"].sum().reset_index(), x="customer", y="operating_profit", title="Operating Profit by Customer")
    st.plotly_chart(fig, use_container_width=True)
if "service_level_pct" in sA.columns and "roi_pct" in fB.columns and "customer" in fB.columns:
    a = sA.groupby("customer")["service_level_pct"].mean()
    b = fB.groupby("customer")["roi_pct"].mean()
    ab = pd.concat([a,b], axis=1).dropna().reset_index()
    fig = px.scatter(ab, x="service_level_pct", y="roi_pct", hover_name="customer", title="Service Level vs ROI (Customer)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldown")
if not sA.empty: st.dataframe(sA)
if not fB.empty: st.dataframe(fB)
