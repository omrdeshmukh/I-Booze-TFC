
import streamlit as st
import pandas as pd
import plotly.express as px
from utils_dual import load_dual_sources, coerce_num, add_filters

st.set_page_config(page_title="SCM (Dual Excel)", page_icon="🔗", layout="wide")
st.title("🔗 SCM — Availability Impact (Dual Source)")

dual = load_dual_sources()
if not dual["A"] and not dual["B"]:
    st.stop()

framesA = []
for s, df in dual["A"].items():
    need = ["component_availability_pct","product_availability_pct","component","product","round","week"]
    if any([(c in df.columns) for c in need]):
        framesA.append(df)
scmA = pd.concat(framesA, ignore_index=True, sort=False) if framesA else pd.DataFrame()

framesB = []
for s, df in dual["B"].items():
    need = ["revenue","roi_pct","product","round","week"]
    if any([(c in df.columns) for c in need]):
        framesB.append(df)
finB = pd.concat(framesB, ignore_index=True, sort=False) if framesB else pd.DataFrame()

if not scmA.empty:
    scmA = add_filters(scmA)
if not finB.empty:
    finB = add_filters(finB)

# Filters
components = sorted(scmA.get("component", pd.Series(dtype=str)).dropna().unique().tolist())
products = sorted(scmA.get("product", pd.Series(dtype=str)).dropna().unique().tolist())
sel_comp = st.multiselect("Component(s)", components, default=components)
sel_prod = st.multiselect("Product(s)", products, default=products)

def filt(df):
    if df.empty: return df
    m = pd.Series(True, index=df.index)
    if "component" in df.columns and sel_comp:
        m &= df["component"].isin(sel_comp)
    if "product" in df.columns and sel_prod:
        m &= df["product"].isin(sel_prod)
    return df[m]

scmA = filt(scmA)
finB = filt(finB)

scmA = coerce_num(scmA, ["product_availability_pct","component_availability_pct"])
finB = coerce_num(finB, ["revenue","roi_pct"])

c1,c2,c3 = st.columns(3)
if "product_availability_pct" in scmA.columns:
    c1.metric("Product Availability %", f"{scmA['product_availability_pct'].mean():.2f}%")
if "component_availability_pct" in scmA.columns:
    c2.metric("Component Availability %", f"{scmA['component_availability_pct'].mean():.2f}%")
if "revenue" in finB.columns:
    c3.metric("Revenue", f"{finB['revenue'].sum():,.0f}")

if "product" in scmA.columns and "product_availability_pct" in scmA.columns:
    st.subheader("Product Availability Heatmap")
    heat = scmA.groupby(["week","product"])["product_availability_pct"].mean().reset_index()
    if not heat.empty:
        fig = px.density_heatmap(heat, x="week", y="product", z="product_availability_pct")
        st.plotly_chart(fig, use_container_width=True)

if "product_availability_pct" in scmA.columns and "revenue" in finB.columns and "product" in scmA.columns:
    st.subheader("Availability vs Revenue (by Product)")
    a = scmA.groupby("product", dropna=True)["product_availability_pct"].mean()
    b = finB.groupby("product", dropna=True)["revenue"].sum()
    ab = pd.concat([a,b], axis=1).dropna().reset_index()
    fig = px.scatter(ab, x="product_availability_pct", y="revenue", hover_name="product")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldowns")
if not scmA.empty:
    st.markdown("**SCM KPIs (from TFC_-2_6.xlsx)**")
    st.dataframe(scmA)
if not finB.empty:
    st.markdown("**Finance KPIs (from FinanceReport (3).xlsx)**")
    st.dataframe(finB)
