import streamlit as st
import pandas as pd

def create_pivot_table(df):
    st.header("📊 Pivot Table Summary")
    # st.info("Summaries created here are stored in memory and won't affect your raw data.")

    # 1. Configuration UI
    col1, col2 = st.columns(2)
    with col1:
        rows = st.multiselect("Rows (Index):", df.columns, key="piv_row_multi")
        cols = st.multiselect("Columns:", [c for c in df.columns if c not in rows], key="piv_col_multi")
    
    with col2:
        values = st.multiselect("Values to Aggregate:", 
                                 [c for c in df.columns if c not in rows + cols], key="piv_val_multi")
        agg_func = st.selectbox("Aggregation Method:", 
                                 ["sum", "mean", "count", "min", "max"], key="piv_agg_sel")

    # 2. Generation Logic
    if st.button("Generate Summary Report", type="primary"):
        if not rows or not values:
            st.warning("Please select at least one Row and one Value column.")
        else:
            try:
                # Store the result in session_state instead of a local variable
                st.session_state.current_pivot = df.pivot_table(
                    index=rows, 
                    columns=cols if cols else None, 
                    values=values, 
                    aggfunc=agg_func
                )
                st.success("Summary Generated!")
            except Exception as e:
                st.error(f"Could not generate pivot table: {e}")

    # 3. Persistent Display Logic
    # This block ensures the table stays visible even after switching tabs
    if "current_pivot" in st.session_state:
        st.divider()
        st.subheader("📋 Last Generated Summary")
        st.dataframe(st.session_state.current_pivot, use_container_width=True)
        
        # Persistent Download Button
        csv_summary = st.session_state.current_pivot.to_csv().encode('utf-8')
        st.download_button(
            label="📥 Download This Pivot Table (CSV)",
            data=csv_summary,
            file_name="pivot_summary_report.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        if st.button("🗑️ Clear Summary"):
            del st.session_state.current_pivot
            st.rerun()