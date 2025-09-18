
import streamlit as st, pandas as pd, plotly.express as px
from utils_dual_v2 import load_sources, coerce_num, add_time_filters

st.set_page_config(page_title="Purchase", page_icon="🛒", layout="wide")
st.title("🛒 Purchase — Supplier KPIs & Financial Impact")

data = load_sources(st.session_state.get("ops_path"), st.session_state.get("fin_path"),
                    st.session_state.get("ops_up"), st.session_state.get("fin_up"))
ops = pd.concat(list(data["OPS"].values()), ignore_index=True, sort=False) if data["OPS"] else pd.DataFrame()
fin = pd.concat(list(data["FIN"].values()), ignore_index=True, sort=False) if data["FIN"] else pd.DataFrame()

st.caption(f"Data status → OPS rows: {len(ops)} | FIN rows: {len(fin)}")

if ops.empty and fin.empty:
    st.warning("No supplier data detected. Ensure the OPS and FIN files are selected/uploaded on Home.")
    st.stop()

if not ops.empty: ops = add_time_filters(ops)
if not fin.empty: fin = add_time_filters(fin)

# Filters
sup_list = sorted(pd.concat([ops.get('supplier', pd.Series(dtype=str)),
                             fin.get('supplier', pd.Series(dtype=str))], ignore_index=True).dropna().unique().tolist())
sel_sup = st.multiselect("Supplier(s)", sup_list, default=sup_list)

def filt(df):
    if df.empty or "supplier" not in df.columns: return df
    return df[df["supplier"].isin(sel_sup)] if sel_sup else df

ops, fin = filt(ops), filt(fin)

# KPI tiles
ops = coerce_num(ops, ["delivery_reliability_pct","rejection_pct","component_obsolete_pct","raw_material_cost_pct"])
fin = coerce_num(fin, ["revenue","cogs","indirect_cost","operating_profit","roi_pct"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
if "delivery_reliability_pct" in ops.columns: c1.metric("Delivery Reliability %", f"{ops['delivery_reliability_pct'].mean():.2f}%")
if "rejection_pct" in ops.columns: c2.metric("Rejection %", f"{ops['rejection_pct'].mean():.2f}%")
if "component_obsolete_pct" in ops.columns: c3.metric("Component Obsolete %", f"{ops['component_obsolete_pct'].mean():.2f}%")
if "raw_material_cost_pct" in ops.columns: c4.metric("RM Cost %", f"{ops['raw_material_cost_pct'].mean():.2f}%")
if "operating_profit" in fin.columns: c5.metric("Operating Profit", f"{fin['operating_profit'].sum():,.0f}")
if "roi_pct" in fin.columns: c6.metric("ROI %", f"{fin['roi_pct'].mean():.2f}%")

# Graphs per KPI
left,right = st.columns(2)
if "supplier" in ops.columns and "delivery_reliability_pct" in ops.columns:
    with left:
        fig = px.box(ops, x="supplier", y="delivery_reliability_pct", points="all", title="Delivery Reliability % by Supplier")
        st.plotly_chart(fig, use_container_width=True)
if "supplier" in ops.columns and "rejection_pct" in ops.columns:
    with right:
        rej = ops.groupby("supplier", dropna=True)["rejection_pct"].mean().reset_index()
        fig = px.bar(rej, x="supplier", y="rejection_pct", title="Avg Rejection % by Supplier")
        st.plotly_chart(fig, use_container_width=True)

left,right = st.columns(2)
if "supplier" in ops.columns and "component_obsolete_pct" in ops.columns:
    with left:
        cob = ops.groupby("supplier", dropna=True)["component_obsolete_pct"].mean().reset_index()
        fig = px.bar(cob, x="supplier", y="component_obsolete_pct", title="Component Obsolete % by Supplier")
        st.plotly_chart(fig, use_container_width=True)
if "supplier" in ops.columns and "raw_material_cost_pct" in ops.columns:
    with right:
        rmc = ops.groupby("supplier", dropna=True)["raw_material_cost_pct"].mean().reset_index()
        fig = px.bar(rmc, x="supplier", y="raw_material_cost_pct", title="RM Cost % by Supplier")
        st.plotly_chart(fig, use_container_width=True)

if "supplier" in fin.columns and "operating_profit" in fin.columns:
    fig = px.bar(fin.groupby("supplier", dropna=True)["operating_profit"].sum().reset_index(),
                 x="supplier", y="operating_profit", title="Operating Profit by Supplier")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldown")
if not ops.empty: st.dataframe(ops)
if not fin.empty: st.dataframe(fin)
