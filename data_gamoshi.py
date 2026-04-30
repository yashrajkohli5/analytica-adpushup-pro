import pandas as pd
import io

def process_gamoshi_report(uploaded_file):
    """Splits Gamoshi report into multiple sheets within one workbook."""
    df = pd.read_excel(uploaded_file)
    
    # Metadata skip logic
    if 'Advertiser' not in df.columns:
        df = pd.read_excel(uploaded_file, skiprows=3)

    if 'Advertiser' not in df.columns:
        return None, None
    
    output = io.BytesIO()
    # Use ExcelWriter to manage multiple sheets in a single file
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Sheet 1: The full raw data
        df.to_excel(writer, sheet_name="RAW_DATA", index=False)
        
        # Subsequent Sheets: One per Advertiser
        unique_adv = df['Advertiser'].dropna().unique()
        for adv in unique_adv:
            clean_name = str(adv)[:31].strip() # Excel sheet name limit
            subset = df[df['Advertiser'] == adv]
            subset.to_excel(writer, sheet_name=clean_name, index=False)
            
    return df, output.getvalue()
