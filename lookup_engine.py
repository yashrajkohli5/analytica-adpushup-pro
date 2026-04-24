import pandas as pd
import streamlit as st

def build_master_mapping(lookup_df):
    """
    Iterates through AB, DE, GH, JK pairs to create a unique mapping.
    Domain is the Key, Site ID is the Value.
    """
    master_map = {}
    
    # Define the pairs based on your column letters (0-indexed)
    # A:0, B:1 | D:3, E:4 | G:6, H:7 | J:9, K:10
    pairs = [(0, 1), (3, 4), (6, 7), (9, 10)]
    
    for dom_idx, id_idx in pairs:
        if dom_idx < len(lookup_df.columns) and id_idx < len(lookup_df.columns):
            # Extract the pair and drop empty rows
            current_pair = lookup_df.iloc[:, [dom_idx, id_idx]].dropna()
            
            for _, row in current_pair.iterrows():
                domain = str(row.iloc[0]).strip().lower()
                site_id = str(row.iloc[1]).strip()
                
                # UNIQUE CONSTRAINT: Only map if domain isn't already in the map
                if domain and domain not in master_map:
                    master_map[domain] = site_id
                    
    return master_map

def apply_master_lookup(df, site_col, master_map):
    """Applies the master map to the active dataframe."""
    df = df.copy()
    # Create the new Site ID column based on the domain column
    df['Mapped_Site_ID'] = df[site_col].astype(str).str.strip().str.lower().map(master_map)
    return df