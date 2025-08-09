import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

def load_prep_data():
    aqi_suf = pd.read_csv('AQI-BOS.csv')
    aqi_la = pd.read_csv('AQI-LA.csv')
    infant_suf = pd.read_csv('BOSInfantDeaths.csv')
    infant_la = pd.read_csv('InfantDeathsLA.csv')

    def prep_aqi(df, county_name):
        df = df[['Year', 'AQI']].copy()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['AQI'] = pd.to_numeric(df['AQI'], errors='coerce')
        df = df.dropna()
        df['County'] = county_name
        return df

    def prep_infant(df, county_name):
        df = df[['Year', 'Number of Deaths']].copy()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Number of Deaths'] = pd.to_numeric(df['Number of Deaths'], errors='coerce')
        df = df.dropna()
        df['County'] = county_name
        return df
    
    # Process all data
    aqi_suffolk = prep_aqi(aqi_suf, 'Suffolk')
    aqi_la = prep_aqi(aqi_la, 'Los Angeles')
    infant_suffolk = prep_infant(infant_suf, 'Suffolk')
    infant_la = prep_infant(infant_la, 'Los Angeles')
    
    # Combine data
    all_aqi = pd.concat([aqi_suffolk, aqi_la], ignore_index=True)
    all_infant = pd.concat([infant_suffolk, infant_la], ignore_index=True)
    
    return all_aqi, all_infant

# Load data
aqi_data, infant_data = load_prep_data()

# Initialize app
app = Dash(__name__)
app.title = "PM2.5 and Infant Mortality Dashboard"
server = app.server

app.layout = html.Div([
    html.H1("PM2.5 and Infant Mortality Dashboard", 
            style={'textAlign': 'center', 'marginBottom': 30, 'color': "#700C0C", 'fontFamily': 'sans-serif'}),
    
    html.Div([
        html.Label("Select County:", 
                  style={'marginBottom': 10, 'fontSize': 16, 'fontFamily': 'Verdana'}),
        dcc.Dropdown(
            id='county-dropdown',
            options=[
                {'label': 'Suffolk County, MA', 'value': 'Suffolk'},
                {'label': 'Los Angeles County, CA', 'value': 'Los Angeles'}
            ],
            value='Suffolk',
            clearable=False,
            style={'marginBottom': 20}
        )
    ], style={'width': '400px', 'margin': '0 auto', 'fontFamily': 'Verdana'}),
    
    html.Div([
        html.Div([
            dcc.Graph(id='aqi-chart', config={'displayModeBar': False})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='infant-chart', config={'displayModeBar': False})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '4%'})
    ]),
], style={
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

@app.callback(
    Output('aqi-chart', 'figure'),
    Input('county-dropdown', 'value')
)
def update_aqi_chart(selected_county):
    filtered_data = aqi_data[aqi_data['County'] == selected_county]

    fig = px.line(
        filtered_data,
        x='Year',
        y='AQI',
        title=f"Air Quality Index of PM2.5 - {selected_county} County",
        labels={'Year': 'Year', 'AQI': 'Air Quality Index (μg/m³)'},
        markers=True
    )
    
    fig.update_traces(line=dict(color= "blue", width=4), marker=dict(size=8, color="blue"))
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        yaxis=dict(title='AQI Value'),
        showlegend=False,
        hovermode='x unified',
        plot_bgcolor="#e1dfdb",
        paper_bgcolor="#e1dfdb",
        height=400
    )
    return fig

@app.callback(
    Output('infant-chart', 'figure'),
    Input('county-dropdown', 'value')
)
def update_infant_chart(selected_county):
    filtered_data = infant_data[infant_data['County'] == selected_county]

    fig = px.bar(
        filtered_data,
        x='Number of Deaths',
        y='Year',
        title=f"Infant Mortality - {selected_county} County",
        labels={'Year': 'Year', 'Number of Deaths': 'Number of Infant Deaths'},
        color='Number of Deaths',
        color_continuous_scale='reds',
        orientation='h'
    )
    
    fig.update_layout(
        yaxis=dict(tickmode='linear'),
        showlegend=False,
        hovermode='y unified',
        plot_bgcolor='#e1dfdb',
        paper_bgcolor="#e1dfdb",
        height=400
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)