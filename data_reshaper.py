import streamlit as st
import pandas as pd

def reshape_logic(df):
    st.header("🔄 Structural Reshaping")
    
    # Using Tabs instead of Radio for a more modern navigation feel
    tab1, tab2 = st.tabs(["🚀 Melt (Wide to Long)", "📊 Pivot (Long to Wide)"])

    # --- MELT TAB ---
    with tab1:
        with st.expander("🤔 When should I use Melt?"):
            st.write("""
                Use **Melt** when you have multiple columns that should be combined into one. 
                *Example: Turning 'Jan', 'Feb', 'Mar' columns into a single 'Month' column.*
            """)
        
        col_id, col_val = st.columns(2)
        all_cols = df.columns.tolist()
        
        with col_id:
            id_vars = st.multiselect("1. Select Static Columns:", all_cols, help="These columns will repeat for every new row.")
        
        with col_val:
            remaining = [c for c in all_cols if c not in id_vars]
            value_vars = st.multiselect("2. Select Columns to Collapse:", remaining, help="These headers will become values in a new 'Metric' column.")
        
        if id_vars and value_vars:
            st.divider()
            c1, c2 = st.columns(2)
            var_name = c1.text_input("New 'Metric' Header:", value="Attribute")
            val_name = c2.text_input("New 'Value' Header:", value="Value")
            
            if st.button("🚀 Execute Melt", use_container_width=True, type="primary"):
                df_melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, 
                                    var_name=var_name, value_name=val_name)
                return df_melted

    # --- PIVOT TAB ---
    with tab2:
        with st.expander("🤔 When should I use Pivot?"):
            st.write("""
                Use **Pivot** to turn row values into column headers. 
                *Example: Turning a 'City' column with values 'Paris', 'London' into two separate columns.*
            """)

        col_p1, col_p2, col_p3 = st.columns(3)
        
        index_col = col_p1.selectbox("1. Index (Rows):", df.columns, key="piv_idx")
        columns_col = col_p2.selectbox("2. Pivot Header:", [c for c in df.columns if c != index_col], key="piv_hdr")
        values_col = col_p3.selectbox("3. Cell Values:", [c for c in df.columns if c not in [index_col, columns_col]], key="piv_val")
        
        agg_func = st.selectbox("Aggregation Method:", ["mean", "sum", "count", "max", "min"], help="How to handle multiple values for the same cell.")

        if st.button("📊 Execute Pivot", use_container_width=True, type="primary"):
            try:
                df_pivoted = df.pivot_table(index=index_col, columns=columns_col, 
                                            values=values_col, aggfunc=agg_func).reset_index()
                return df_pivoted
            except Exception as e:
                st.error(f"Pivoting failed: {e}")
                
    return df
