import pandas as pd
import streamlit as st

def change_datatypes(df):
    st.subheader("⚙️ Data Type Conversion")
    col = st.selectbox("Select column to convert:", df.columns)
    new_type = st.radio("Convert to:", ["Integer (Nullable)", "Float", "DateTime", "String/Object"])
    
    if st.button("Convert Type"):
        try:
            df = df.copy()
            if new_type == "Integer (Nullable)":
                # Convert to numeric first to handle string-decimals, then to Nullable Int64
                df[col] = pd.to_numeric(df[col], errors='coerce').round(0).astype('Int64')
            elif new_type == "Float":
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif new_type == "DateTime":
                df[col] = pd.to_datetime(df[col], errors='coerce')
            elif new_type == "String/Object":
                df[col] = df[col].astype(str)
            
            st.success(f"Converted {col} to {new_type}")
            return df
        except Exception as e:
            st.error(f"Transformation failed: {e}")
    return df