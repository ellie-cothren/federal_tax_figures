# Federal Tax Revenue Visualizations - Streamlit Dashboard

## Overview 
This project provides tools to automatically download, clean, and visualize federal tax data from government sources (Office of Management and Budget, Congressional Budget Office, Tax Policy Center). 


## Project Structure
'''
federal-tax-dashboard/
├── app.py                  # Streamlit dashboard (main entry point)
├── src/
│   ├── data_pipeline.py    # Download, clean, and cache all datasets
│   └── charts.py           # Plotly chart functions
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
├── requirements.txt
└── README.md
'''




## How to Use

View [Dashboard App](https://federaltaxfigures-jq9vcwbvxmvdbwf2phzzx7.streamlit.app/)

Or see directions below for running locally

### Prerequisites
- Python 3.10+

(see requirements.txt for all requirements)

### Installation
 
```bash
git clone https://github.com/ellie-cothren/federal-tax-figures.git
cd federal-tax-figures
pip install -r requirements.txt
```
 
### Run Locally
 
```bash
streamlit run app.py
```
 
On first run, it downloads and caches data from OMB, TPC, and FRED (takes ~10–15 seconds)


## Data Sources

| Dataset | Source | Years | Description |
|---------|--------|-------|-------------|
| Effective Tax Rates | [Tax Policy Center](https://www.taxpolicycenter.org/statistics/historical-average-federal-tax-rates-all-households) | 1979-2020 | Average rates by income group & tax type |
| Revenue by Source (Amounts) | [OMB Historical Tables 2.1](https://www.whitehouse.gov/omb/budget/historical-tables/) | 1934-2024 | Revenue in millions USD |
| Revenue by Source (%) | [OMB Historical Tables 2.2](https://www.whitehouse.gov/omb/budget/historical-tables/) | 1934-2024 | Revenue as % of total |
Consumer Price Index | [FRED Series CPIAUCSL](https://fred.stlouisfed.org/series/CPIAUCSL) | 1947-2025 | Consumer Price Index, all items

**Original sources:**
- Office of Management and Budget (OMB) - Budget Historical Tables
- Tax Policy Center - Reformatted data from CBO publications
    - Supplemental data for a Congressional Budget Office (CBO) specific report from November 2022, *The Distribution of Household Income, 2019* [linked here](www.cbo.gov/publication/58353)
- Bureau of Labor Statistics (BLS) - CPI data used to adjust tax revenue amount for inflation 

Note: Government URLs may change when new fiscal year budgets are released. Check error messages for updated links.

##  License

MIT License

##  Author

**Ellie Cothren**  
Data Scientist


PhD Candidate, Economics, Indiana University  

[LinkedIn](https://linkedin.com/in/elliecothren) | [GitHub](https://github.com/ellie-cothren) | [Personal Website](www.elliecothren.com)



