import pandas as pd
import geopandas as gpd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load GeoJSONs as GeoDataFrames
la_gdf = gpd.read_file("la_traffic_merged.geojson")
suf_gdf = gpd.read_file("suf_traffic_merged.geojson")

# Convert GeoDataFrames to GeoJSON-like dicts for Plotly
la_geojson = la_gdf.__geo_interface__
suf_geojson = suf_gdf.__geo_interface__

# Create the Dash app
app = Dash(__name__)
app.title = "Traffic+Burdened Communities"
server = app.server

# App layout
app.layout = html.Div([
    html.H1("2023: Traffic Density and Burdened Communities", style={'textAlign': 'center','color': "#023047", 'fontFamily': 'Helvetica'}),

    dcc.Dropdown(
        id='county-dropdown',
        options=[
            {'label': 'Los Angeles County', 'value': 'LA'},
            {'label': 'Suffolk County', 'value': 'Suffolk'}
        ],
        value='LA',
        clearable=False,
        style={'width': '300px', 'margin-bottom': '20px', 'fontFamily': 'Verdana'}
    ),

    dcc.Dropdown(
        id='demo-dropdown',
        options=[
            {'label': 'Hispanic', 'value': 'Hispanic'},
            {'label': 'White', 'value': 'White'},
            {'label': 'Black', 'value': 'Black'},
            {'label': 'Asian', 'value': 'Asian'},
            {'label': 'American Indian and Alaska Native', 'value': 'AIAN'},
            {'label': 'Native Hawaiian & Pacific Islander', 'value': 'NHPI'}
        ],
        value='Hispanic',
        clearable=False,
        style={'width': '300px', 'margin-bottom': '20px', 'fontFamily': 'Verdana'}
    ),

    html.Div([
        dcc.Graph(id='traffic-map', style={'display': 'inline-block', 'width': '48%'}),
        dcc.Graph(id='demo-map', style={'display': 'inline-block', 'width': '48%'})
    ], style={'display': 'flex', 'justify-content': 'space-between'})
],  style={
    'backgroundColor': "#e1dfdb",
    'minHeight': '100vh',
    'margin': '0',
    'padding': '20px',
    'position': 'absolute',
    'top': '0',
    'left': '0',
    'right': '0',
    'bottom': '0'
})

# Callback for traffic map
@app.callback(
    Output('traffic-map', 'figure'),
    Input('county-dropdown', 'value')
)
def update_map(selected_county):
    if selected_county == 'LA':
        gdf = la_gdf
        geojson = gdf.__geo_interface__
        center = {"lat": 34.05, "lon": -118.25}
        color_scale = "magenta"
    else:
        gdf = suf_gdf
        geojson = gdf.__geo_interface__
        center = {"lat": 42.36, "lon": -71.0}
        color_scale = "Blues"

    fig = px.choropleth_mapbox( # choropleth_mapbox depreciated
        gdf,
        geojson=geojson,
        locations='GEOID',  # must match the GeoJSON properties key
        color='TrafficDensity',
        featureidkey="properties.GEOID",  # ties the locations to the geojson
        center=center,
        zoom=8.5,
        opacity=0.6,
        mapbox_style="carto-positron", # map_style used locally
        color_continuous_scale=color_scale
    )

    fig.update_layout(
        plot_bgcolor="#e1dfdb",
        paper_bgcolor="#e1dfdb"
    )

    return fig

# Callback for demographics map
@app.callback(
    Output('demo-map', 'figure'),
    [Input('county-dropdown', 'value'),
     Input('demo-dropdown', 'value')]
)
def update_demo_map(selected_county, selected_demo):
    if selected_county == 'LA':
        gdf = la_gdf
        geojson = la_geojson
        center = {"lat": 34.05, "lon": -118.25}
        color_scale = "magenta"
    else:
        gdf = suf_gdf
        geojson = suf_geojson
        center = {"lat": 42.36, "lon": -71.0}
        color_scale = "Blues"

    fig = px.choropleth_mapbox(
        gdf,
        geojson=geojson,
        locations=gdf.index,
        color=selected_demo,
        center=center,
        zoom=8.5,
        opacity=0.6,
        mapbox_style="carto-positron",
        color_continuous_scale=color_scale
    )

    fig.update_layout(
            plot_bgcolor="#e1dfdb",
            paper_bgcolor="#e1dfdb"
        )

    return fig

if __name__ == "__main__":
    app.run(debug=True)