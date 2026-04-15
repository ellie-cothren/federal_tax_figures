"""
U.S. Federal Tax Dashboard

Interactive dashboard exploring federal tax revenue and effective rates using data from OMB, CBO/TPC, and FRED
"""

import streamlit as st
import numpy as np


st.set_page_config(
    page_title='U.S. Federal Tax Dashboard',
    layout='wide',
    initial_sidebar_state='expanded'
)

#---------------------------------------------------------------------
# Imports (after page config)
#---------------------------------------------------------------------

from src.data_pipeline import load_all_data
from src.charts import(
    effective_rates_chart,
    revenue_pie_chart,
    revenue_share_history,
    revenue_history,
    effective_rates_over_time
)


#--------------------------------------------------------------------
# Load data, chached (only download once per session day)
#--------------------------------------------------------------------

data = load_all_data()

receipts_nom = data['receipts_nominal']
receipts_real = data['receipts_real']
receipts_pct = data['receipts_real']
eff_rates = data['effective_rates']

# year ranges
eff_rate_years = sorted(eff_rates['Year'].unique())
revenue_years = sorted(receipts_nom['Fiscal Year'].unique())


#--------------------------------------------------------------------
# Sidebar
#--------------------------------------------------------------------

with st.sidebar:
    st.markdown('## Federal Tax Dashboard')
    st.caption('Explore U.S. federal tax revenue sources and effective tax rates across income groups.')

    st.divider()

    view = st.radio(
        "**Select a view**",
        [
            'Effective Tax Rates',
            'Tax Revenue Sources',
            'Tax Revenue Over Time',
            'Effective Rates Over Time'
        ],
        index=0
    )

    st.divider()

    st.markdown('### Data Sources')
    st.markdown(
        """
        - [OMB Historical Tables](https://www.whitehouse.gov/omb/budget/historical-tables/)
        - [CBO Household Income Report](https://www.cbo.gov/publication/58353)
        - [Tax Policy Center](https://taxpolicycenter.org/)
        - [FRED CPI Data](https://fred.stlouisfed.org/series/CPIAUCSL)
        """
    )
    st.caption('Revenue is adjusted to 2017 dollars by default using CPI')



#---------------------------------------------------------------
# Header
#---------------------------------------------------------------

st.markdown(
    """
    <h1 style='margin-bottom: 0;'>U.S. Federal Tax Dashboard</h1>
    <p style='color: #64748B; font-size: 1.1rem; margin-top: 0.25rem;'>
        Exploring federal tax revenue sources and effective rates across income groups
    </p>
    """,
    unsafe_allow_html=True
)


#-----------------------------------------------------------------
# View 1: Effective Tax Rates (single year, stacked bar)
#-----------------------------------------------------------------

if 'Effective Tax Rates' in view and 'Over Time' not in view:

    col_ctrl1, col_ctrl2 = st.columns([1, 3])
    with col_ctrl1:
        fy = st.select_slider(
            'Fiscal Year',
            options=eff_rate_years,
            value=max(eff_rate_years)
        )
    
    fig = effective_rates_chart(eff_rates, fy)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Key stats row
    df_fy = eff_rates[(eff_rates['Year'] == fy) & (eff_rates['Tax Type'] == 'Total Federal Tax Rate')]
    if not df_fy.empty:
        row = df_fy.iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Lowest Quintile", f"{row.get('Lowest Quintile', 0):.1f}%")
        c2.metric("Middle Quintile", f"{row.get('Middle Quintile', 0):.1f}%")
        c3.metric("Highest Quintile", f"{row.get('Highest Quintile', 0):.1f}%")
        c4.metric("Top 1%", f"{row.get('Top 1%', 0):.1f}%")

    
    with st.expander('About this chart'):
        st.markdown(
            """
            Effective tax rates represent the share of income each group actually pays in federal taxes, broken down by the type of tax (individual income taxes, corporate income taxes, payroll taxes, and excise taxes). 
            
            A Congressional Budget Office (CBO) analysis allocated all federal taxes to households based on the income group the household fell under (based on percentile), and data from this report is summarized by the Tax Policy Center.

            **Source:** Congression Budget Office via the Tax Policy Center
            """
        )

    df_fy = eff_rates[eff_rates['Year'] == 2019].copy()
    df_fy = df_fy.set_index('Tax Type')
    print("Tax Types in index:")
    for t in df_fy.index.unique():
        print(f"  '{t}'")

    print("Individual Income Tax Rate, Lowest Quintile:", 
      df_fy.loc['Individual Income Tax Rate', 'Lowest Quintile'])
    print("Payroll Tax Rate, Lowest Quintile:",
      df_fy.loc['Payroll Tax Rate', 'Lowest Quintile'])
    print("\nFull row for Individual Income Tax Rate:")
    print(df_fy.loc['Individual Income Tax Rate'])


