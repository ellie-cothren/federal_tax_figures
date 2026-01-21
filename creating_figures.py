# functions to create a variety of figures using federal tax data

# import necessary packages
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
import os


# creates stacked bar chart showing effective tax rates for different income groups, broken down by tax type
# creates chart for a given fiscal year 
def effective_rates_chart(data_file, fiscal_year, style, output_dir):

    # load data
    df = pd.read_csv(data_file)

    # filter data to chosen fiscal year
    df_fy = df[df['Year'] == fiscal_year].copy()

    # set plot style
    plt.style.use(style)    

    print(f"Creating effective tax rate charts for FY{fiscal_year}...")

    if len(df_fy) == 0:
        print(f"Error: No data available for fiscal year {fiscal_year}")
        print(f"Available years: {df['Year'].min()} - {df['Year'].max()}")
        return 
    
    # set tax type as index
    df_fy = df_fy.set_index('Tax Type')

    # define income groups to display
    income_groups = [
        'Lowest Quintile',
        'Second Quintile',
        'Middle Quintile',
        'Fourth Quintile',
        'Highest Quintile',
        '81st - 90th Percentiles',
        '91st - 95th Percentiles',
        '96th - 99th Percentiles',
        'Top 1%'
    ]

    # improved labels for x-axis
    income_labels = [
        'Lowest\nQuintile',
        'Second\nQuintile',
        'Middle\nQuintile',
        'Fourth\nQuintile',
        'Highest\nQuintile',
        '81st - 90th\nPercentile',
        '91st - 95th\nPercentile',
        '96th - 99th\nPercentile',
        'Top 1%'
    ]

    # overall rates for each group (for labeling)
    overall_rates = df_fy.loc['Total Federal Tax Rate', income_groups].values

    # build data dict for stacked bars
    effective_rates = {
        'Individual Income Tax': df_fy.loc['Individual Income Tax Rate', income_groups].values,
        'Corporate Income Tax': df_fy.loc['Corporate Income Tax Rate', income_groups].values,
        'Payroll Tax': df_fy.loc['Payroll Tax Rate', income_groups].values,
        'Excise Tax': df_fy.loc['Excise Tax Rate', income_groups].values
    }

    # create data from for plotting
    plot_data = pd.DataFrame(effective_rates, index=income_labels)

    # create figure and axis
    fig, ax = plt.subplots(figsize=(14,8))

    # create stacked bar chart
    plot_data.plot.bar(
        stacked=True,
        rot=0,
        width=0.8,
        ax=ax
    )

    # add overall rate to top of bars
    overall_rates_rounded = np.round(overall_rates, 1)
    labels = [f"({rate}%)" for rate in overall_rates_rounded]
    ax.bar_label(ax.containers[-1], labels=labels, fontsize=14)
    
    # Add horizontal lines showing effective tax rate for each group
    # Using plot() instead of axhline for precise positioning
    bar_width = 0.8
    
    for i, rate in enumerate(overall_rates_rounded):
        # Bar is centered at position i
        line_left = i - bar_width/2
        line_right = i + bar_width/2
        
        # Adjust for Top 1% if label would be blocked
        y_offset = -0.35 if i == len(income_groups) - 1 and rate > 30 else 0
        
        # Draw horizontal line using plot
        ax.plot(
            [line_left, line_right],
            [rate + y_offset, rate + y_offset],
            linewidth=2,
            linestyle='--',
            color='k',
            alpha=0.7
        )

    # formatting
    ax.set_ylabel('Average Tax Rate (%)', fontsize=14)
    ax.set_xlabel('')
    ax.grid(True, alpha=0.3)
    ax.set_ylim(top=max(overall_rates_rounded) + 5)

    # title and legend
    plt.title(f'U.S. Federal Effective Tax Rates: Fiscal Year {fiscal_year}', fontsize=20, pad=20)
    ax.legend(fontsize=12, loc='upper left', framealpha=0.9)

    plt.tight_layout()

    # save figure
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'effective_rates_fy{fiscal_year}.png')
    plt.savefig(output_path, dpi=1000, bbox_inches='tight')
    print(f"Figure saved to {output_path}")

    plt.show()









