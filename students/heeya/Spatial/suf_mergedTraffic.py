import geopandas as gpd
import pandas as pd

tracts = gpd.read_file('suf_geo.geojson')

# Reproject tracts to match traffic points CRS
tracts = tracts.to_crs("EPSG:4326")

traffic = pd.read_csv('TrafficSUF2023.csv')
traffic_gdf = gpd.GeoDataFrame(
    traffic,
    geometry=gpd.points_from_xy(traffic['Longitude'], traffic['Latitude']),
    crs="EPSG:4326"
)

joined = gpd.sjoin(traffic_gdf, tracts[['GEOID', 'geometry']], how="left", predicate='within')

traffic_by_tract = joined.groupby('GEOID')['Daily'].sum().reset_index()
traffic_by_tract.rename(columns={'Daily': 'TrafficDensity'}, inplace=True)

tracts = tracts.merge(traffic_by_tract, on='GEOID', how='left')
tracts['TrafficDensity'] = tracts['TrafficDensity'].fillna(0)

tracts.to_file('suf_traffic_merged.geojson', driver='GeoJSON')