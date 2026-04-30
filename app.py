import sys
import io
import streamlit as st
import pandas as pd

# Modular Imports
from data_loader import upload_file
from data_cleaner import apply_institutional_logic, finalize_report, clean_url_manually, apply_precision_manually
from data_transformer import change_datatypes
from data_gamoshi import process_gamoshi_report 
from lookup_engine import build_master_mapping, apply_master_lookup

st.set_page_config(page_title="Analytica Pro", layout="wide")

def main():
    st.title("🧼 Analytica: RevOps Engineering")
    
    if "catalog" not in st.session_state:
        st.session_state.catalog = {}

    # 1. IMPORT CENTER
    with st.expander("📂 Import Center", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("### 📄 Standard Data Upload")
            new_data = upload_file()
            if new_data:
                for name, df in new_data.items():
                    if name not in st.session_state.catalog:
                        st.session_state.catalog[name] = {"df": df}
        with c2:
            st.markdown("### 📊 Gamoshi Specialized Workflow")
            g_file = st.file_uploader("Upload Gamoshi Excel", type=['xlsx'], key="gamoshi_up")
            if g_file:
                # Explicit "is not None" check to avoid pandas ambiguity error
                g_cat, g_book_bytes = process_gamoshi_report(g_file)
                if g_cat is not None:
                    for name, df in g_cat.items():
                        if name not in st.session_state.catalog:
                            st.session_state.catalog[name] = {"df": df}
                    st.download_button("📥 Download Split Workbook", data=g_book_bytes, file_name="Gamoshi_Split.xlsx")

    # 2. DATA PROCESSING
    if st.session_state.catalog:
        selected_name = st.sidebar.selectbox("Active Dataset:", list(st.session_state.catalog.keys()))
        active_df = st.session_state.catalog[selected_name]["df"]
        
        st.subheader(f"📊 Live View: {selected_name}")
        st.dataframe(active_df, use_container_width=True, height=350)
        
        menu = st.sidebar.radio("Navigate Steps:", [
            "1. Institutional Cleanup", 
            "2. Manual Engineering Tools",
            "3. Type Conversion", 
            "4. Column Finalizer"
        ])

        def commit_changes(new_df):
            st.session_state.catalog[selected_name]["df"] = new_df
            st.rerun()

        if menu == "1. Institutional Cleanup":
            st.header("Step 1 & 2: AdPushup Rules")
            s_col = st.selectbox("Site/Domain Column:", active_df.columns)
            e_col = st.selectbox("Email Column:", active_df.columns)
            i_col = st.selectbox("Site ID (Optional):", [None] + list(active_df.columns))
            if st.button("🚀 Run Rules Cleanup"):
                commit_changes(apply_institutional_logic(active_df, s_col, e_col, i_col))

        elif menu == "2. Manual Engineering Tools":
            st.header("🛠️ Engineering Tools")
            
            # URL Cleaning
            t_col = st.selectbox("Select Column to Clean (URL):", active_df.columns)
            if st.button("🔗 Clean URLs Now"):
                commit_changes(clean_url_manually(active_df, t_col))
            
            st.divider()
            
            # Decimal Precision
            num_cols = active_df.select_dtypes(include=['number']).columns.tolist()
            prec_cols = st.multiselect("Select columns for 2-Decimal Precision:", num_cols)
            if st.button("💎 Apply Rounding Now"):
                commit_changes(apply_precision_manually(active_df, prec_cols))

            st.divider()
            
            # Manual Site ID Mapping (One-by-one for current active sheet)
            st.subheader("🗺️ Master Site ID Mapping")
            m_file = st.file_uploader("Upload Mapping Workbook (AB, DE, GH, JK)", type=['xlsx'], key="manual_map")
            if m_file:
                m_match_col = st.selectbox("Match Domain using:", active_df.columns)
                if st.button("🗺️ Execute Mapping"):
                    m_dict = build_master_mapping(pd.read_excel(m_file))
                    # Maps domains and fills unmatched rows with 'Nil'
                    commit_changes(apply_master_lookup(active_df, m_match_col, m_dict))
                    st.success("Mapping complete for this sheet. Unmatched rows marked as 'Nil'.")

        elif menu == "3. Type Conversion":
            st.header("Step 3: Change Column Types")
            # Fixed: handles Nullable Integer (Int64) for NaN support
            transformed_df = change_datatypes(active_df)
            if transformed_df is not None and not transformed_df.equals(active_df):
                commit_changes(transformed_df)

        elif menu == "4. Column Finalizer":
            st.header("Step 4: Trim Columns")
            to_keep = st.multiselect("Select columns to KEEP:", active_df.columns.tolist(), default=active_df.columns.tolist())
            if st.button("🏁 Finalize & Trim"):
                commit_changes(finalize_report(active_df, to_keep))

        # --- SIDEBAR EXPORT SETTINGS ---
        st.sidebar.divider()
        st.sidebar.header("📥 Export Settings")
        file_name_input = st.sidebar.text_input("Export Filename:", value=f"cleaned_{selected_name.split('.')[0]}")
        
        # CSV Export
        csv = active_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Export CSV", csv, f"{file_name_input}.csv")
        
        # Excel Export
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            active_df.to_excel(writer, index=False)
        st.sidebar.download_button("📊 Export Excel", buffer.getvalue(), f"{file_name_input}.xlsx")

    else:
        st.info("👋 Welcome! Please upload files to begin.")

if __name__ == "__main__":
    main()