# creates donut chart showing sources for revenue for a given fiscal year 
def revenue_donut_chart(data_file, fiscal_year, style, output_dir):

    # load data
    df = pd.read_csv(data_file)

    # set fiscal year as index
    df = df.set_index('Fiscal Year')

    if fiscal_year not in df.index:
        print(f"Error: No data available for fiscal year {fiscal_year}")
        print(f"Available years: {df.index.min()} - {df.index.max()}")
        return
    
    # get data for selected fiscal year
    df_fy = df.loc[fiscal_year]

    # Set plot style
    plt.style.use(style)

    # extract revenue sources (in million of USD)
    ind_income = df_fy['Individual Income Taxes']
    corp_income = df_fy['Corporation Income Taxes']
    social_insurance = df_fy['Social Insurance and Retirement Receipts Total']
    excise = df_fy['Excise Taxes']
    other = df_fy['Other']

    # convert from million USD to billions USD
    revenues = np.array([ind_income, corp_income, social_insurance, excise, other]) / 1000

    # calculate percent of total
    total_revenue = sum(revenues)
    percentages = (revenues / total_revenue) * 100

    # labels for each revenue source 
    labels = [
        'Individual Income',
        'Corporate Income',
        'Social Insurance Retirement',
        'Excise Taxes',
        'Other'
    ]

    # create descriptions ith dollar amount labels
    descriptions = [f"{label}: {pct:.1f}%"
                    for label, pct in zip(labels, percentages)]
    
    # create figure and axis
    fig, ax = plt.subplots(figsize=(14,8), subplot_kw=dict(aspect="equal"))


    # create donut chart
    wedges, texts = ax.pie(
        revenues, 
        wedgeprops=dict(width=0.5),
        startangle=55,
    )

    # style for annotations 
    bbox_props = dict(boxstyle="round,pad=0.5", fc="white", ec="black", lw=1.2, alpha=0.9)
    kw = dict(
        arrowprops=dict(arrowstyle="-", lw=1.5, color='black'),
        bbox=bbox_props,
        zorder=0,
        va="center",
        fontsize=12
    )

    # add labels and lines pointing to wedges
    for i, p in enumerate(wedges):
        # calcuate angle and position
        ang = (p.theta2 - p.theta1)/ 2.+p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))

        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]

        # set connection style for arrows
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        kw["arrowprops"].update({"connectionstyle": connectionstyle})

        # add annotation 
        ax.annotate(
            descriptions[i],
            xy=(x, y),
            xytext=(1.15 * np.sign(x), 1.15*y),
            horizontalalignment=horizontalalignment,
            **kw
        )

    # add titles
    plt.suptitle(f'U.S. Federal Tax Revenues: Fiscal Year {fiscal_year}', fontsize=20)

    plt.title(f'Total Revenue = ${total_revenue:.1f} billion', fontsize=16)
    
    # save figure
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'revenue_donut_fy{fiscal_year}.png')
    plt.savefig(output_path, dpi=1000, bbox_inches='tight')
    print(f"Figure saved to {output_path}")

    plt.show()










# creates pie chart showing revenue sources for a given fiscal year (default to 2022)
# information is essentially the same as the donut chart, just stylistically different
def revenue_pie_chart(data_file, fiscal_year, style, output_dir):

    # load data
    df = pd.read_csv(data_file)
    df = df.set_index('Fiscal Year')

    if fiscal_year not in df.index:
        print(f"Error: No data available for fiscal year {fiscal_year}")
        print(f"Available years: {df.index.min()} - {df.index.max()}")
        return
    
    # get data for selected fiscal year
    df_fy = df.loc[fiscal_year]

    # set plot style
    plt.style.use(style)

    # extract revenue sources (in millions USD)
    ind_income = df_fy['Individual Income Taxes']
    corp_income = df_fy['Corporation Income Taxes']
    social_insurance = df_fy['Social Insurance and Retirement Receipts Total']
    excise = df_fy['Excise Taxes']
    other = df_fy['Other']

    # convert from millions to billions
    revenues = np.array([ind_income, corp_income, social_insurance, excise, other]) / 1000

    # create labels for each revenue source
    labels = [
        'Individual Income Taxes',
        'Corporate Income Taxes',
        'Social Insurance and\nRetirement Receipts',
        'Excise Taxes',
        'Other'
    ]

    # create figure and axis
    fig, ax = plt.subplots(figsize=(14, 8))
    
    
    # function to format autopct labels (percentage and dollar amount)
    def format_label(pct):
        return f"{pct:.1f}%" if pct > 1 else ""
    
    # Create pie chart
    wedges, texts, autotexts = ax.pie(
        revenues,
        autopct=format_label,
        textprops=dict(color="white"),
        startangle=-45,
        pctdistance=0.75
    )

    # add legend
    ax.legend(
        wedges,
        labels,
        loc="center left",
        bbox_to_anchor=(0.85, 0.85),
        fontsize=12,
    )

    # format percent labels
    plt.setp(autotexts, size=16, weight="bold")
    
    # add titles
    plt.suptitle(
        f'U.S. Federal Tax Revenues: Fiscal Year {fiscal_year}',
        fontsize=20,
    )
    plt.title(
        f'Total Revenue = ${sum(revenues):.1f} billion',
        fontsize=14,
        pad=15
    )

    plt.tight_layout()
    
    # save figure
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'revenue_pie_fy{fiscal_year}.png')
    plt.savefig(output_path, dpi=1000, bbox_inches='tight')
    print(f"Figure saved to {output_path}")
    
    plt.show()









