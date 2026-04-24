import streamlit as st
import pandas as pd

def change_datatypes(df):
    st.subheader("⚙️ Data Type Conversion")
    col = st.selectbox("Select column to convert:", df.columns)
    new_type = st.radio("Convert to:", ["int64", "float64", "datetime64[ns]", "object"])
    
    if st.button("Convert Type"):
        try:
            if new_type == "datetime64[ns]":
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].astype(new_type)
            st.success(f"Converted {col} to {new_type}")
        except Exception as e:
            st.error(f"Transformation failed: {e}")
    return df