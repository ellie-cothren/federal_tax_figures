# Federal Tax Revenue Visualizations

## Overview 
This project provides tools to automatically download, clean, and visualize federal tax data from government sources (Office of Management and Budget, Congressional Budget Office, Tax Policy Center). 


## Project Structure
```
federal_tax_figures/
├── data/                                               # csv files of cleaned data
│   ├── avg_effective_tax_rates.csv                 
│   ├── receipts_by_source_amount_nominal.csv       
│   ├── receipts_by_source_amount_real.csv          
│   └── receipts_by_source_percent.csv              
├── figures/                                            # png files of generated figures
│   └── (generated visualizations)
├── .gitignore
├── creating_figures.py                                 # python functions to create figures
├── data_download_and_clean.py                          # python functions to download and clean data
├── federal_tax_visualization.ipynb                     # jupyter notebook to create visualization 
├── README.md
└── requirements.txt

```

## Available Visualizations

### 1. Effective Tax Rates by Income Group
**Function:** `effective_rates_chart()` 

**Data File:** `avg_effective_tax_rates.csv`

**Saved As:** `effective_rates_fy{year}.png`

Stacked bar chart showing average effective tax rates broken down by tax type (individual income, payroll, corporate, excise) for different income groups (quintiles and top percentiles). Shown for a given fiscal year.

**Sample Output:**
![Sample Visualization Effective Rates](figures/effective_rates_fy2003.png)


### 2. Sources of Federal Tax Revenue - Donut Chart
**Function:** `revenue_donut_chart()` 

**Data File:** `receipts_by_source_amount_nominal.csv` or `receipts_by_source_amount_real.csv`

**Saved As:** `revenue_donut_fy{year}.png`

Donut chart showing the share of tax revenue by source (individual income tax, corporate income tax, social insurance and retirement, excise taxes, and other) for a given fiscal year. 

**Sample Output**
![Sample Visualization Donut](figures/revenue_donut_fy2018.png)


### 3. Sources of Federal Tax Revenue - Pie Chart
**Function:** `revenue_pie_chart()`

**Data File:**  `receipts_by_source_amount_nominal.csv` or `receipts_by_source_amount_real.csv`

**Saved As:** `revenue_pie_fy{year}.png`

Pie chart showing the share of tax revenue by source (individual income tax, corporate income tax, social insurance and retirement, excise taxes, and other) for a given fiscal year. The information in this chart is the same as the information in the donut chart - they are only stylistically different.

**Sample Output**
![Sample Visualization Pie](figures/revenue_pie_fy1971.png)

### 4. Historical Revenue Share (Time Series)
**Function:** `revenue_share_hist()`

**Data File:** `receipts_by_source_percent.csv`

**Saved As:** `revenue_share_hist_start{year}.png`

Stacked area chart showing how revenue sources have evolved as percentages of total revenue. Based on time series data, given a particular starting year.

**Sample Output**
![Sample Visualization Rev Share TS](figures/revenue_share_hist_start1935.png)


### 5. Historical Revenue (Time Series)
**Function:** `revenue_hist()`

**Data File:** `receipts_by_source_amount_nominal.csv` or `receipts_by_source_amount_real.csv`

**Saved As:** `revenue_hist_{type}_start{year}.png`

Stacked area chart of total federal revenues by source in billions of dollars. Baesd on time series data given a particular starting year, can be nominal or real (adjusted for inflation)

**Sample Output:**
![Sample Visualization Rev TS](figures/revenue_hist_real_start1950.png)


## How to Use

### Installation
```bash
# clone the repository
git clone https://github.com/ellie-cothren/federal_tax_figures.git
cd federal_tax_figures

# create virtual environment
python -m venv venv
venv/Scripts/activate

# install dependencies
pip install -r requirements.txt
```

### Requirements 
```
pandas>=2.0.0
matplotlib>=3.7.0
numpy>=1.24.0
requests>=2.31.0
openpyxl>=3.1.0
jupyter>=1.0.0
```

See `requirements.txt` for full details.

### Usage

**Option 1: Run Jupyter Notebooks**

Use `federal_tax_visualization.ipynb` to download and clean data and create figures. 

You can choose the figure style, output directory, specify the fiscal year for single year plots, and specify the starting year for time series plots. These can also be set for each plot individually, if preferred. 

```python
# set style and output directory for figures 
style = 'default'
output_dir = 'figures'

# set fiscal year
fiscal_year=2018

# set time series start year (match nominal and real time series)
start_year=1950
```

**Option 2: Use Functions Directly**

Import functions and use directly

```python
import data_download_and_clean as dat

import creating_figures as fig
```



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

This project is open source and available for educational and demonstration purposes. Please feel free to use the code as a reference for your own projects.

##  Author

**Ellie Cothren**  
PhD Candidate, Economics, Indiana University  

[LinkedIn](https://linkedin.com/in/elliecothren) | [GitHub](https://github.com/ellie-cothren) | [Personal Website](www.elliecothren.com)



