
import streamlit as st
from utils_dual_v2 import list_candidate_excels, load_sources

st.set_page_config(page_title="TFC KPI (Dual Excel v2)", page_icon="🍊", layout="wide")
st.title("🍊 The Fresh Connection — Dual-Source KPI Dashboards (v2)")
st.caption("No consolidation. Reads two Excel workbooks directly. Choose which file is Ops vs Finance or upload them.")

# discover files
cands = list_candidate_excels()
st.write("Detected Excel files:", cands if cands else "None found. You can still upload below.")

# sensible defaults: preselect first/second candidate if present
ops_default_idx = 1 if len(cands) >= 1 else 0
fin_default_idx = 2 if len(cands) >= 2 else (1 if len(cands) >= 1 else 0)

ops_choice = st.selectbox("Pick the **Operations/SCM/Sales/Purchase** workbook", ["<upload or none>"] + cands, index=ops_default_idx)
fin_choice = st.selectbox("Pick the **Finance** workbook", ["<upload or none>"] + cands, index=fin_default_idx)

# remember selections for other pages
if "ops_path" not in st.session_state and ops_choice != "<upload or none>":
    st.session_state["ops_path"] = ops_choice
if "fin_path" not in st.session_state and fin_choice != "<upload or none>":
    st.session_state["fin_path"] = fin_choice
# update on change
if ops_choice != "<upload or none>":
    st.session_state["ops_path"] = ops_choice
if fin_choice != "<upload or none>":
    st.session_state["fin_path"] = fin_choice

with st.expander("⬆️ Upload workbooks (optional)"):
    up_ops = st.file_uploader("Upload Operations workbook (.xlsx)", type=["xlsx"], key="ops_up")
    up_fin = st.file_uploader("Upload Finance workbook (.xlsx)", type=["xlsx"], key="fin_up")
    # Keep in session for all pages
    if up_ops is not None:
        st.session_state["ops_up"] = up_ops
        st.success("Operations workbook uploaded and will override selection.")
    if up_fin is not None:
        st.session_state["fin_up"] = up_fin
        st.success("Finance workbook uploaded and will override selection.")

# load summary (for user feedback only)
data = load_sources(st.session_state.get("ops_path"), st.session_state.get("fin_path"),
                    st.session_state.get("ops_up"), st.session_state.get("fin_up"))

ok_ops = len(data["OPS"])>0
ok_fin = len(data["FIN"])>0
msg = "OPS ✅" if ok_ops else "OPS ❌"
msg += " | FIN ✅" if ok_fin else " | FIN ❌"
st.info(f"Loaded: {msg}. Use the sidebar pages. (Pages degrade gracefully if a source is missing.)")

with st.expander("Sheets detected"):
    st.write("**OPS sheets:**", list(data["OPS"].keys()))
    st.write("**FIN sheets:**", list(data["FIN"].keys()))
