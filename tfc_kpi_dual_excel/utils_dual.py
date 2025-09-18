
import streamlit as st
import pandas as pd
import numpy as np
import re
from typing import Dict, List, Tuple, Optional

DEFAULT_FILE_A = "TFC_-2_6.xlsx"
DEFAULT_FILE_B = "FinanceReport (3).xlsx"

ALIAS = {
    "round": ["round","period","cycle"],
    "week": ["week","wk"],
    "date": ["date","day","timestamp"],
    "customer": ["customer","client","channel","account"],
    "product": ["product","sku","item","fg","finished good","finished_goods","fg_sku"],
    "component": ["component","rawmaterial","raw_material","rm","ingredient","material"],
    "supplier": ["supplier","vendor"],
    "plant": ["plant","factory","site","production_site","mixing","bottling"],
    "warehouse": ["warehouse","dc","inbound_warehouse","outbound_warehouse"],
    "order_qty": ["orderqty","order_qty","ordered_qty","orders","demand_qty","demand"],
    "delivered_qty": ["deliveredqty","delivered_qty","ship_qty","shipped_qty","deliveries"],
    "backorder_qty": ["backorderqty","backorder_qty","bo_qty","backorders"],
    "revenue": ["realizedrevenue","revenue","sales_value","sales"],
    "price": ["price","unit_price","selling_price"],
    "discount": ["discount","disc_pct","discount_pct"],
    "cogs": ["cogs","cost_of_goods_sold","cost of goods sold","product_cost"],
    "indirect_cost": ["indirectcost","indirect_cost","overhead","opex"],
    "operating_profit": ["operatingprofit","operating_profit","net_profit","profit","ebit"],
    "capital_employed": ["capitalemployed","capital_employed","cap_employed"],
    "roi_pct": ["roi_pct","roi%","roi","return_on_investment"],
    "service_level_pct": ["servicelevelpct","service_level_pct","service_level","fill_rate","fillrate"],
    "shelf_life_days": ["shelflifeachieveddays","shelf_life_days","shelf_life","shelflife"],
    "forecast": ["forecast","fcst"],
    "forecast_error_pct": ["forecasterrorpct","forecast_error_pct","mape","forecast_error"],
    "obsolescence_qty": ["obsolescenceqty","obsolete_qty","obsolescence_qty"],
    "obsolescence_value": ["obsolescencevalue","obsolete_value","obsolescence_value"],
    "component_availability_pct": ["componentavailabilitypct","component_availability_pct"],
    "product_availability_pct": ["productavailabilitypct","product_availability_pct","availability"],
    "delivery_reliability_pct": ["deliveryreliabilitypct","delivery_reliability_pct","on_time_delivery_pct"],
    "rejection_pct": ["rejectionpct","rejection_pct","reject_rate_pct","quality_reject_pct"],
    "component_obsolete_pct": ["componentobsoletepct","component_obsolete_pct"],
    "raw_material_cost_pct": ["rawmaterialcostpct","raw_material_cost_pct","rm_cost_pct"],
    "inbound_cube_util_pct": ["inboundcubeutilpct","inbound_cube_util_pct","inbound_util_pct"],
    "outbound_cube_util_pct": ["outboundcubeutilpct","outbound_cube_util_pct","outbound_util_pct"],
    "mixing_util_pct": ["mixingutilpct","mixing_util_pct"],
    "bottling_util_pct": ["bottlingutilpct","bottling_util_pct"],
    "plan_adherence_pct": ["productionplanadherencepct","plan_adherence_pct","schedule_adherence_pct"],
}

_alias_rev = {re.sub(r'[^a-z0-9]+','',v):k for k,vals in ALIAS.items() for v in vals}

def _norm(s:str)->str:
    return re.sub(r'[^a-z0-9]+','',str(s).strip().lower())

