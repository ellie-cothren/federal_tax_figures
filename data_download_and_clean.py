# functions download and clean three datasets: (1) average effective tax rate by income group, (2) receipts by source amount, and (3) receipts by source percentage/share

# import necessary package
import pandas as pd
import requests
from io import BytesIO
from io import StringIO
import re
import os


# downloads OMB tables (receipts by source amount/percent) directly from OMB website - defaults to 2026 budget year
# returns dict with a df for each 
def download_omb_tables(budget_year=2026):
    
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
    
    # store Table 2.1 and Table 2.2 
    tables = {}

    # read Table 2.1: Receipts by Source Amount
    try: 
        excel_file = BytesIO(response.content)
        df_2_1 = pd.read_excel(
            excel_file,
            sheet_name='hist02z1',
            skiprows=2,
            header=[0,1]
        )
        print(f"Successfully loaded Table 2.1")
        print(f"Shape: {df_2_1.shape}")

        tables['table_2_1'] = df_2_1

    except Exception as e:
        print(f"Error reading Table 2.1: {e}")
        tables['table_2_1'] = None

    # read Table 2.2: Receipts by Source Percentage
    try:
        excel_file = BytesIO(response.content)
        df_2_2 = pd.read_excel(
            excel_file,
            sheet_name='hist02z2',
            skiprows=1,
            header=[0,1]
        )
        print(f"Successfully loaded Table 2.2")
        print(f"Shape: {df_2_2.shape}")
        tables['table_2_2'] = df_2_2

    except Exception as e:
        print(f"Error reading Table 2.2: {e}")
        tables['table_2_2'] = None

    return tables








# downloads data from CBO report on effective tax rates for different income groups
# downloads from Tax Policy Center (TPC) where supplementary data from the report is more readily available
# returns df
def download_tpc_table():
    
    # download from url
    url = "https://taxpolicycenter.org/sites/default/files/statistics/spreadsheet/average_rate_historical_all_5.xlsx"
    
    print("Downloading Tax Policy Center effective tax rates...")
    print(f"URL: {url}")

    # Add headers for User-Agent to mimic a browser request
    #headers = {
    #    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    #}

    try: 
        response = requests.get(url, timeout=30)
        response.raise_for_status()

    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        print("Check for updated data at: https.//www.cbo.gov/topics/taxes")
        return None
    
    # convert to df
    try: 
        excel_file = BytesIO(response.content)
        df = pd.read_excel(
            excel_file,
            sheet_name='Summary',
            header=None
        )

        print(f"Loaded Federal Tax Rate data")
        print(f"Shape: {df.shape}")

        return df

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None
    





# downloads CPI data directly from FRED (which is taken from BLS) to deflate revenue by source amount (get data in real terms rather than nominal) and calcuates an annual average
# includes cleaning - removes NaN (specifically, handles missing data from Oct-2025 due to government shutdown)
def download_cpi_data():

    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"

    print("Downloading CPI from FRED...")

    try: 
        df = pd.read_csv(url)

        df['observation_date'] = pd.to_datetime(df['observation_date'])
        df['Year'] = df['observation_date'].dt.year

        # remove missing values
        df = df.dropna(subset=['CPIAUCSL'])

        # calculate annual average from available months
        df_cpi = df.groupby('Year')['CPIAUCSL'].mean().reset_index()
        df_cpi.columns = ['Year', 'CPI']
        df_cpi = df_cpi.sort_values('Year').reset_index(drop=True)

        print(f"Downloaded CPI data for years {int(df_cpi['Year'].min())} - {int(df_cpi['Year'].max())}")

        return df_cpi
    
    except Exception as e:
        print(f"Error downloading data from FRED: {e}")
        return None
        

        



# saves df to specified data folder 
def save_data_csv(df, file_name):

    # create data folder (if it doesn't already exist)
    os.makedirs('data', exist_ok=True)

    # create output path with given file name
    output_path = f'data/{file_name}.csv'

    # save df to csv 
    df.to_csv(output_path, index=False)

    print(f"Saved cleaned data to {output_path}")







# cleans df from OMB download - removes NaN rows/columns, deals with multi-level headers, adjusts header names
# returns clean df
def clean_omb_dataframe(df): 

    print("\nCleaning data...")

    # drop rows that are all NaN
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

    print(f"Cleaned df shape: {df_clean.shape}")
    print(f"Columns in cleaned df: {list(df_clean.columns)}")

    print(f"Years: {df_clean['Fiscal Year'].min()} to {df_clean['Fiscal Year'].max()}")

    

    return df_clean









# cleans df from TPC download - removes NaN rows/columns, deals with multiple data sections organized by tax-type
# returns cleaned df
def clean_tpc_dataframe(df):

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
    
    print(f"\nCleaned data shape: {df_clean.shape}")
    print(f"Years: {df_clean['Year'].min()} to {df_clean['Year'].max()}")
    print(f"Tax Types: {df_clean['Tax Type'].unique().tolist()}")


    return df_clean








# adjusts nominal data for inflation for a given year 
def adjust_for_inflation(df, adj_year):

    # download CPI data
    df_cpi = download_cpi_data()

    if df_cpi is None:
        print("Error: Could not download CPI data")
        return df
    
    # check CPI data range
    cpi_min_year = int(df_cpi['Year'].min())
    cpi_max_year = int(df_cpi['Year'].max())
    print(f"CPI data available from {cpi_min_year} to {cpi_max_year}")

    # merge CPI with revenue data (only keeping years that have CPI )
    df_merged = df.merge(
        df_cpi,
        left_on='Fiscal Year',
        right_on = 'Year',
        how='inner'
    )

    original_years = len(df)
    adjusted_years = len(df_merged)
    dropped_years = original_years - adjusted_years

    if dropped_years > 0:
        print(f"Dropped {dropped_years} years withouth CPI data")

    if adj_year not in df_cpi['Year'].values:
        print(f"Warning: adjsutement year {adj_year} is not available in CPI data. Defaulting to adjust year of 2017.")
        adj_year = 2017

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

    print(f"Created inflation adjusted df with all values in {adj_year} dollars.")
    print(f"Years included: {int(df_real['Fiscal Year'].min())} - {int(df_real['Fiscal Year'].max())}")

    return df_real

    

