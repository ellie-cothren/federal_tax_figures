"""
Data pipeline for downloading, cleaning, and caching federal tax data

Sources:
    - OMB Historical Tables (Tables 2.1, 2.2): Receipts by source (amount/level and percent/share)
    - CBO/TPC: Average effective federal tax rates by income group
    - FRED/BLS: CPI data for inflation adjustment
"""

import pandas as pd
import requests
from io import BytesIO
from io import StringIO
import re
import os
import streamlit as st


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')

#--------------------------------------------------------------------------------
# Download Functions
#--------------------------------------------------------------------------------

@st.chache_data(ttl=86400, show_spinner='Downloading OMB data...')
def download_omb_tables(budget_year: int=2026) -> tuple[pd.DataFrame, pd.DataFrame]:
    
    # Download OMB Historical Tables 2.1 and 2.2

    # url for download
    url = f"https://www.whitehouse.gov/wp-content/uploads/{budget_year-1}/06/BUDGET-{budget_year}-HIST.xlsx"

    print(f"Downloading OMB Historical Tables for FY{budget_year}...")
    print(f"URL: {url}")

    try: 
        response = requests.get(url, timeout=30)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        print(f"The URL may have changed. Check https://www.whitehouse.gov/omb/budget/historical-tables/")
        return None
    

    excel_bytes = BytesIO(response.content)

    table_2_1 = pd.read_excel(
        excel_bytes, 
        sheet_name='hist02z1',
        skiprows=2,
        header=[0,1]
    )

    excel_bytes.seek(0)

    table_2_2 = pd.read_excel(
        excel_bytes,
        sheet_name='hist02z2',
        skiprows=2,
        header=[0,1]
    )

    return table_2_1, table_2_2
    


@st.cahce_data(ttl=86400, show_spinner='Downloading effective tax rate data...')
def download_tpc_table() -> pd.DataFrame:
    
    # Download Tax Policy Center effective tax rate data

    # download from url
    url = "https://taxpolicycenter.org/sites/default/files/statistics/spreadsheet/average_rate_historical_all_5.xlsx"
    
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    df_tpc_data = pd.read_excel(
        BytesIO(response.content),
        sheet_name='Summary',
        header=None
    )

    return df_tpc_data
    


@st.cache_data(ttl=86400, show_spinner='Downloading CPI data...')
def download_cpi_data() -> pd.DataFrame:

    # Download CPI data, handle missing data (Oct-2025 duge to government shutdown)

    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"

    print("Downloading CPI from FRED...")

    df = pd.read_csv(url)

    df['observation_date'] = pd.to_datetime(df['observation_date'])
    df['Year'] = df['observation_date'].dt.year

    # remove missing values
    df = df.dropna(subset=['CPIAUCSL'])

    # calculate annual average from available months
    df_cpi = df.groupby('Year')['CPIAUCSL'].mean().reset_index()
    df_cpi.columns = ['Year', 'CPI']
    df_cpi = df_cpi.sort_values('Year').reset_index(drop=True)

    return df_cpi
    



#-----------------------------------------------------------------------------------------
# Cleaning Helper Functions
#-----------------------------------------------------------------------------------------


def clean_omb_dataframe(df: pd.DataFrame) -> pd.DataFrame: 

    # Clean raw OMB tables: flatten headers, fix column names, drop footnotes

    df_clean = df.dropna(how='all')

    # drop columns that are all NaN
    df_clean = df_clean.dropna(axis=1, how='all')

    # flatten multi-level columns: break levels into level_0 (header) and level_1 (sub-header)
    # if level_1 is unnamed, label using only level_0
    # if there is a level_0 and level_1, combine with a space and remove parenthese
    new_columns = []
    for col in df_clean.columns: 
        level_0 = col[0]    # first part
        level_1 = col[1]    # second part

        if 'Unnamed' in level_1:
            new_columns.append(level_0)
        else:
            combined = f"{level_0} {level_1}"
            combined = combined.replace('(', '').replace(')', '')
            new_columns.append(combined)

    df_clean.columns = new_columns 
    
    df_clean.columns = df_clean.columns.str.strip()

    # remove footnote numbers (1), (2), etc. from column names
    df_clean.columns = [re.sub(r'\s*\(\d+\)', '', col) for col in df_clean.columns]

    # remove any standalone numbers leftover
    df_clean.columns = [re.sub(r'\s+\d+\s+', ' ', col).strip() for col in df_clean.columns]

    # remove rows where fiscal year is NaN (i.e. remove footnotes)
    df_clean['Fiscal Year'] = pd.to_numeric(df_clean['Fiscal Year'], errors='coerce')
    df_clean = df_clean.dropna(subset=['Fiscal Year'])

    # convert fiscal year to integer
    df_clean['Fiscal Year'] = df_clean['Fiscal Year'].astype(int)
    
    return df_clean




