import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# -------------------- Load & Preprocess Pollutant Data --------------------
def load_pollutant_data(file_path, pollutant_name, county_name):
    df = pd.read_csv(file_path, low_memory=False)
    df['Year'] = pd.to_datetime(df['date_local'], errors='coerce').dt.year
    df = df[df['Year'] <= 2021]  # Truncate to 2021

    if 'arithmetic_mean' in df.columns:
        measure_col = 'arithmetic_mean'
    elif 'Arithmetic Mean' in df.columns:
        measure_col = 'Arithmetic Mean'
    elif 'arithmetic mean' in df.columns:
        measure_col = 'arithmetic mean'
    elif 'sample_measurement' in df.columns:
        measure_col = 'sample_measurement'
    else:
        raise KeyError("No known concentration column found.")

    df = df.groupby('Year')[measure_col].mean().reset_index()
    df['Pollutant'] = pollutant_name
    df['County'] = county_name
    df.rename(columns={measure_col: 'Concentration'}, inplace=True)
    return df

# LA County pollutant data
la_o3 = load_pollutant_data('LA County Ozone Trends 2000-2021.csv', 'Ozone', 'LA')
la_no2 = load_pollutant_data('LA County NO2 Trends 2000-2024.csv', 'NO2', 'LA')
la_benzene = load_pollutant_data('LA County Benzene Trends 2000-2021.csv', 'Benzene', 'LA')

# Suffolk County pollutant data
suf_o3 = load_pollutant_data('Suffolk County Ozone Trends 2000-2024.csv', 'Ozone', 'Suffolk')
suf_no2 = load_pollutant_data('Suffolk County NO2 Trends 2000-2024.csv', 'NO2', 'Suffolk')
suf_benzene = load_pollutant_data('Suffolk County Benzene Trends 2000-2024.csv', 'Benzene', 'Suffolk')

pollutant_df = pd.concat([la_o3, la_no2, la_benzene, suf_o3, suf_no2, suf_benzene])

# -------------------- Load & Preprocess Asthma Hospitalization Data --------------------

# Suffolk hospitalization
suf_hosp = pd.read_csv('Suffolk County Asthma Hospitalizations 2000-2021.csv', low_memory=False)
suf_hosp.columns = suf_hosp.columns.str.strip().str.lower()
if 'year' in suf_hosp.columns and 'case count' in suf_hosp.columns:
    suf_hosp = suf_hosp[['year', 'case count']].copy()
else:
    raise KeyError("Expected columns 'year' and 'case count' not found in Suffolk file")
suf_hosp.columns = ['Year', 'Hospitalizations']
suf_hosp = suf_hosp[(suf_hosp['Year'] >= 2000) & (suf_hosp['Year'] <= 2021)]
suf_hosp['County'] = 'Suffolk'

# LA hospitalization data — concatenate both datasets without summing
la1 = pd.read_csv('LA Asthma Hospitalizations 2005-2023.csv', low_memory=False)
la2 = pd.read_csv('LA Asthma in Younger Adults (Age 18-39).csv', low_memory=False)

la1.columns = la1.columns.str.strip().str.lower()
la2.columns = la2.columns.str.strip().str.lower()

if 'year' in la1.columns and 'count_icd9' in la1.columns and 'year' in la2.columns and 'count_icd9' in la2.columns:
    la1 = la1[['year', 'count_icd9']]
    la2 = la2[['year', 'count_icd9']]
else:
    raise KeyError("Expected columns 'year' and 'count_icd9' not found in LA hospitalization files")

# Filter years 2000-2021
la1 = la1[(la1['year'] >= 2000) & (la1['year'] <= 2021)]
la2 = la2[(la2['year'] >= 2000) & (la2['year'] <= 2021)]

# Concatenate datasets (no summing)
la_hosp = pd.concat([la1, la2], ignore_index=True)
la_hosp.columns = ['Year', 'Hospitalizations']
la_hosp['County'] = 'LA'

# Combine Suffolk and LA hospitalization data
hosp_df = pd.concat([suf_hosp, la_hosp])

# -------------------- App Layout --------------------
app.layout = dbc.Container([
    html.H2("Pollution & Asthma Dashboard"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='county-dropdown',
                options=[
                    {'label': 'LA County', 'value': 'LA'},
                    {'label': 'Suffolk County', 'value': 'Suffolk'}
                ],
                value='LA',
                clearable=False
            )
        ], width=6),

        dbc.Col([
            dcc.Dropdown(
                id='pollutant-dropdown',
                options=[
                    {'label': p, 'value': p} for p in ['NO2', 'Ozone', 'Benzene']
                ],
                value='Ozone',
                clearable=False
            )
        ], width=6)
    ], className='my-3'),

    dbc.Row([
        dbc.Col([dcc.Graph(id='pollutant-graph')], width=6),
        dbc.Col([dcc.Graph(id='hospitalization-graph')], width=6),
    ])
])

# -------------------- Callbacks --------------------
@app.callback(
    Output('pollutant-graph', 'figure'),
    Output('hospitalization-graph', 'figure'),
    Input('county-dropdown', 'value'),
    Input('pollutant-dropdown', 'value')
)
def update_graphs(selected_county, selected_pollutant):
    # Pollutant graph
    df_poll = pollutant_df[
        (pollutant_df['County'] == selected_county) &
        (pollutant_df['Pollutant'] == selected_pollutant)
    ]
    df_poll = df_poll.sort_values('Year')
    
    # Ensure Concentration is numeric
    df_poll['Concentration'] = pd.to_numeric(df_poll['Concentration'], errors='coerce')
    df_poll = df_poll.dropna(subset=['Concentration'])  # Remove any NaN values
    
    fig_poll = px.line(df_poll, x='Year', y='Concentration',
                       title=f"{selected_pollutant} Concentration in {selected_county} County")

    # Hospitalization line chart
    df_hosp = hosp_df[hosp_df['County'] == selected_county]
    
    # Remove commas and convert to numeric
    df_hosp['Hospitalizations'] = df_hosp['Hospitalizations'].astype(str).str.replace(',', '')
    df_hosp['Hospitalizations'] = pd.to_numeric(df_hosp['Hospitalizations'], errors='coerce')
    df_hosp = df_hosp.dropna(subset=['Hospitalizations'])  # Remove any NaN values
    
    # Group by year and sum hospitalizations
    df_hosp = df_hosp.groupby('Year')['Hospitalizations'].sum().reset_index()
    df_hosp = df_hosp.sort_values('Year')
    
    fig_hosp = px.line(df_hosp, x='Year', y='Hospitalizations',
                       title=f"Asthma Hospitalizations in {selected_county} County")
    fig_hosp.update_xaxes(range=[2000, 2021])

    return fig_poll, fig_hosp

# -------------------- Run App --------------------
if __name__ == '__main__':
    app.run(debug=True)
