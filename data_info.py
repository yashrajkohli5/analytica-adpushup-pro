import streamlit as st

def show_basic_info(df):
    st.subheader("📊 Data Preview")
    st.dataframe(df.head())
    st.write("**Current Shape:**", df.shape)

def get_null_report(df):
    null_counts = df.isnull().sum()
    null_df = null_counts[null_counts > 0]
    
    if not null_df.empty:
        st.subheader("🔍 Missing Data Report")
        st.table(null_df)
        return null_df.index.tolist()
    return []