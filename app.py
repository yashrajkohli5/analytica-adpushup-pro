import sys
import importlib.metadata
import io
import streamlit as st
import pandas as pd

# Modular Imports
from data_loader import upload_file
from data_cleaner import apply_institutional_logic, finalize_report, clean_url_manually, apply_precision_manually
from data_transformer import change_datatypes
from data_gamoshi import process_gamoshi_report 
# New import for the mapping engine
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
            new_data = upload_file()
            if new_data:
                for name, df in new_data.items():
                    if name not in st.session_state.catalog:
                        st.session_state.catalog[name] = {"df": df}
        with c2:
            g_file = st.file_uploader("Gamoshi Excel", type=['xlsx'], key="gamoshi_up")
            if g_file:
                g_cat, g_book = process_gamoshi_report(g_file)
                if g_cat:
                    for name, df in g_cat.items():
                        st.session_state.catalog[name] = {"df": df}
                    st.download_button("📥 Download Workbook", data=g_book, file_name="Gamoshi_Split.xlsx")

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
            i_col = st.selectbox("Site ID Column (Optional):", [None] + list(active_df.columns))
            if st.button("🚀 Run Rules Cleanup"):
                commit_changes(apply_institutional_logic(active_df, s_col, e_col, i_col))

        elif menu == "2. Manual Engineering Tools":
            st.header("🛠️ Manual URL, Precision & Master Lookup")
            
            # Manual URL Cleaning
            t_col = st.selectbox("Select Column to Clean (URL):", active_df.columns)
            if st.button("🔗 Clean URLs Now"):
                commit_changes(clean_url_manually(active_df, t_col))
            
            st.divider()
            
            # Manual Decimal Precision
            num_cols = active_df.select_dtypes(include=['number']).columns.tolist()
            prec_cols = st.multiselect("Select columns for 2-Decimal Precision:", num_cols)
            if st.button("💎 Apply Rounding Now"):
                commit_changes(apply_precision_manually(active_df, prec_cols))

            st.divider()

            # --- MASTER MAPPING SECTION ---
            st.subheader("🗺️ Master Site ID Mapping")
            st.info("Upload the workbook containing column pairs: AB, DE, GH, and JK.")
            map_file = st.file_uploader("Upload Master Mapping Workbook", type=['xlsx'], key="master_map_file")
            
            if map_file:
                lookup_df = pd.read_excel(map_file)
                # User selects which column in the report should be matched against the domain
                match_col = st.selectbox("Match IDs using this column (Domain):", active_df.columns)
                
                if st.button("🗺️ Execute Master Mapping"):
                    # 1. Build dictionary from pairs
                    master_dict = build_master_mapping(lookup_df)
                    # 2. Apply to the active report
                    mapped_df = apply_master_lookup(active_df, match_col, master_dict)
                    commit_changes(mapped_df)
                    st.success(f"Successfully created unique mappings for {len(master_dict)} domains.")

        elif menu == "3. Type Conversion":
            st.header("Step 3: Change Column Types")
            transformed_df = change_datatypes(active_df)
            if transformed_df is not None and not transformed_df.equals(active_df):
                commit_changes(transformed_df)

        elif menu == "4. Column Finalizer":
            st.header("Step 4: Trim Columns")
            all_cols = active_df.columns.tolist()
            to_keep = st.multiselect("Select columns to KEEP:", all_cols, default=all_cols)
            if st.button("🏁 Finalize & Trim"):
                commit_changes(finalize_report(active_df, to_keep))

        st.sidebar.divider()
        csv = active_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Export CSV", csv, f"{selected_name}_final.csv")
    else:
        st.info("👋 Welcome! Please upload files to begin.")

if __name__ == "__main__":
    main()