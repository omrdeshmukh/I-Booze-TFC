
import streamlit as st
import pandas as pd
import plotly.express as px
from utils_dual import load_dual_sources, coerce_num, add_filters

st.set_page_config(page_title="Operations (Dual Excel)", page_icon="🏭", layout="wide")
st.title("🏭 Operations — Warehouses & Plants → COGS/Profit (Dual Source)")

dual = load_dual_sources()
if not dual["A"] and not dual["B"]:
    st.stop()

framesA = []
for s, df in dual["A"].items():
    need = ["inbound_cube_util_pct","outbound_cube_util_pct","mixing_util_pct","bottling_util_pct","plan_adherence_pct","round","week","plant","warehouse"]
    if any([(c in df.columns) for c in need]):
        framesA.append(df)
opsA = pd.concat(framesA, ignore_index=True, sort=False) if framesA else pd.DataFrame()

framesB = []
for s, df in dual["B"].items():
    need = ["cogs","operating_profit","roi_pct","round","week"]
    if any([(c in df.columns) for c in need]):
        framesB.append(df)
finB = pd.concat(framesB, ignore_index=True, sort=False) if framesB else pd.DataFrame()

if not opsA.empty:
    opsA = add_filters(opsA)
if not finB.empty:
    finB = add_filters(finB)

opsA = coerce_num(opsA, ["inbound_cube_util_pct","outbound_cube_util_pct","mixing_util_pct","bottling_util_pct","plan_adherence_pct"])
finB = coerce_num(finB, ["cogs","operating_profit","roi_pct"])

c1,c2,c3,c4,c5,c6 = st.columns(6)
if "inbound_cube_util_pct" in opsA.columns:
    c1.metric("Inbound Util %", f"{opsA['inbound_cube_util_pct'].mean():.2f}%")
if "outbound_cube_util_pct" in opsA.columns:
    c2.metric("Outbound Util %", f"{opsA['outbound_cube_util_pct'].mean():.2f}%")
if "mixing_util_pct" in opsA.columns:
    c3.metric("Mixing Util %", f"{opsA['mixing_util_pct'].mean():.2f}%")
if "bottling_util_pct" in opsA.columns:
    c4.metric("Bottling Util %", f"{opsA['bottling_util_pct'].mean():.2f}%")
if "plan_adherence_pct" in opsA.columns:
    c5.metric("Plan Adherence %", f"{opsA['plan_adherence_pct'].mean():.2f}%")
if "cogs" in finB.columns:
    c6.metric("COGS", f"{finB['cogs'].sum():,.0f}")

# Time series
if "week" in opsA.columns and "inbound_cube_util_pct" in opsA.columns:
    st.subheader("Inbound Utilization Over Time")
    fig = px.line(opsA.sort_values("week"), x="week", y="inbound_cube_util_pct")
    st.plotly_chart(fig, use_container_width=True)
if "week" in opsA.columns and "outbound_cube_util_pct" in opsA.columns:
    st.subheader("Outbound Utilization Over Time")
    fig = px.line(opsA.sort_values("week"), x="week", y="outbound_cube_util_pct")
    st.plotly_chart(fig, use_container_width=True)
if "week" in opsA.columns and "mixing_util_pct" in opsA.columns:
    st.subheader("Mixing Utilization Over Time")
    fig = px.line(opsA.sort_values("week"), x="week", y="mixing_util_pct")
    st.plotly_chart(fig, use_container_width=True)
if "week" in opsA.columns and "bottling_util_pct" in opsA.columns:
    st.subheader("Bottling Utilization Over Time")
    fig = px.line(opsA.sort_values("week"), x="week", y="bottling_util_pct")
    st.plotly_chart(fig, use_container_width=True)

if "plan_adherence_pct" in opsA.columns and "cogs" in finB.columns:
    st.subheader("Plan Adherence vs COGS")
    aggA = opsA.groupby("week", dropna=True)["plan_adherence_pct"].mean()
    aggB = finB.groupby("week", dropna=True)["cogs"].sum()
    ab = pd.concat([aggA, aggB], axis=1).dropna().reset_index()
    fig = px.scatter(ab, x="plan_adherence_pct", y="cogs", trendline="ols")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldowns")
if not opsA.empty:
    st.markdown("**Operations KPIs (from TFC_-2_6.xlsx)**")
    st.dataframe(opsA)
if not finB.empty:
    st.markdown("**Finance KPIs (from FinanceReport (3).xlsx)**")
    st.dataframe(finB)
