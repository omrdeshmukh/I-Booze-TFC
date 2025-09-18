
import streamlit as st
import pandas as pd
import numpy as np
from typing import Tuple, List

@st.cache_data(show_spinner=False)
def load_fact(path: str = "fact_kpis.csv") -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        st.warning("`fact_kpis.csv` not found in the app folder. Upload a CSV on this page to continue.")
        return pd.DataFrame()
    # Normalize columns to expected set if users rename
    df.columns = [c.strip().lower() for c in df.columns]
    return df

def coerce_num(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def kpi_row(kpis: List[Tuple[str, float, str]]):
    cols = st.columns(len(kpis))
    for i, (label, value, suffix) in enumerate(kpis):
        with cols[i]:
            st.metric(label, f"{value:,.2f}{suffix}")
            
def ensure_cols(df: pd.DataFrame, needed: List[str]) -> List[str]:
    return [c for c in needed if c in df.columns]

def add_round_week_filters(df: pd.DataFrame):
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        rounds = sorted([r for r in df.get("round", pd.Series([])).dropna().unique().tolist()])
        sel_rounds = st.multiselect("Round", rounds, default=rounds)
    with c2:
        weeks = sorted([w for w in df.get("week", pd.Series([])).dropna().unique().tolist()])
        default_weeks = weeks if len(weeks) <= 12 else weeks[-12:]
        sel_weeks = st.multiselect("Week", weeks, default=default_weeks)
    with c3:
        st.markdown("")
        reset = st.button("Reset filters")
        if reset:
            st.experimental_rerun()
    mask = pd.Series([True]*len(df))
    if "round" in df.columns and sel_rounds:
        mask &= df["round"].isin(sel_rounds)
    if "week" in df.columns and sel_weeks:
        mask &= df["week"].isin(sel_weeks)
    return df[mask]

def add_dimension_filter(df: pd.DataFrame, label: str, colname: str):
    values = sorted([v for v in df.get(colname, pd.Series([])).dropna().unique().tolist()])
    return st.multiselect(label, values, default=values)
