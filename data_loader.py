import pandas as pd
import streamlit as st

def upload_file():
    uploaded_files = st.file_uploader(
        "Import CSV or Excel files", 
        type=['csv', 'xlsx'], 
        accept_multiple_files=True  # 👈 Enable multiple file uploads
    )
    
    # This will hold all our datasets: { "filename_or_sheetname": dataframe }
    data_catalog = {}

    if uploaded_files:
        for uploaded_file in uploaded_files:
            try:
                if uploaded_file.name.endswith('.csv'):
                    data_catalog[uploaded_file.name] = pd.read_csv(uploaded_file)
                
                else:
                    # For Excel, we extract EVERY sheet automatically
                    excel_file = pd.ExcelFile(uploaded_file)
                    for sheet_name in excel_file.sheet_names:
                        # Create a unique name: "Filename - SheetName"
                        unique_name = f"{uploaded_file.name} ({sheet_name})"
                        data_catalog[unique_name] = pd.read_excel(uploaded_file, sheet_name=sheet_name)
                        
            except Exception as e:
                st.error(f"Error loading {uploaded_file.name}: {e}")
        
        return data_catalog if data_catalog else None
            
    return None