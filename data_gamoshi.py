import pandas as pd
import io

def process_gamoshi_report(uploaded_file, master_map=None):
    """
    Processes Gamoshi report, applies mapping globally, 
    and returns a single multi-sheet workbook.
    """
    try:
        df = pd.read_excel(uploaded_file)
        
        if 'Advertiser' not in df.columns:
            df = pd.read_excel(uploaded_file, skiprows=3)

        if 'Advertiser' not in df.columns:
            return None, None
        
        # Global Mapping: Apply to all rows before splitting
        if master_map:
            match_col = 'Site' if 'Site' in df.columns else df.columns[0]
            df['Mapped_Site_ID'] = df[match_col].astype(str).str.strip().str.lower().map(master_map)
            df['Mapped_Site_ID'] = df['Mapped_Site_ID'].fillna('Nil') #
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Sheet 1: Master data
            df.to_excel(writer, sheet_name="RAW_DATA", index=False)
            
            # Subsequent Sheets: Advertiser-specific
            unique_adv = df['Advertiser'].dropna().unique()
            for adv in unique_adv:
                clean_name = str(adv)[:31].strip()
                subset = df[df['Advertiser'] == adv]
                subset.to_excel(writer, sheet_name=clean_name, index=False)
                
        # Return a dictionary for the catalog and the bytes for download
        catalog = {str(adv): df[df['Advertiser'] == adv] for adv in unique_adv}
        catalog["RAW_DATA"] = df
        
        return catalog, output.getvalue()
    except Exception:
        return None, None
