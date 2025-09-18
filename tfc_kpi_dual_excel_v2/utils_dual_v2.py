
import streamlit as st
import pandas as pd
import numpy as np
import re, glob, os
from typing import Dict, List, Tuple, Optional

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
def _n(s): return re.sub(r'[^a-z0-9]+','',str(s).strip().lower())
def std_col(c):
    n=_n(c)
    if n in _alias_rev: return _alias_rev[n]
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

def list_candidate_excels()->List[str]:
    # find .xlsx files in cwd and /data (non-hidden)
    files = []
    for root in [".", "data"]:
        for p in glob.glob(os.path.join(root, "*.xlsx")):
            files.append(p)
    return sorted(list(dict.fromkeys(files)))  # unique, stable order

def parse_workbook(fileobj_or_path)->Dict[str,pd.DataFrame]:
    import pandas as pd
    try:
        xls = pd.ExcelFile(fileobj_or_path)
    except Exception:
        return {}
    out={}
    for s in xls.sheet_names:
        try:
            df = xls.parse(s)
        except Exception:
            continue
        if df.empty: 
            continue
        mapped={}
        for c in df.columns:
            key = std_col(c)
            if key and key not in mapped:
                mapped[key]=df[c]
        if mapped:
            sdf=pd.DataFrame(mapped)
            sdf["__sheet"]=s
            out[s]=sdf
    return out

@st.cache_data(show_spinner=False)
def load_sources(selected_ops:Optional[str], selected_fin:Optional[str], uploaded_ops, uploaded_fin):
    # Allow uploaded overrides
    src_ops = uploaded_ops if uploaded_ops is not None else selected_ops
    src_fin = uploaded_fin if uploaded_fin is not None else selected_fin
    data={"OPS":{}, "FIN":{}}
    if src_ops is not None:
        data["OPS"]=parse_workbook(src_ops)
    if src_fin is not None:
        data["FIN"]=parse_workbook(src_fin)
    return data

def coerce_num(df: pd.DataFrame, cols: List[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

def add_time_filters(df: pd.DataFrame):
    c1,c2 = st.columns(2)
    rounds = sorted(df.get("round", pd.Series([], dtype=object)).dropna().unique().tolist())
    weeks = sorted(df.get("week", pd.Series([], dtype=object)).dropna().unique().tolist())
    rsel = c1.multiselect("Round", rounds, default=rounds)
    wsel = c2.multiselect("Week", weeks, default=weeks[-12:] if len(weeks)>12 else weeks)
    mask = pd.Series(True, index=df.index)
    if "round" in df.columns and rsel: mask &= df["round"].isin(rsel)
    if "week" in df.columns and wsel: mask &= df["week"].isin(wsel)
    return df[mask]
