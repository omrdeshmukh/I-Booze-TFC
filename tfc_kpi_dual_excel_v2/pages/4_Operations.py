
import streamlit as st, pandas as pd, plotly.express as px
from utils_dual_v2 import load_sources, coerce_num, add_time_filters

st.set_page_config(page_title="Operations", page_icon="🏭", layout="wide")
st.title("🏭 Operations — Utilization & Plan Adherence → COGS/Profit")

data = load_sources(None, None, st.session_state.get("ops_up"), st.session_state.get("fin_up"))
opsA = pd.concat([df for df in data["OPS"].values()], ignore_index=True, sort=False) if data["OPS"] else pd.DataFrame()
finB = pd.concat([df for df in data["FIN"].values()], ignore_index=True, sort=False) if data["FIN"] else pd.DataFrame()

if not opsA.empty: opsA = add_time_filters(opsA)
if not finB.empty: finB = add_time_filters(finB)

opsA = coerce_num(opsA, ["inbound_cube_util_pct","outbound_cube_util_pct","mixing_util_pct","bottling_util_pct","plan_adherence_pct"])
finB = coerce_num(finB, ["cogs","operating_profit","roi_pct"])

c1,c2,c3,c4,c5 = st.columns(5)
if "inbound_cube_util_pct" in opsA.columns: c1.metric("Inbound Util %", f"{opsA['inbound_cube_util_pct'].mean():.2f}%")
if "outbound_cube_util_pct" in opsA.columns: c2.metric("Outbound Util %", f"{opsA['outbound_cube_util_pct'].mean():.2f}%")
if "mixing_util_pct" in opsA.columns: c3.metric("Mixing Util %", f"{opsA['mixing_util_pct'].mean():.2f}%")
if "bottling_util_pct" in opsA.columns: c4.metric("Bottling Util %", f"{opsA['bottling_util_pct'].mean():.2f}%")
if "plan_adherence_pct" in opsA.columns: c5.metric("Plan Adherence %", f"{opsA['plan_adherence_pct'].mean():.2f}%")

if "week" in opsA.columns and "inbound_cube_util_pct" in opsA.columns:
    fig = px.line(opsA.sort_values("week"), x="week", y="inbound_cube_util_pct", title="Inbound Utilization Over Time")
    st.plotly_chart(fig, use_container_width=True)
if "week" in opsA.columns and "outbound_cube_util_pct" in opsA.columns:
    fig = px.line(opsA.sort_values("week"), x="week", y="outbound_cube_util_pct", title="Outbound Utilization Over Time")
    st.plotly_chart(fig, use_container_width=True)
if "week" in opsA.columns and "mixing_util_pct" in opsA.columns:
    fig = px.line(opsA.sort_values("week"), x="week", y="mixing_util_pct", title="Mixing Utilization Over Time")
    st.plotly_chart(fig, use_container_width=True)
if "week" in opsA.columns and "bottling_util_pct" in opsA.columns:
    fig = px.line(opsA.sort_values("week"), x="week", y="bottling_util_pct", title="Bottling Utilization Over Time")
    st.plotly_chart(fig, use_container_width=True)

if "plan_adherence_pct" in opsA.columns and "cogs" in finB.columns:
    aggA = opsA.groupby("week", dropna=True)["plan_adherence_pct"].mean()
    aggB = finB.groupby("week", dropna=True)["cogs"].sum()
    ab = pd.concat([aggA, aggB], axis=1).dropna().reset_index()
    if not ab.empty:
        fig = px.scatter(ab, x="plan_adherence_pct", y="cogs", trendline="ols", title="Plan Adherence vs COGS")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Drilldown")
if not opsA.empty: st.dataframe(opsA)
if not finB.empty: st.dataframe(finB)
