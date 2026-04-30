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

    # 1. IMPORT & MAPPING SETUP
    with st.expander("📂 Import Center", expanded=True):
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("### 1. Setup Global Mapping (Optional)")
            # Uploading mapping here allows Gamoshi to map all sheets at once
            map_file_setup = st.file_uploader("Upload Master Map (AB, DE, GH, JK)", type=['xlsx'], key="global_map")
            master_dict = None
            if map_file_setup:
                lookup_df_setup = pd.read_excel(map_file_setup)
                master_dict = build_master_mapping(lookup_df_setup)
                st.success(f"✅ Master Map Loaded ({len(master_dict)} domains)")

            st.divider()
            st.markdown("### 2. Standard Upload")
            new_data = upload_file()
            if new_data:
                for name, df in new_data.items():
                    if name not in st.session_state.catalog:
                        st.session_state.catalog[name] = {"df": df}
                        
        with c2:
            st.markdown("### 3. Gamoshi Specialized Workflow")
            g_file = st.file_uploader("Gamoshi Excel", type=['xlsx'], key="gamoshi_up")
            if g_file:
                # pass master_dict to process all advertiser sheets at once
                g_cat, g_book_bytes = process_gamoshi_report(g_file, master_map=master_dict)
                if g_cat:
                    for name, df in g_cat.items():
                        if name not in st.session_state.catalog:
                            st.session_state.catalog[name] = {"df": df}
                    st.download_button("📥 Download Mapped Workbook", data=g_book_bytes, file_name="Gamoshi_Mapped_Report.xlsx")

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
            
            t_col = st.selectbox("Select Column to Clean (URL):", active_df.columns)
            if st.button("🔗 Clean URLs Now"):
                commit_changes(clean_url_manually(active_df, t_col))
            
            st.divider()
            
            num_cols = active_df.select_dtypes(include=['number']).columns.tolist()
            prec_cols = st.multiselect("Select columns for 2-Decimal Precision:", num_cols)
            if st.button("💎 Apply Rounding Now"):
                commit_changes(apply_precision_manually(active_df, prec_cols))

            st.divider()

            st.subheader("🗺️ Manual Site ID Mapping")
            st.info("Upload the workbook containing column pairs: AB, DE, GH, and JK.")
            map_file = st.file_uploader("Upload Master Mapping Workbook", type=['xlsx'], key="manual_map_file")
            
            if map_file:
                lookup_df = pd.read_excel(map_file)
                match_col = st.selectbox("Match IDs using this column (Domain):", active_df.columns)
                
                if st.button("🗺️ Execute Master Mapping"):
                    m_dict = build_master_mapping(lookup_df)
                    # apply_master_lookup now fills unmatched rows with 'Nil'
                    mapped_df = apply_master_lookup(active_df, match_col, m_dict)
                    commit_changes(mapped_df)
                    st.success(f"Mapping complete. Unmatched rows marked as 'Nil'.")

        elif menu == "3. Type Conversion":
            st.header("Step 3: Change Column Types")
            # Fixed: handles Nullable Integer (Int64) for NaN support
            transformed_df = change_datatypes(active_df)
            if transformed_df is not None and not transformed_df.equals(active_df):
                commit_changes(transformed_df)

        elif menu == "4. Column Finalizer":
            st.header("Step 4: Trim Columns")
            all_cols = active_df.columns.tolist()
            to_keep = st.multiselect("Select columns to KEEP:", all_cols, default=all_cols)
            if st.button("🏁 Finalize & Trim"):
                commit_changes(finalize_report(active_df, to_keep))

        # --- EXPORT SECTION ---
        st.sidebar.divider()
        st.sidebar.header("📥 Export Settings")
        file_name_input = st.sidebar.text_input("Export Filename:", value=f"cleaned_{selected_name.split('.')[0]}")
        
        csv = active_df.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button("📥 Export CSV", csv, f"{file_name_input}.csv", "text/csv")
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            active_df.to_excel(writer, index=False)
        st.sidebar.download_button("📊 Export Excel", buffer.getvalue(), f"{file_name_input}.xlsx")

    else:
        st.info("👋 Welcome! Please upload files to begin.")

if __name__ == "__main__":
    main()
