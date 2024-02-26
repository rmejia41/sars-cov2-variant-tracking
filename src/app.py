#Final SARS-2_CoV-2 Variant Tracker
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Load and clean the dataset
df = pd.read_csv('https://github.com/rmejia41/open_datasets/raw/main/sars_cov_2_data.csv')
df['week_ending'] = pd.to_datetime(df['week_ending'])
df['published_date'] = pd.to_datetime(df['published_date'])
latest_published_date = df['published_date'].max().strftime('%B %d, %Y')

# Separate and sort HHS regions, correctly ordering numeric values
regions = df['usa_or_hhsregion'].unique().tolist()
if 'ALL' in regions:
    regions.remove('ALL')
numeric_regions = sorted([int(r) for r in regions if r.isdigit()], key=int)
non_numeric_regions = sorted([r for r in regions if not r.isdigit()])
sorted_regions = ['ALL'] + [str(r) for r in numeric_regions] + non_numeric_regions

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SANDSTONE])
server = app.server

# Define a modern blue color and red for the latest update date
modern_blue_color = "#007BFF"
red_color = "#FF0000"

app.layout = dbc.Container(fluid=True, children=[
    dbc.Row(justify="center", children=[
        dbc.Col(md=8, children=[
            html.H1("SARS-CoV-2 Variant Tracker", className="mb-2 mt-2 text-center", style={'color': modern_blue_color}),
            html.P("Visualize the distribution of variant proportions over time.", className="mb-2 text-center", style={'color': modern_blue_color}),
            html.P(f"Latest CDC Data Update: {latest_published_date}", className="mb-4 text-center", style={'color': red_color}),
        ])
    ]),
    dbc.Row([
        dbc.Col(md=4, children=[
            html.Div([
                html.Label("Select Date Range:", className="form-label"),
                dcc.DatePickerRange(
                    id='date-picker-range',
                    start_date=df['week_ending'].min(),
                    end_date=df['week_ending'].max(),
                    min_date_allowed=df['week_ending'].min(),
                    max_date_allowed=df['week_ending'].max(),
                    className="mb-4"
                ),
                html.Div(style={'height': '10px'}),
                html.Label("Select HHS Region:", className="form-label"),
                dcc.Dropdown(
                    id='region-selector',
                    options=[{'label': region, 'value': region} for region in sorted_regions],
                    value='ALL',
                    multi=True,
                    className="mb-4"
                ),
                html.Div(style={'height': '10px'}),
                html.Label("Select Variant:", className="form-label"),
                dcc.Dropdown(
                    id='variant-selector',
                    options=[{'label': 'All Variants', 'value': 'ALL'}] +
                            [{'label': variant, 'value': variant} for variant in df['variant'].unique()],
                    value='ALL',
                    multi=True
                ),
            ], className="mb-5"),
        ]),
        dbc.Col(md=8, children=[
            dcc.Graph(id='variant-distribution'),
            html.Div([
                html.A("CDC Respiratory Virus Updates",
                       href="https://www.cdc.gov/respiratory-viruses/whats-new/",
                       target="_blank",
                       className="text-center d-block mt-4", style={'color': modern_blue_color})
            ], className="text-center")
        ]),
    ])
])

@app.callback(
    Output('variant-distribution', 'figure'),
    [Input('region-selector', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('variant-selector', 'value')])
def update_graph(selected_regions, start_date, end_date, selected_variants):
    # Convert start_date and end_date from string to datetime if necessary
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Adjust filtering based on "All Regions" or "All Variants" selection
    if 'ALL' in selected_regions or selected_regions is None or len(selected_regions) == 0:
        filtered_df = df
    else:
        filtered_df = df[df['usa_or_hhsregion'].isin(selected_regions)]

    if 'ALL' in selected_variants or selected_variants is None or len(selected_variants) == 0:
        filtered_df = filtered_df
    else:
        filtered_df = filtered_df[filtered_df['variant'].isin(selected_variants)]

    filtered_df = filtered_df[
        (filtered_df['week_ending'] >= start_date) &
        (filtered_df['week_ending'] <= end_date)
    ]

    # Use a boxplot to represent the distribution of variant proportions
    fig = px.box(filtered_df, x='variant', y='share',
                 title="Distribution of SARS-CoV-2 Variant Proportions",
                 labels={'share': 'Variant Proportion', 'variant': 'Variant'},
                 color='variant', notched=True)
    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True, port=8054)
