"""
Interactive plotly chart functions for federal tax dashboard

Functions return a plotly.graph_objects.Figure that is rendered in Streamlit with st.plotly_chart()
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px


#-------------------------------------------------------------------------
# Colors, Fonts, and Layouts - consistency across charts
#-------------------------------------------------------------------------

COLORS = {
    'Individual Income Tax' : "#2563EB", 
    'Corporate Income Tax' : "#F59E0B",
    'Payroll Tax' : "#10B981", 
    'Excise Tax' : "#EF4444",
    # revenue sources (handle different naming conventions in OMB data)
    'Individual Income Taxes' : "#2563EB",
    'Corporation Income Taxes' : "#F59E0B",
    'Social Insurance and Retirement Receipts Total' : "#10B981",
    'Excise Taxes' : "#EF4444",
    'Other' : "#8B5CF6", 
}

LAYOUT_DEFAULTS = dict(
    font=dict(family='Inter, system-ui, sans-serif', size=13),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=60, r=30, t=80, b=60),
    hoverlabel=dict(bgcolor='white', font_size=13),
    legend=dict(
        orientation='h', 
        yanchor='bottom',
        y=1.02,
        xanchor='left',
        x=0,
        font=dict(size=12)
    ),
)

def _apply_defaults(fig: go.Figure) -> go.Figure:
    fig.update_layout(**LAYOUT_DEFAULTS)
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor='rgba(0,0,0,0.06)')

    return fig




#------------------------------------------------------------------------
# 1. Effective Tax Rates (by income group) - stacked bar graph
#------------------------------------------------------------------------

def effective_rates_chart(df: pd.DataFrame, fiscal_year: int) -> go.Figure:

    df_fy = df[df['Year'] == fiscal_year].copy()
    if df_fy.empty:
        return go.Figure().add_annotation(text='No data for this year', showarrow=False)
    

    df_fy = df_fy.set_index('Tax Type')

    income_groups = [
        'Lowest Quintile',
        'Second Quintile',
        'Middle Qunitile',
        'Fourth Quintile',
        'Highest Quintile',
        '81st - 90th Percentiles', 
        '91st - 95th Percentiles',
        '96th - 99th Percentiles',
        'Top 1%'
    ]

    short_labels = [
        'Lowest<br>Quintile',
        'Second<br>Quintile',
        'Middle<br>Quintile',
        'Fourth<br>Quintile',
        'Highest<br>Quintile',
        '81st-90th<br>Pctile',
        '91st-95th<br>Pctile',
        '96th-99th<br>Pctile',
        'Top 1%'
    ]

    tax_types = [
        ('Individual Income Tax Rate', 'Individual Income Tax'),
        ('Corporate Income Tax Rate', 'Corporate Income Tax'),
        ('Payroll Tax Rate', 'Payroll Tax'),
        ('Excise Tax Rate', 'Excise Tax')
    ]

    fig = go.Figure()
    for rate_key, display_name in tax_types:
        vals = df_fy.loc[rate_key, income_groups].values.astype(float)
        fig.add_trace(go.Bar(
            x=short_labels,
            y=vals,
            name=display_name,
            marker_color=COLORS[display_name],
            hovertemplate='%{x}<br>' + display_name + ': %{y:.1f}%<extra></extra>'
        ))

    # overall rate annotations
    overall = df_fy.loc['Total Federal Tax Rate', income_groups].values.astype(float)
    for i, rate in enumerate(overall):
        fig.add_annotation(
            x=short_labels[i], y=rate + 0.8,
            text=f'<b>{rate:.1f}%</b>',
            showarrow=False,
            font=dict(size=11)
        )

    fig.update_layout(
        barmode='stack',
        title=dict(text=f'Effective Federal Tax Rates - FY {fiscal_year}', font=dict(size=20)),
        yaxis_title='Average Tax Rate (%)',
        yaxis=dict(range=[0, max(overall) + 6])
    )

    return _apply_defaults(fig)



#---------------------------------------------------------------------------------
# 2. Revenue Donut Chart
#---------------------------------------------------------------------------------

def revenue_donut_chart(df: pd.DataFrame, fiscal_year: int) -> go.Figure:

    df_fy = df.set_index('Fiscal Year')
    if fiscal_year not in df_fy.index:
        return go.Figure().add_annotation(text='No data for this year', showarrow=False)
    
    
    row = df_fy.loc[fiscal_year]

    source_cols = [
        'Individual Income Taxes',
        'Corporation Income Taxes',
        'Social Insurance and Retirement Receipts Total',
        'Excise Taxes', 
        'Other'
    ]

    display_labels = [
        'Individual Income',
        'Corporate Income',
        'Social Insurance & Retirement',
        'Excise Taxes', 
        'Other'
    ]

    values = np.array([row[c] for c in source_cols]) / 1000  # converts millions to billions
    total = values.sum()
    colors = [COLORS[c] for c in source_cols]

    fig = go.Figure(go.Pie(
        labels=display_labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color='white', width=2)),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=13),
        hovertemplate='%{label}<br>$%{value:.1f}B (%{percent})<extra></extra>'
    ))
    fig.update_layout(
        title=dict(text=f'Federal Revenue Sources - FY {fiscal_year}', font=dict(size=20)),
        annotations=[dict(
            text=f'<b>${total:.0f}B</b><br>Total',
            x=0.5, y=0.5, fontsize=18, showarrow=False
        )],
        showlegend=False,
        margin=dict(l=30, r=30, t=80, b=30)
    )

    fig.update(font=LAYOUT_DEFAULTS['font'], paper_bgcolor="rgba(0,0,0,0)")
    
    return fig



#---------------------------------------------------------------------------------
# 3. Revenue share over time - stacked area (percent/share)
#---------------------------------------------------------------------------------

def revenue_share_history(df: pd.DataFrame, start_year: int) -> go.Figure:

    df = df.set_index('Fiscal Year')
    df = df[df.index>= start_year]

    source_cols = [
        'Individual Income Taxes',
        'Corporation Income Taxes',
        'Social Insurance and Retirement Receipts Total',
        'Excise Taxes',
        'Other'
    ]

    display_labels = [
        'Individual Income',
        'Corporate Income',
        'Social Insurance & Retirement',
        'Excise',
        'Other'
    ]

    fig = go.Figure()
    for col, label in zip(source_cols, display_labels):
        fig.add_trace(go.Scatter(
            x=df.index, y=df[col],
            name=label,
            stackgroup='one',
            mode='lines',
            line=dict(width=0.5),
            fillercolor=COLORS[col],
            marker_color=COLORS[col],
            hovertemplate=f'{label}: ' + '%{y:.1f}%<extra></extra>'
        ))

    fig.update_layout(
        title=dict(
            text=f'Revenue Composition Over Time ({df.index.min()}-{df.index.max()})',
            font=dict(size=20),
        ),
        yaxis=dict(title='Share of Total Revenue (%)', range=[0,100]),
        xaxis_title='Fiscal Year'
    )

    return _apply_defaults(fig)



#------------------------------------------------------------------------------------------
# 4. Revenue over time - stacked area (in dollars)
#------------------------------------------------------------------------------------------

def revenue_history(df: pd.DataFrame, start_year: int, real: bool=False) -> go.Figure:

    df = df.set_index('Fiscal Year')
    df = df[df.index >= start_year]

    source_cols = [
        "Individual Income Taxes",
        "Corporation Income Taxes",
        "Social Insurance and Retirement Receipts Total",
        "Excise Taxes",
        "Other",
    ]
    display_labels = [
        "Individual Income",
        "Corporate Income",
        "Social Insurance & Retirement",
        "Excise",
        "Other",
    ]

    tag = 'Inflation Adjusted' if real else 'Nominal'

    fig = go.Figure()
    for col, label in zip(source_cols, display_labels):
        vals = df[col] / 1000           # convert millions to billions
        fig.add_trace(go.Scatter(
            x=df.index, y=vals,
            name=label,
            stackgroup="one",
            mode="lines",
            line=dict(width=0.5),
            fillcolor=COLORS[col],
            marker_color=COLORS[col],
            hovertemplate=f"{label}: " + "$%{y:,.0f}B<extra></extra>",
        ))

    fig.update_layout(
        title=dict(
            text=f'Federal Revenue by Source, {tag} ({df.index.min()}-{df.index.max()})',
            fontsize=dict(size=20)
        ),
        yaxis=dict(title=f'Revenue (Billions USD, {tag})', tickprefix='$', tickformat=','),
        xaxis_title='Fiscal Year'
    )

    return _apply_defaults(fig)



#----------------------------------------------------------------------------------------------
# 5. Effective rates over time - line chart
#----------------------------------------------------------------------------------------------

def effective_rates_over_time(df: pd.DataFrame, income_group: str = 'All Quintiles') -> go.Figure:

    df_total = df[df['Tax Type'] == 'Total Federal Tax Rate'].copy()

    if income_group == 'All Quintiles':
        groups = [
            'Lowest Quintile',
            'Second Quintile',
            'Middle Quintile',
            'Fourth Quintile',
            'Highest Quintile'
        ]
    elif income_group == 'Top Earners':
        groups = [
            '81st - 90th Percentiles',
            '91st - 95th Percentiles',
            '96th - 99th Percentiles',
            'Top 1%'
        ]
    else:
        groups = [income_group]


    quintile_colors = {
        "Lowest Quintile": "#93C5FD",
        "Second Quintile": "#60A5FA",
        "Middle Quintile": "#3B82F6",
        "Fourth Quintile": "#2563EB",
        "Highest Quintile": "#1D4ED8",
        "81st - 90th Percentiles": "#10B981",
        "91st - 95th Percentiles": "#F59E0B",
        "96th - 99th Percentiles": "#EF4444",
        "Top 1%": "#8B5CF6"
    }

    fig = go.Figure()
    for g in groups:
        if g in df_total.columns:
            fig.add_trace(go.Scatter(
                x=df_total['Year'], y=df_total[g],
                name=g,
                mode='lines',
                line=dict(width=2.5, color=quintile_colors.get(g,"#6B7280")),
                hovertemplate=f'{g}: ' + '%{y:.1f}%<extra></extra>'
            ))
    
    fig.update_layout(
        title=dict(text='Effective Federal Tax Rate Over Time', font=dict(size=20)),
        yaxis_title='Total Effective Rate (%)',
        xaxis_title='Year'
    )

    return _apply_defaults(fig)