def std_col(c:str)->Optional[str]:
    n = _norm(c)
    if n in _alias_rev:
        return _alias_rev[n]
    # fallbacks
    if n.endswith("pct"):
        if "service" in n or "fill" in n: return "service_level_pct"
        if "availability" in n and "product" in n: return "product_availability_pct"
        if "availability" in n and "component" in n: return "component_availability_pct"
        if "ontime" in n or "reliab" in n: return "delivery_reliability_pct"
        if "reject" in n: return "rejection_pct"
        if "obsolete" in n and "component" in n: return "component_obsolete_pct"
        if "util" in n and "inbound" in n: return "inbound_cube_util_pct"
        if "util" in n and "outbound" in n: return "outbound_cube_util_pct"
        if "util" in n and "mix" in n: return "mixing_util_pct"
        if "util" in n and "bottling" in n: return "bottling_util_pct"
        if "adherence" in n or "schedule" in n: return "plan_adherence_pct"
        if "roi" in n: return "roi_pct"
        if "raw" in n and "cost" in n: return "raw_material_cost_pct"
    if "order" in n and "qty" in n: return "order_qty"
    if ("deliver" in n or "ship" in n) and "qty" in n: return "delivered_qty"
    if "backorder" in n and "qty" in n: return "backorder_qty"
    if "obsolesc" in n and "qty" in n: return "obsolescence_qty"
    if "obsolesc" in n and "val" in n: return "obsolescence_value"
    if "revenue" in n or n=="sales": return "revenue"
    if "cogs" in n or "costofgoods" in n: return "cogs"
    if "overhead" in n or "indirect" in n or n=="opex": return "indirect_cost"
    if "profit" in n or "ebit" in n: return "operating_profit"
    if n in ["sku","fgsku","fg","item"]: return "product"
    if "customer" in n or "client" in n or "channel" in n: return "customer"
    if "supplier" in n or "vendor" in n: return "supplier"
    if "component" in n or "material" in n or "raw" in n: return "component"
    if "plant" in n or "factory" in n or "site" in n: return "plant"
    if "warehouse" in n or n in ["dc","inboundwarehouse","outboundwarehouse"]: return "warehouse"
    if n.startswith("week") or n=="wk": return "week"
    if n in ["round","period","cycle"]: return "round"
    if "date" in n or "timestamp" in n or n=="day": return "date"
    if "forecast" in n and "error" in n: return "forecast_error_pct"
    if n=="forecast" or "fcst" in n: return "forecast"
    if "shelf" in n: return "shelf_life_days"
    if n=="price" or "unitprice" in n: return "price"
    if "discount" in n: return "discount"
    if "capital" in n and "employed" in n: return "capital_employed"
    if "roi" in n: return "roi_pct"
    return None

def read_all_sheets(path:str)->Dict[str,pd.DataFrame]:
    xls = pd.ExcelFile(path)
    out = {}
    for s in xls.sheet_names:
        try:
            df = xls.parse(s)
        except Exception:
            continue
        if df.empty: 
            continue
        # map columns
        mapped = {}
        for c in df.columns:
            key = std_col(c)
            if key and key not in mapped:
                mapped[key] = df[c]
        if mapped:
            sdf = pd.DataFrame(mapped)
            sdf["__sheet"] = s
            out[s] = sdf
    return out

