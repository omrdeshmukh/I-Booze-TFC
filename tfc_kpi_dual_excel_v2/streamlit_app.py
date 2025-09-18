
import streamlit as st
from utils_dual_v2 import list_candidate_excels, load_sources

st.set_page_config(page_title="TFC KPI (Dual Excel v2)", page_icon="🍊", layout="wide")
st.title("🍊 The Fresh Connection — Dual-Source KPI Dashboards (v2)")
st.caption("No consolidation. Reads two Excel workbooks directly. Choose which file is Ops vs Finance or upload them.")

# discover files
cands = list_candidate_excels()
st.write("Detected Excel files:", cands if cands else "None found. You can still upload below.")

# pick mapping
ops_choice = st.selectbox("Pick the **Operations/SCM/Sales/Purchase** workbook", ["<upload or none>"] + cands, index=0)
fin_choice = st.selectbox("Pick the **Finance** workbook", ["<upload or none>"] + cands, index=0)

with st.expander("⬆️ Upload workbooks (optional)"):
    up_ops = st.file_uploader("Upload Operations workbook (.xlsx)", type=["xlsx"], key="ops_up")
    up_fin = st.file_uploader("Upload Finance workbook (.xlsx)", type=["xlsx"], key="fin_up")

data = load_sources(None if ops_choice=="<upload or none>" else ops_choice,
                    None if fin_choice=="<upload or none>" else fin_choice,
                    up_ops, up_fin)

ok_ops = len(data["OPS"])>0
ok_fin = len(data["FIN"])>0
msg = "OPS ✅" if ok_ops else "OPS ❌"
msg += " | FIN ✅" if ok_fin else " | FIN ❌"
st.info(f"Loaded: {msg}. Use the sidebar pages. (Pages degrade gracefully if a source is missing.)")

with st.expander("Sheets detected"):
    st.write("**OPS sheets:**", list(data["OPS"].keys()))
    st.write("**FIN sheets:**", list(data["FIN"].keys()))
