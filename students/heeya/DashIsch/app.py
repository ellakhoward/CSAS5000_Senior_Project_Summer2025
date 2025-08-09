import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

def load_prep_data():
    la=pd.read_csv('Isch-LA.csv')
    suf=pd.read_csv('Isch-Suf.csv')

    def prep_la(df,county_name):
        df=df[['Year','Count']].copy()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Count'] = df['Count'].astype(str).str.replace(',','')
        df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
        df = df.dropna()
        df['County'] = county_name
        return df
    def prep_suf(df,county_name):
        df=df[['Year','Count']].copy()
        df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
        df['Count'] = pd.to_numeric(df['Count'], errors='coerce')
        df = df.dropna()
        df['County'] = county_name
        return df
   
    la=prep_la(la, 'Los Angeles')
    suf=prep_suf(suf,'Suffolk')
    return la, suf

la_data, suf_data = load_prep_data()

app = Dash(__name__)
app.title = "Ischemic Heart Disease Mortality"
server = app.server

app.layout = html.Div([
    html.H1("Ischemic Heart Disease Mortality", 
            style={'textAlign': 'center', 'marginBottom': 30, 'color': "#700C0C", 'fontFamily': 'sans-serif'}),

 html.Div([
        html.Div([
            dcc.Graph(id='LA-chart', config={'displayModeBar': False})
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        
        html.Div([
            dcc.Graph(id='Suf-chart', config={'displayModeBar': False})
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
    Output('LA-chart', 'figure'),
    Input('LA-chart', 'id')
)

def update_la_chart(_):
    fig = px.bar(
        la_data,
        x = 'Year',
        y = 'Count',
        title='Los Angeles County Mortality',
        labels= {
            'Year':'Year',
            'Count': 'Number of Deaths'
        },
        
        color ='Count',
        color_continuous_scale='reds'
    )

    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        showlegend=False,
        plot_bgcolor="#e1dfdb",
        paper_bgcolor="#e1dfdb"
    ) 
    
    return fig

@app.callback( 
    Output('Suf-chart', 'figure'),
    Input('Suf-chart', 'id')
)

def update_suf_chart(_):
    fig = px.bar(
        suf_data,
        x='Year',
        y='Count',
        title='Suffolk County Mortality',
        labels={
            'Year': 'Year',
            'Count': 'Number of Deaths'
        },
        color='Count',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        xaxis=dict(tickmode='linear'),
        showlegend=False,
        plot_bgcolor='#e1dfdb',
        paper_bgcolor='#e1dfdb'
    )
    
    return fig

if __name__ == '__main__':
    app.run(debug=True)