
import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_fact, coerce_num, kpi_row, add_round_week_filters, ensure_cols

st.set_page_config(page_title="Operations Dashboard", page_icon="🏭", layout="wide")
st.title("🏭 Operations — Inbound/Outbound/Mixing/Bottling → ROI & COGS")

df = load_fact()
if df.empty:
    st.stop()

df = add_round_week_filters(df)

# Area toggles
area_inbound = st.checkbox("Inbound Warehouse", value=True)
area_outbound = st.checkbox("Outbound Warehouse", value=True)
area_mixing = st.checkbox("Mixing", value=True)
area_bottling = st.checkbox("Bottling", value=True)

num_cols = ["inbound_cube_util_pct","outbound_cube_util_pct","mixing_util_pct","bottling_util_pct",
            "plan_adherence_pct","cogs","operating_profit","roi_pct"]
df = coerce_num(df, [c for c in num_cols if c in df.columns])

kpis = []
if area_inbound and "inbound_cube_util_pct" in df.columns:
    kpis.append(("Inbound Util %", df["inbound_cube_util_pct"].mean(skipna=True), "%"))
if area_outbound and "outbound_cube_util_pct" in df.columns:
    kpis.append(("Outbound Util %", df["outbound_cube_util_pct"].mean(skipna=True), "%"))
if area_mixing and "mixing_util_pct" in df.columns:
    kpis.append(("Mixing Util %", df["mixing_util_pct"].mean(skipna=True), "%"))
if area_bottling and "bottling_util_pct" in df.columns:
    kpis.append(("Bottling Util %", df["bottling_util_pct"].mean(skipna=True), "%"))
if "plan_adherence_pct" in df.columns:
    kpis.append(("Plan Adherence %", df["plan_adherence_pct"].mean(skipna=True), "%"))
if "cogs" in df.columns:
    kpis.append(("COGS", df["cogs"].sum(skipna=True), ""))
if "operating_profit" in df.columns:
    kpis.append(("Operating Profit", df["operating_profit"].sum(skipna=True), ""))
if "roi_pct" in df.columns:
    kpis.append(("ROI", df["roi_pct"].mean(skipna=True), "%"))
if kpis: kpi_row(kpis)

# Utilization charts
if area_inbound and "inbound_cube_util_pct" in df.columns and "week" in df.columns:
    st.subheader("Inbound Warehouse Utilization Over Time")
    fig = px.line(df.dropna(subset=["week","inbound_cube_util_pct"]).sort_values("week"),
                  x="week", y="inbound_cube_util_pct", title="Inbound Utilization %")
    st.plotly_chart(fig, use_container_width=True)

if area_outbound and "outbound_cube_util_pct" in df.columns and "week" in df.columns:
    st.subheader("Outbound Warehouse Utilization Over Time")
    fig = px.line(df.dropna(subset=["week","outbound_cube_util_pct"]).sort_values("week"),
                  x="week", y="outbound_cube_util_pct", title="Outbound Utilization %")
    st.plotly_chart(fig, use_container_width=True)

if area_mixing and "mixing_util_pct" in df.columns and "week" in df.columns:
    st.subheader("Mixing Utilization Over Time")
    fig = px.line(df.dropna(subset=["week","mixing_util_pct"]).sort_values("week"),
                  x="week", y="mixing_util_pct", title="Mixing Utilization %")
    st.plotly_chart(fig, use_container_width=True)

if area_bottling and "bottling_util_pct" in df.columns and "week" in df.columns:
    st.subheader("Bottling Utilization Over Time")
    fig = px.line(df.dropna(subset=["week","bottling_util_pct"]).sort_values("week"),
                  x="week", y="bottling_util_pct", title="Bottling Utilization %")
    st.plotly_chart(fig, use_container_width=True)

# Plan adherence vs COGS / Profit
if "plan_adherence_pct" in df.columns and "cogs" in df.columns:
    st.subheader("Plan Adherence vs COGS")
    agg = df.groupby("week", dropna=True).agg(plan_adherence_pct=("plan_adherence_pct","mean"),
                                              cogs=("cogs","sum")).reset_index()
    fig = px.scatter(agg, x="plan_adherence_pct", y="cogs", trendline="ols", title="Higher Adherence → Lower COGS?")
    st.plotly_chart(fig, use_container_width=True)

# Drilldown
st.subheader("Drilldown")
cols = ensure_cols(df, ["round","week","plant","warehouse","inbound_cube_util_pct","outbound_cube_util_pct",
                        "mixing_util_pct","bottling_util_pct","plan_adherence_pct","cogs","operating_profit","roi_pct"])
st.dataframe(df[cols].sort_values(by=ensure_cols(df, ["round","week"]), na_position='last'))