# creates stacked plot using time series data on tax revenue shares over time
def revenue_share_hist(data_file, start_year, style, output_dir):

    # set plot style
    plt.style.use(style)

    # load cleaned data
    df = pd.read_csv(data_file)
    df = df.set_index('Fiscal Year')

    df = df[df.index >= start_year]

    # extract time series data
    fiscal_years = df.index.tolist()

    ind_income = df['Individual Income Taxes'].tolist()
    corp_income = df['Corporation Income Taxes'].tolist()
    social_insurance = df['Social Insurance and Retirement Receipts Total'].tolist()
    excise = df['Excise Taxes'].tolist()
    other = df['Other'].tolist()

    # stack revenue source for plotting
    revenue_shares = [ind_income, corp_income, social_insurance, excise, other]

    labels = [
        'Individual Income Taxes',
        'Corporate Income Taxes',
        'Social Insurance and Retirement Receipts',
        'Excise Taxes',
        'Other'
    ]

    # create figure and axis
    fig, ax = plt.subplots(figsize=(14,8))

    # create stacked area plot
    ax.stackplot(
        fiscal_years,
        revenue_shares,
        labels=labels,
        alpha=0.8
    )

    # formatting 
    ax.legend(loc='lower right', fontsize=12, framealpha=0.9)
    ax.set_title(
        f'U.S. Federal Tax Revenue by Source: {min(fiscal_years)} - {max(fiscal_years)}',
        fontsize = 20,
        pad = 20
    )
    ax.set_xlabel('Fiscal Year', fontsize=14)
    ax.set_ylabel('Percentage of Total Revenue', fontsize=14)

    ax.set_ylim(0,100)

    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    # save figure
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'revenue_share_hist_start{start_year}.png')
    plt.savefig(output_path, dpi=1000, bbox_inches='tight')
    print(f"Figure saved to {output_path}")

    plt.show()








# creates stacked plot from time series data on tax revenue broken down by revenue source
def revenue_hist(data_file, start_year, style, output_dir, real):

    # set plot style
    plt.style.use(style)

    # load data
    df = pd.read_csv(data_file)    
    df = df.set_index('Fiscal Year')

    df = df[df.index >= start_year]

    # extract time series 
    fiscal_years = df.index.tolist()
    
    ind_income = df['Individual Income Taxes'].tolist()
    corp_income = df['Corporation Income Taxes'].tolist()
    social_insurance = df['Social Insurance and Retirement Receipts Total'].tolist()
    excise = df['Excise Taxes'].tolist()
    other = df['Other'].tolist()

    # Convert from millions to billions
    revenue_sources = np.array([ind_income, corp_income, social_insurance, excise, other]) / 1000

    labels = [
        'Individual Income Taxes',
        'Corporate Income Taxes',
        'Social Insurance and Retirement Receipts',
        'Excise Taxes',
        'Other'
    ]    

    # create figure and axis
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create stacked area plot
    ax.stackplot(
        fiscal_years,
        revenue_sources,
        labels=labels,
        alpha=0.8
    )

    if real:
        title_tag = 'Inflation Adjusted'
    else:
        title_tag = 'Nominal'

    # formatting
    ax.legend(loc='upper left', fontsize=12, framealpha=0.9)
    ax.set_title(
        f'U.S. Federal Tax Revenue by Source ({title_tag}): {min(fiscal_years)} - {max(fiscal_years)}',
        fontsize=20,
        pad=20
    )

    ax.set_xlabel('Fiscal Year', fontsize=14)
    ax.set_ylabel('Revenue (Billions of Dollars)', fontsize=14)

    ax.grid(True, alpha=0.3)

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}B'))

    plt.tight_layout()

    if real:
        tag = 'real'
    else:
        tag = 'nominal'

    # save figure
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f'revenue_hist_{tag}_start{start_year}.png')
    plt.savefig(output_path, dpi=1000, bbox_inches='tight')
    print(f"Figure saved to {output_path}")
    
    plt.show()