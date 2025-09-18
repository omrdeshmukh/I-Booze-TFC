
import streamlit as st, pandas as pd, plotly.express as px
from utils_dual_v2 import load_sources, coerce_num, add_time_filters

st.set_page_config(page_title="SCM", page_icon="🔗", layout="wide")
st.title("🔗 SCM — Availability KPIs & Revenue/ROI Impact")

data = load_sources(None, None, st.session_state.get("ops_up"), st.session_state.get("fin_up"))
scmA = pd.concat([df for df in data["OPS"].values()], ignore_index=True, sort=False) if data["OPS"] else pd.DataFrame()
finB = pd.concat([df for df in data["FIN"].values()], ignore_index=True, sort=False) if data["FIN"] else pd.DataFrame()

if not scmA.empty: scmA = add_time_filters(scmA)
if not finB.empty: finB = add_time_filters(finB)

scmA = coerce_num(scmA, ["product_availability_pct","component_availability_pct"])
finB = coerce_num(finB, ["revenue","roi_pct"])

products = sorted(scmA.get("product", pd.Series(dtype=str)).dropna().unique().tolist())
components = sorted(scmA.get("component", pd.Series(dtype=str)).dropna().unique().tolist())
sel_p = st.multiselect("Product(s)", products, default=products)
sel_c = st.multiselect("Component(s)", components, default=components)

def filt(df):
    if df.empty: return df
    m = pd.Series(True, index=df.index)
    if "product" in df.columns and sel_p: m &= df["product"].isin(sel_p)
    if "component" in df.columns and sel_c: m &= df["component"].isin(sel_c)
    return df[m]

scmA, finB = filt(scmA), filt(finB)

c1,c2,c3 = st.columns(3)
if "product_availability_pct" in scmA.columns: c1.metric("Product Availability %", f"{scmA['product_availability_pct'].mean():.2f}%")
if "component_availability_pct" in scmA.columns: c2.metric("Component Availability %", f"{scmA['component_availability_pct'].mean():.2f}%")
if "revenue" in finB.columns: c3.metric("Revenue", f"{finB['revenue'].sum():,.0f}")

if "product" in scmA.columns and "product_availability_pct" in scmA.columns:
    heat = scmA.groupby(["week","product"])["product_availability_pct"].mean().reset_index()
    if not heat.empty:
        fig = px.density_heatmap(heat, x="week", y="product", z="product_availability_pct", title="Product Availability Heatmap")
        st.plotly_chart(fig, use_container_width=True)

if "component" in scmA.columns and "component_availability_pct" in scmA.columns:
    comp = scmA.groupby("component")["component_availability_pct"].mean().reset_index().sort_values("component_availability_pct")
    fig = px.bar(comp, x="component", y="component_availability_pct", title="Lowest Availability Components")
    st.plotly_chart(fig, use_container_width=True)

if "product_availability_pct" in scmA.columns and "revenue" in finB.columns:
    a = scmA.groupby("product")["product_availability_pct"].mean()
    b = finB.groupby("product")["revenue"].sum()
    ab = pd.concat([a,b], axis=1).dropna().reset_index()
    if not ab.empty:
        fig = px.scatter(ab, x="product_availability_pct", y="revenue", hover_name="product", title="Availability vs Revenue (Product)")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldown")
if not scmA.empty: st.dataframe(scmA)
if not finB.empty: st.dataframe(finB)
