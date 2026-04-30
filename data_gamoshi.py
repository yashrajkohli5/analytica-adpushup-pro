import pandas as pd
import io

def process_gamoshi_report(uploaded_file, master_map=None):
    try:
        df = pd.read_excel(uploaded_file)
        if 'Advertiser' not in df.columns:
            df = pd.read_excel(uploaded_file, skiprows=3)

        if 'Advertiser' not in df.columns:
            return None, None
        
        # Apply mapping to the entire dataset first
        if master_map:
            site_col = 'Site' if 'Site' in df.columns else df.columns[0]
            df['Mapped_Site_ID'] = df[site_col].astype(str).str.strip().str.lower().map(master_map)
            df['Mapped_Site_ID'] = df['Mapped_Site_ID'].fillna('Nil') #
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="RAW_DATA", index=False)
            unique_adv = df['Advertiser'].dropna().unique()
            for adv in unique_adv:
                clean_name = str(adv)[:31].strip()
                subset = df[df['Advertiser'] == adv]
                subset.to_excel(writer, sheet_name=clean_name, index=False)
                
        catalog = {str(adv): df[df['Advertiser'] == adv] for adv in unique_adv}
        catalog["RAW_DATA"] = df
        return catalog, output.getvalue()
    except Exception:
        return None, None
