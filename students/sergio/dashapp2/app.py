import dash
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

csv_file_path = 'datasources/Carbon_Monoxide_Poisoning_Rate_Of_Death_For_CO_Per_100_000_All_States_20250713.csv' 

df = pd.read_csv(csv_file_path)
print(df.columns)
print(df.head())
df = df.rename(columns={
    'Year': 'year',
     'Massachusetts': 'rate'
})

if 'Year' not in df.columns:
    df = df.reset_index().rename(columns={'index': 'year'})
else:
    df = df.rename(columns={'Year': 'year'})

print(df.columns.tolist())

app = dash.Dash(__name__)
server = app.server

app.layout = html.Div(style={'backgroundColor': "#ae924c", 'color': '#fff', 'padding': '2rem'}, children=[
    html.H1("Massachusetts CO Poisoning Death Rate (per 100k) 2000 - 2007", style={'textAlign': 'center'}),
     dcc.Dropdown(
   id='y-axis-type',
    options=[
     {'label': 'Rate', 'value': 'rate'},
    ],
    value='rate',
    clearable=False,
    style={
        'color': 'black',            
        'backgroundColor': 'white'   
    }
),

    dcc.Graph(id='bar-chart'),
])

@app.callback(
    Output('bar-chart', 'figure'),
    Input('y-axis-type', 'value')
)
def update_chart(metric):
    df['year'] = df['year'].astype(str)
    ordered_years = [str(year) for year in range(2000, 2007)] 

    fig = px.bar(
        df,
        x='year',
        y=metric,
        labels={'year': 'Year', metric: 'Deaths per 100k'},
        category_orders={'year': ordered_years}
    )
    fig.update_layout(
        transition_duration=300,
        xaxis_title='Year',
        yaxis_title='Deaths per 100k',
        xaxis_type='category',
    )
    return fig

if __name__ == '__main__':
    app.run(debug=True)