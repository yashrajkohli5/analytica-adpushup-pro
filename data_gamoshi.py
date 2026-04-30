import pandas as pd
import io

def process_gamoshi_report(uploaded_file, master_map=None):
    """
    Processes Gamoshi report and applies Site ID mapping to all rows 
    before splitting into sheets.
    """
    df = pd.read_excel(uploaded_file)
    
    # Metadata skip logic
    if 'Advertiser' not in df.columns:
        df = pd.read_excel(uploaded_file, skiprows=3)

    if 'Advertiser' not in df.columns:
        return None, None
    
    # Apply Mapping to the entire dataframe at once if map is provided
    if master_map:
        # Standardize site names for matching
        match_col = 'Site' if 'Site' in df.columns else df.columns[0]
        df['Mapped_Site_ID'] = df[match_col].astype(str).str.strip().str.lower().map(master_map)
        df['Mapped_Site_ID'] = df['Mapped_Site_ID'].fillna('Nil')
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Save the fully mapped master sheet
        df.to_excel(writer, sheet_name="RAW_DATA", index=False)
        
        # Split into mapped advertiser sheets
        unique_adv = df['Advertiser'].dropna().unique()
        for adv in unique_adv:
            clean_name = str(adv)[:31].strip()
            subset = df[df['Advertiser'] == adv]
            subset.to_excel(writer, sheet_name=clean_name, index=False)
            
    return df, output.getvalue()
