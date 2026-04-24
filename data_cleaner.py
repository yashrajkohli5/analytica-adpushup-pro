import pandas as pd
import streamlit as st

def clean_url_manually(df, column):
    """Manually standardizes URLs by removing protocols, www, and sub-paths."""
    df = df.copy()
    # Handle NaNs and convert to string
    df[column] = df[column].astype(str).replace('nan', '').str.lower().str.strip()
    
    # Remove http, https, and www prefix
    df[column] = df[column].str.replace(r'^https?://', '', regex=True)
    df[column] = df[column].str.replace(r'^www\.', '', regex=True)
    
    # Extract root domain only
    df[column] = df[column].str.split('/').str[0]
    return df

def apply_precision_manually(df, columns):
    """Manually rounds specific numeric columns to 2 decimal places."""
    df = df.copy()
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].round(2)
    return df

def apply_institutional_logic(df, site_col, email_col, id_col=None):
    """Step 1 & 2: Removals and Correct Mappings ONLY."""
    df = df.copy()
    emails = df[email_col].astype(str).str.lower().str.strip()
    domains = df[site_col].astype(str).str.lower().str.strip()
    
    # --- STEP 1: REMOVALS ---
    whitelist = ['wifty.ai@adpushup.com', 'ti-tech.ai@adpushup.com']
    mask_adpushup = emails.str.endswith('@adpushup.com') & (~emails.isin(whitelist))
    
    bad_pairs = [('ndtv.com', 'sanjay.nagpal@aajtak.com'), ('andhrajyoti', 'jyothy@magzian.com')]
    mask_pairs = pd.Series(False, index=df.index)
    for dom, eml in bad_pairs:
        mask_pairs |= (domains.str.contains(dom, na=False)) & (emails == eml)
        
    mask_id = pd.Series(False, index=df.index)
    if id_col and id_col in df.columns:
        mask_id = (df[id_col].astype(str) == '37902') & (domains.str.contains('theconstructor.org', na=False))

    mask_junk = emails.str.contains('@mailinator|@adushup|@inuxu', na=False)
    df = df[~(mask_adpushup | mask_pairs | mask_id | mask_junk)].reset_index(drop=True)

    # --- STEP 2: CORRECT MAPPINGS ---
    mapping_rules = {
        "freightwaves.com": "sfchronicle@instaread.com", "missyusa.com": "james@mediafix.us",
        "dramabeans.com": "james@mediafix.us", "style.ca": "evan.leftwich@buzzworthy.com",
        "randomwordgenerator": "contact@papayads.net", "washingtonian": "sfchronicle@instaread.com",
        "golf.com": "sfchronicle@instaread.com", "steelernation.com": "sfchronicle@instaread.com",
        "fantasypros.com": "sfchronicle@instaread.com", "hindutamil.in": "kamadenutamil@gmail.com",
        "bangla.hindustantimes.com": "bushra.parvez@htdigital.in", "healthshots.com": "bushra.parvez@htdigital.in",
        "khaleejtimes.com": "programmatic@khaleejtimes.ae", "allmusic.com": "george@bandsintown.com",
        "allmovie.com": "george@bandsintown.com", "ottplay.com": "bushra.parvez@htdigital.in",
        "sidereel.com": "george@bandsintown.com", "lfi": "gamadpushup@lfi-media.nl",
        "firstcry": "suraj.dhakne@firstcry.com", "shaala": "anthony@shaala.com",
        "pinkvilla": "sanket.vora@pinkvilla.com", "worldjournal.com": "ti-tech.ai@adpushup.com",
        "theprint.in": "theprint.mamcm@gmail.com"
    }
    for site, email in mapping_rules.items():
        df.loc[df[site_col].str.contains(site, case=False, na=False), email_col] = email

    # Network Logic
    df.loc[df[site_col].str.contains('tv9|news9live', case=False, na=False), email_col] = 'tv9@adpushup.com'
    df.loc[df[site_col].str.contains('abpnetwork|abp', case=False, na=False), email_col] = 'anupam@adpushup.com'
    df.loc[df[site_col].str.contains('jagran', case=False, na=False), email_col] = 'adtech@jagrannewmedia.com'
    df.loc[df[site_col].str.contains('udn', case=False, na=False), email_col] = 'udn@adpushup.com'

    return df

def finalize_report(df, cols_to_keep):
    """Step 3: Column trimming only."""
    df = df.copy()
    return df[[c for c in cols_to_keep if c in df.columns]]