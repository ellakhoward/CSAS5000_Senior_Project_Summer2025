import dash
from dash import Dash, dcc, html, Input, Output
import pandas as pd
import plotly.graph_objs as go
import requests
from datetime import datetime



app = dash.Dash(__name__)
server = app.server
app.title = "Past 24-hour CO Levels & Income by Zip Code in Suffolk County, MA"
API_KEY = '5c60f307f08a9fe0acd901195430ee0f'

SUFFOLK_ZIPS = ["02108", "02109", "02110", "02111", "02113", "02114", "02115", "02116", "02118", "02119", "02120", "02121", "02122", "02124",
"02125", "02126", "02127", "02128", "02129", "02130", "02131", "02132", "02134", "02135", "02136", "02150", "02151", "02152", "02163", "02171",
"02199", "02142", "02201", "02210", "02215", "02467"]

#CSV File source - 1. https://www.census.gov/data/developers/data-sets/acs-5year.html, 2. www.incomebyzipcode.com, 3. bestneighborhood.org, 
# & 4. UnitedStatesZipCodes.org

income_df = pd.read_csv("datasources/suffolk_county_ma_income_by_zip.csv")
#income_dict = dict(zip(income_df["ZIP Code"].astype(str), income_df["Median Household Income"]))
income_df["ZIP Code"] = income_df["ZIP Code"].astype(str).str.zfill(5)
income_dict = dict(zip(income_df["ZIP Code"], income_df["Median Household Income"]))


def fetch_lat_lon(zip_code):
    url = f"http://api.openweathermap.org/geo/1.0/zip?zip={zip_code},US&appid={API_KEY}"
    response = requests.get(url)
    print(f"API status: {response.status_code}, ZIP: {zip_code}")
    data = response.json()
    print(f"API response: {data}")
    if "lat" in data and "lon" in data:
        return data["lat"], data["lon"]
    raise ValueError(f"Invalid ZIP code or location not found: {zip_code}")



def fetch_co_data(lat, lon):
    end = int(datetime.utcnow().timestamp())
    start = end - 24 * 3600
    url = (
        f"http://api.openweathermap.org/data/2.5/air_pollution/history"
        f"?lat={lat}&lon={lon}&start={start}&end={end}&appid={API_KEY}"
    )
    response = requests.get(url)
    data = response.json()
    if "list" not in data or not data["list"]:
        print("No CO data returned")
        return pd.DataFrame(columns=["time", "co"])
    
    times = [datetime.utcfromtimestamp(item["dt"]) for item in data["list"]]
    co_vals = [item["components"]["co"] for item in data["list"]]
    return pd.DataFrame({"time": times, "co": co_vals})


app.layout = html.Div([
    html.Div(
         html.H1("Past 24-hour CO Levels & Income by Zip Code in Suffolk County, MA", style={'textAlign': 'center'}),
    ),
    
    dcc.Dropdown(
        id="zip-dropdown",
        options=[{"label": z, "value": z} for z in SUFFOLK_ZIPS],
        value=SUFFOLK_ZIPS[0],
        style={"width": "300px", "margin": "auto"},
        clearable=False
    ),
    
    html.Div([
        dcc.Graph(id="co-chart", style={"width": "48%", "display": "inline-block", "height": "600px"}),
        dcc.Graph(id="income-gauge", style={"width": "48%", "display": "inline-block", "height": "600px"})
    ])
])


@app.callback(
    Output("co-chart", "figure"),
    Output("income-gauge", "figure"),
    Input("zip-dropdown", "value")
)
def update_dashboard(zip_code):
    try:
        lat, lon = fetch_lat_lon(zip_code)
        df = fetch_co_data(lat, lon)

        if df.empty:
            co_fig = go.Figure()
            co_fig.add_annotation(
                text=f"No CO data available for {zip_code}",
                showarrow=False, font=dict(color="orange", size=16),
                xref="paper", yref="paper", x=0.5, y=0.5
            )
            co_fig.update_layout(template="plotly_dark")

        else:
            co_fig = go.Figure(go.Scatter(
                x=df["time"], y=df["co"],
                mode="lines+markers", name="Carbon Monoxide Amount"
            ))
            co_fig.update_layout(
                title=f"Past 24 Hours CO Levels for ZIP Code: {zip_code}",
                title_x=0.5,
                xaxis_title="Time (Universal)",
                yaxis_title="Carbon Monoxide Amount",
                template="plotly_dark"
            )

    except Exception as e:
        co_fig = go.Figure()
        co_fig.add_annotation(
            text=f"Error loading CO data: {str(e)}",
            showarrow=False, font=dict(color="red", size=16),
            xref="paper", yref="paper", x=0.5, y=0.5, align="center"
        )
        co_fig.update_layout(template="plotly_dark")

    income = income_dict.get(zip_code, 0)
    income_fig = go.Figure(go.Indicator(
    mode="gauge+number+delta",
    value=income,
    delta={
        "reference": income * 0.75 if income else 0,
        "increasing": {"color": "green"},
        "decreasing": {"color": "red"}
    },
    title={"text": f"Median Household Income for ZIP Code: {zip_code}"},
    number={"valueformat": ",", "prefix": "$"},
    gauge={
        "axis": {"range": [0, max(income * 1.5, 200000)]},
        "bar": {"color": "yellow"},
        "steps": [
            {"range": [0, income * 0.5], "color": "#248264"},
            {"range": [income * 0.5, income], "color": "#339E53"},
            {"range": [income, max(income * 1.5, 200000)], "color": "#13dc42"}
        ]
    }
))

    income_fig.update_layout(
        template="plotly_dark",
        transition={"duration": 600, "easing": "cubic-in-out"}
    )

    return co_fig, income_fig

if __name__ == '__main__':
    app.run(debug=True)