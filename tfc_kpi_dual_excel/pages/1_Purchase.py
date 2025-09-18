
import streamlit as st
import pandas as pd
import plotly.express as px
from utils_dual import load_dual_sources, coerce_num, add_filters

st.set_page_config(page_title="Purchase (Dual Excel)", page_icon="🛒", layout="wide")
st.title("🛒 Purchase — Supplier Performance → ROI & Financial Impact (Dual Source)")

dual = load_dual_sources()
if not dual["A"] and not dual["B"]:
    st.stop()

# Build frames from A (operational) for supplier KPIs
ops_frames = []
for s, df in dual["A"].items():
    needed = ["supplier","component","delivery_reliability_pct","rejection_pct","component_obsolete_pct","raw_material_cost_pct",
              "round","week"]
    if any([(c in df.columns) for c in needed]):
        ops_frames.append(df)
ops = pd.concat(ops_frames, ignore_index=True, sort=False) if ops_frames else pd.DataFrame()

# Build finance frame from B
fin_frames = []
for s, df in dual["B"].items():
    needed = ["supplier","revenue","cogs","indirect_cost","operating_profit","roi_pct","round","week"]
    if any([(c in df.columns) for c in needed]):
        fin_frames.append(df)
fin = pd.concat(fin_frames, ignore_index=True, sort=False) if fin_frames else pd.DataFrame()

# Join if both have supplier columns; else show separately
if not ops.empty:
    ops = add_filters(ops)
if not fin.empty:
    fin = add_filters(fin)

# Supplier selection
sup_values = sorted(pd.concat([ops.get("supplier", pd.Series(dtype=str)),
                               fin.get("supplier", pd.Series(dtype=str))], ignore_index=True).dropna().unique().tolist())
sel_sup = st.multiselect("Supplier(s)", sup_values, default=sup_values)

def apply_sup(df):
    if df.empty or "supplier" not in df.columns:
        return df
    return df[df["supplier"].isin(sel_sup)] if sel_sup else df

ops = apply_sup(ops)
fin = apply_sup(fin)

# KPI cards from ops + finance
num_cols_ops = ["delivery_reliability_pct","rejection_pct","component_obsolete_pct","raw_material_cost_pct"]
ops = coerce_num(ops, [c for c in num_cols_ops if c in ops.columns])
num_cols_fin = ["revenue","cogs","indirect_cost","operating_profit","roi_pct"]
fin = coerce_num(fin, [c for c in num_cols_fin if c in fin.columns])

c1,c2,c3,c4,c5,c6 = st.columns(6)
if "delivery_reliability_pct" in ops.columns:
    c1.metric("Delivery Reliability %", f"{ops['delivery_reliability_pct'].mean():.2f}%")
if "rejection_pct" in ops.columns:
    c2.metric("Rejection %", f"{ops['rejection_pct'].mean():.2f}%")
if "component_obsolete_pct" in ops.columns:
    c3.metric("Component Obsolete %", f"{ops['component_obsolete_pct'].mean():.2f}%")
if "raw_material_cost_pct" in ops.columns:
    c4.metric("RM Cost %", f"{ops['raw_material_cost_pct'].mean():.2f}%")
if "operating_profit" in fin.columns:
    c5.metric("Operating Profit", f"{fin['operating_profit'].sum():,.0f}")
if "roi_pct" in fin.columns:
    c6.metric("ROI %", f"{fin['roi_pct'].mean():.2f}%")

# Charts
if "supplier" in ops.columns and "delivery_reliability_pct" in ops.columns:
    st.subheader("Supplier Reliability")
    fig = px.box(ops, x="supplier", y="delivery_reliability_pct", points="all")
    st.plotly_chart(fig, use_container_width=True)

if "supplier" in ops.columns and "rejection_pct" in ops.columns:
    st.subheader("Supplier Rejection %")
    rej = ops.groupby("supplier", dropna=True)["rejection_pct"].mean().reset_index()
    fig = px.bar(rej, x="supplier", y="rejection_pct")
    st.plotly_chart(fig, use_container_width=True)

if "supplier" in fin.columns and "operating_profit" in fin.columns:
    st.subheader("Operating Profit by Supplier")
    prof = fin.groupby("supplier", dropna=True)["operating_profit"].sum().reset_index()
    fig = px.bar(prof, x="supplier", y="operating_profit")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldowns")
if not ops.empty:
    st.markdown("**Operational KPIs (from TFC_-2_6.xlsx)**")
    st.dataframe(ops)
if not fin.empty:
    st.markdown("**Financials (from FinanceReport (3).xlsx)**")
    st.dataframe(fin)