#---------------------------------------------------------------------------------------------
# View 2: Revenue Composition (Revenue by Source), single year pie + time series share
#---------------------------------------------------------------------------------------------

elif 'Tax Revenue Sources' in view:

    col_ctrl1, _ = st.columns([1, 3])
    with col_ctrl1:
        fy_rev = st.select_slider(
            'Fiscal Year',
            options=revenue_years,
            value=max(revenue_years),
            key='fy_rev',
        )

    fig_pie = revenue_pie_chart(receipts_nom, fy_rev)
    st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with st.expander('About this chart'):
        st.markdown(
            """
            The pie chart shows the composition of federal revenue for a single fiscal year.

            Key trend: Corporate income taxes have shrunk from ~30% of revenue in the 1950s to
            roughly 9–15% today, while payroll taxes (Social Insurance) have grown substantially.

            **Source:** OMB Historical Table 2.1.
            """
        )


#-------------------------------------------------------------------------------------------
# View 3: Revenue Over Time (stacked area, nominal vs real)
#-------------------------------------------------------------------------------------------

elif 'Revenue Over Time' in view:
 
    col_ctrl1, col_ctrl2, _ = st.columns([1, 1, 2])
    with col_ctrl1:
        start = st.select_slider(
            'Start Year',
            options=revenue_years,
            value=1950,
            key="start_rev",
        )
    with col_ctrl2:
        use_real = st.toggle('Inflation-Adjusted (2017 $)', value=False)
 
    if use_real:
        fig = revenue_history(receipts_real, start_year=start, real=True)
    else:
        fig = revenue_history(receipts_nom, start_year=start, real=False)
 
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
 
    with st.expander('About this chart'):
        st.markdown(
            """
            Total federal revenue broken down by source. Toggle between nominal dollars and
            inflation-adjusted (2017) dollars to see real growth versus price-level effects.
 
            Inflation adjustment uses CPI-U annual averages from FRED (Federal Reserve
            Economic Data, originally Bureau of Labor Statistics).
 
            **Source:** OMB Historical Table 2.1; CPI from FRED/BLS.
            """
        )



#--------------------------------------------------------------------------------------------
# View 4: Effective Rates Over Time (line chart)
#--------------------------------------------------------------------------------------------

elif 'Effective Rates Over Time' in view:

    col_ctrl1, _ = st.columns([1, 3])
    with col_ctrl1:
        group_view = st.selectbox(
            'Income Group',
            ['All Quintiles', 'Top Earners'],
            index=0
        )

    fig = effective_rates_over_time(eff_rates, income_group=group_view)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    with st.expander('About this chart'):
        st.markdown(
            """
            Total effective federal tax rate over time for different income groups. 

            "All Quintiles" shows the five quintiles of the income distribution.

            "Top Earners" breaks out the top income quintile into smaller groups.

            **Source:** Congressional Budget Office via the Tax Policy Center
            """
        )



#----------------------------------------------------------------------------------------------
# Footer
#----------------------------------------------------------------------------------------------

st.divider()
st.caption(
    'Built with streamlit & Plotly, Data: OMB, CBO/TPC, FRED'
    '[GitHub](https://github.com/ellie-cothren/federal-tax-figures)'
)

