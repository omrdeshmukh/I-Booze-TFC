
import streamlit as st
import pandas as pd
from utils_dual import load_dual_sources, DEFAULT_FILE_A, DEFAULT_FILE_B

st.set_page_config(page_title="TFC KPI (Dual Excel)", page_icon="📊", layout="wide")
st.title("🍊 The Fresh Connection — Dual-Source KPI Dashboards")
st.caption("No consolidation. Reads both Excel files directly and stitches KPIs at runtime.")

with st.expander("⬆️ Upload your two Excel files here (optional)"):
    upA = st.file_uploader(f"Upload {DEFAULT_FILE_A}", type=["xlsx"], key="upA")
    upB = st.file_uploader(f"Upload {DEFAULT_FILE_B}", type=["xlsx"], key="upB")
    if "uploaded_override" not in st.session_state:
        st.session_state["uploaded_override"] = {}
    if upA is not None:
        st.session_state["uploaded_override"][DEFAULT_FILE_A] = upA
        st.session_state["uploaded_override"][f"data/{DEFAULT_FILE_A}"] = upA
        st.success(f"Loaded {DEFAULT_FILE_A}")
    if upB is not None:
        st.session_state["uploaded_override"][DEFAULT_FILE_B] = upB
        st.session_state["uploaded_override"][f"data/{DEFAULT_FILE_B}"] = upB
        st.success(f"Loaded {DEFAULT_FILE_B}")

dual = load_dual_sources()

countA = sum([len(v) for v in dual["A"].values()])
countB = sum([len(v) for v in dual["B"].values()])

okA = len(dual["A"])>0
okB = len(dual["B"])>0

if not okA or not okB:
    st.error("Both files are required. Place them in the repo root or /data, or upload above: "
             f"`{DEFAULT_FILE_A}` and `{DEFAULT_FILE_B}`.")
else:
    st.success("Both sources loaded. Use the pages in the sidebar to explore dashboards.")
    with st.expander("Sheets detected"):
        st.write("**TFC_-2_6.xlsx** sheets:", list(dual["A"].keys()))
        st.write("**FinanceReport (3).xlsx** sheets:", list(dual["B"].keys()))
