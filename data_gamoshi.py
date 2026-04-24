import pandas as pd
import streamlit as st
import io

def process_gamoshi_report(uploaded_file):
    """
    Reads Gamoshi Excel, splits by Advertiser.
    - RAW_DATA sheet: All columns.
    - Advertiser sheets: Only 'Inventory' and 'Gross Spend' columns.
    """
    try:
        # 1. Read the Excel file
        df = pd.read_excel(uploaded_file)
        
        # Metadata skip logic (if 'Advertiser' is not in the first row)
        if 'Advertiser' not in df.columns:
            df = pd.read_excel(uploaded_file, skiprows=3)

        if 'Advertiser' not in df.columns:
            st.warning("Advertiser column missing. Please check the file structure.")
            return None, None
        
        # Define the columns required for the split sheets
        # We include 'Advertiser' so we can actually filter the rows
        target_columns = ['Advertiser', 'Inventory', 'Gross Spend']
        
        # Verify columns exist to prevent crashes
        available_cols = [col for col in target_columns if col in df.columns]
        
        gamoshi_catalog = {}
        # Raw Data in catalog (Full View)
        gamoshi_catalog["GAMOSHI: RAW_DATA"] = df
        
        unique_adv = df['Advertiser'].dropna().unique()
        
        # 2. Create the Multi-Sheet Workbook
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            
            # --- SHEET 1: RAW DATA (All Columns) ---
            df.to_excel(writer, sheet_name="RAW_DATA", index=False)
            
            # 3. Loop for Advertiser Sheets (Filtered Columns)
            for adv in unique_adv:
                clean_name = str(adv)[:31].strip().replace("[", "").replace("]", "")
                
                # Filter rows by Advertiser AND filter columns by target list
                subset = df[df['Advertiser'] == adv][available_cols].reset_index(drop=True)
                
                # Add to Analytica Catalog
                gamoshi_catalog[f"GAMOSHI: {clean_name}"] = subset
                
                # Add to Workbook
                subset.to_excel(writer, sheet_name=clean_name, index=False)
        
        return gamoshi_catalog, output.getvalue()

    except Exception as e:
        st.error(f"Gamoshi Excel Error: {e}")
        return None, None