def clean_tpc_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    # Clean TPC effective tax rate: parse sections by tax type

    # get column headers from row 4
    headers = df.iloc[4].tolist()

    # find all section headers
    section_starts = []
    for i in range(len(df)):
        cell_value = str(df.iloc[i,0])
        if 'Tax Rate (percent)' in cell_value:
            section_starts.append(i)

    # extract each section 
    all_sections = []

    for idx, start_row in enumerate(section_starts):
        section_name = df.iloc[start_row,0]

        data_start = start_row + 1

        if idx < len(section_starts) -1:
            data_end = section_starts[idx+1] -1
        else:
            data_end = len(df)

        # extract each section's data
        section_df = df.iloc[data_start:data_end].copy()
        section_df.columns = headers

        # drop blank rows (all NaN)
        section_df = section_df.dropna(how='all')

        # drop black columns
        section_df = section_df.dropna(axis=1, how='all')

        # only keep rows with valid years
        section_df['Year'] = pd.to_numeric(section_df['Year'], errors='coerce')
        section_df = section_df.dropna(subset=['Year'])

        if len(section_df) > 0:
            section_df['Tax Type'] = section_name.replace(' (percent)', '').replace('Average ', '')
            all_sections.append(section_df)

    # combine all sections
    df_clean = pd.concat(all_sections, ignore_index=True)

    df_clean['Year'] = df_clean['Year'].astype(int)

    for col in df_clean.columns:
        if col not in ['Year', 'Tax Type']:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')

    # clean up column names (remove excess spaces)
    df_clean.columns = df_clean.columns.str.strip()
    df_clean.columns = df_clean.columns.str.replace(r'\s+', ' ', regex=True)
    

    return df_clean





def adjust_for_inflation(df: pd.DataFrame, adj_year: int=2017) -> pd.DataFrame:

    # Adjust nominal data for inflation for a given year (convert nominal revenue to real revenue using CPI data) 

    # download CPI data
    df_cpi = download_cpi_data()

    if adj_year not in df_cpi['Year'].values:
        adj_year=2017

    # merge CPI with revenue data (only keeping years that have CPI data)
    df_merged = df.merge(df_cpi, left_on='Fiscal Year', right_on = 'Year', how='inner')

    # calcualte inflation adjustment factor
    adj_year_cpi = df_cpi[df_cpi['Year'] == adj_year]['CPI'].values[0]

    df_merged['Inflation_Factor'] = adj_year_cpi / df_merged['CPI']

    # revenue columns to adjust
    revenue_cols = [
        'Individual Income Taxes',
        'Corporation Income Taxes',
        'Social Insurance and Retirement Receipts Total',
        'Social Insurance and Retirement Receipts On - Budget',
        'Social Insurance and Retirement Receipts Off - Budget',
        'Excise Taxes',
        'Other',
        'Total Receipts Total',
        'Total Receipts On - Budget',
        'Total Receipts Off - Budget'
    ]

    # create new inflation adjusted df
    df_real = df_merged[['Fiscal Year']].copy()

    for col in revenue_cols:
        if col in df_merged.columns:
            df_real[col] = df_merged[col] * df_merged['Inflation_Factor']


    return df_real

    
#--------------------------------------------------------------------------
# Main Data Load/Clean Function (called once and cached in Streamlit)
#--------------------------------------------------------------------------

def load_all_data() -> dict:
    """
    Download, clean, and return all datasets as a dict of DataFrames

    Return dict with keys:
        - receipts_nominal: OMB Table 2.1 (millions USD, nominal)
        - receipts_real: OMB Table 2.1 (millions of 2017 USD)
        - receipts_pct: OMB Table 2.2 (percent/share of total)
        -effective_rates: TPC effective tax rates by income group
    """

    # OMB Tables
    table_2_1, table_2_2 = download_omb_tables()
    receipts_nominal = clean_omb_dataframe(table_2_1)
    receipts_pct = clean_omb_dataframe(table_2_2)
    receipts_real = adjust_for_inflation(receipts_nominal, adj_year=2017)

    # Effective tax rates (TPC)
    tpc_raw = download_tpc_table()
    effective_rates = clean_tpc_dataframe(tpc_raw)

    dict = {
        'receipts_nominal': receipts_nominal,
        'receipts_real': receipts_real,
        'receipts_pct': receipts_pct,
        'effective_rates': effective_rates
    }

    return dict
