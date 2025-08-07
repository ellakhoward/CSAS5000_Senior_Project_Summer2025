import dash
from dash import html, dcc
import requests
import plotly.graph_objs as go
from datetime import datetime

app = dash.Dash(__name__)
server = app.server 
API_KEY = '5c60f307f08a9fe0acd901195430ee0f'
LAT, LON = 34.05, -118.24 
START = 1743500000
END = 1752171644

def get_air_pollution_data():
    url = f'http://api.openweathermap.org/data/2.5/air_pollution/history?lat={LAT}&lon={LON}&start={START}&end={END}&appid={API_KEY}'
    response = requests.get(url)
    data = response.json()
    timestamps, pm25, co, o3 = [], [], [], []

    for item in data['list']:
        dt = datetime.utcfromtimestamp(item['dt'])
        timestamps.append(dt)
        pm25.append(item['components']['pm2_5'])
        co.append(item['components']['co'])
        o3.append(item['components']['o3'])

    return timestamps, pm25, co, o3

timestamps, pm25, co, o3 = get_air_pollution_data()

app.layout = html.Div(style={'backgroundColor': '#d5aa33', 'color': '#fff', 'padding': '2rem'}, children=[

    html.H1('Air Pollution History for the past 3 months in Los Angeles County', style={'textAlign': 'center'}),
    dcc.Graph(
        id='pollution-line-chart',
        figure={
            'data': [
                go.Scatter(x=timestamps, y=pm25, mode='lines+markers', name='PM2.5'),
                go.Scatter(x=timestamps, y=co, mode='lines+markers', name='CO'),
                go.Scatter(x=timestamps, y=o3,  mode='lines+markers', name='O3'),
            ],
            'layout': go.Layout(
                title='Air Pollutants', 
                xaxis={'title': 'Date'},
                yaxis={'title': 'Pollution Amount'},
                template='plotly_dark'
            )
        }
    )
])

if __name__ == '__main__':
    app.run(debug=True)