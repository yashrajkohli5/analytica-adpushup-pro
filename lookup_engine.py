import pandas as pd

def build_master_mapping(lookup_df):
    """
    Iterates through AB, DE, GH, JK pairs to create a unique mapping.
    First-in-wins logic ensures unique domain-to-ID assignment.
    """
    master_map = {}
    # A:0, B:1 | D:3, E:4 | G:6, H:7 | J:9, K:10
    pairs = [(0, 1), (3, 4), (6, 7), (9, 10)]
    
    for dom_idx, id_idx in pairs:
        if dom_idx < len(lookup_df.columns) and id_idx < len(lookup_df.columns):
            current_pair = lookup_df.iloc[:, [dom_idx, id_idx]].dropna()
            
            for _, row in current_pair.iterrows():
                domain = str(row.iloc[0]).strip().lower()
                site_id = str(row.iloc[1]).strip()
                
                # Check for uniqueness before mapping
                if domain and domain not in master_map:
                    master_map[domain] = site_id
                    
    return master_map

def apply_master_lookup(df, target_col, master_map):
    """
    Applies the master map to the active report. 
    Unmapped rows are marked as 'Nil'.
    """
    df = df.copy()
    # Map the IDs and immediately fill missing values with 'Nil'
    df['Mapped_Site_ID'] = df[target_col].astype(str).str.strip().str.lower().map(master_map)
    df['Mapped_Site_ID'] = df['Mapped_Site_ID'].fillna('Nil')
    return df