@st.cache_data(show_spinner=False)
def load_dual_sources(file_a:str=DEFAULT_FILE_A, file_b:str=DEFAULT_FILE_B):
    # try repo root
    paths = []
    for p in [file_a, file_b, f"data/{file_a}", f"data/{file_b}"]:
        if st.session_state.get("uploaded_override", {}).get(p):
            # prefer uploaded overrides
            pass
        if (not p in st.session_state.get("uploaded_override", {})) and not (st.session_state.get("uploaded_override", {}).get(p)):
            if not paths:
                pass
    # Build dict of DataFrames per source
    result = {"A":{}, "B":{}}
    # Load from upload overrides if present; else from disk
    srcA = st.session_state.get("uploaded_override", {}).get(file_a) or st.session_state.get("uploaded_override", {}).get(f"data/{file_a}")
    if srcA is not None:
        xlsA = pd.ExcelFile(srcA)
    else:
        try:
            xlsA = pd.ExcelFile(file_a)
        except Exception:
            try:
                xlsA = pd.ExcelFile(f"data/{file_a}")
            except Exception:
                xlsA = None
    if xlsA is not None:
        tmp = {}
        for s in xlsA.sheet_names:
            try:
                df = xlsA.parse(s)
                if df.empty: 
                    continue
                mapped = {}
                for c in df.columns:
                    key = std_col(c)
                    if key and key not in mapped:
                        mapped[key] = df[c]
                if mapped:
                    sdf = pd.DataFrame(mapped)
                    sdf["__sheet"] = s
                    tmp[s] = sdf
            except Exception:
                continue
        result["A"] = tmp

    srcB = st.session_state.get("uploaded_override", {}).get(file_b) or st.session_state.get("uploaded_override", {}).get(f"data/{file_b}")
    if srcB is not None:
        xlsB = pd.ExcelFile(srcB)
    else:
        try:
            xlsB = pd.ExcelFile(file_b)
        except Exception:
            try:
                xlsB = pd.ExcelFile(f"data/{file_b}")
            except Exception:
                xlsB = None
    if xlsB is not None:
        tmp = {}
        for s in xlsB.sheet_names:
            try:
                df = xlsB.parse(s)
                if df.empty: 
                    continue
                mapped = {}
                for c in df.columns:
                    key = std_col(c)
                    if key and key not in mapped:
                        mapped[key] = df[c]
                if mapped:
                    sdf = pd.DataFrame(mapped)
                    sdf["__sheet"] = s
                    tmp[s] = sdf
            except Exception:
                continue
        result["B"] = tmp

    return result

def union_frames(frames:List[pd.DataFrame])->pd.DataFrame:
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)

def coerce_num(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def add_filters(df: pd.DataFrame):
    c1, c2 = st.columns(2)
    with c1:
        rounds = sorted(df.get("round", pd.Series([])).dropna().unique().tolist())
        rsel = st.multiselect("Round", rounds, default=rounds)
    with c2:
        weeks = sorted(df.get("week", pd.Series([])).dropna().unique().tolist())
        wsel = st.multiselect("Week", weeks, default=weeks[-12:] if len(weeks)>12 else weeks)
    mask = pd.Series(True, index=df.index)
    if "round" in df.columns and rsel:
        mask &= df["round"].isin(rsel)
    if "week" in df.columns and wsel:
        mask &= df["week"].isin(wsel)
    return df[mask]

def pick_sheets(dual, keysA:List[str], keysB:List[str]):
    # Let user pick which sheets to use for each page
    a_names = list(dual["A"].keys())
    b_names = list(dual["B"].keys())
    a_choice = st.selectbox("Choose sheet from TFC_-2_6.xlsx", ["<auto>"] + a_names, index=0)
    b_choice = st.selectbox("Choose sheet from FinanceReport (3).xlsx", ["<auto>"] + b_names, index=0)
    def pick(src, wanted):
        if src=="A":
            pool = dual["A"]
        else:
            pool = dual["B"]
        # auto-find a sheet that contains all "wanted" columns
        for name, df in pool.items():
            if all([(c in df.columns) for c in wanted]):
                return df.assign(__file=src)
        # or return the first available
        if pool:
            name0 = list(pool.keys())[0]
            return pool[name0].assign(__file=src)
        return pd.DataFrame()
    a_df = pick("A", keysA) if a_choice=="<auto>" else dual["A"].get(a_choice, pd.DataFrame()).assign(__file="A")
    b_df = pick("B", keysB) if b_choice=="<auto>" else dual["B"].get(b_choice, pd.DataFrame()).assign(__file="B")
    return a_df, b_df

