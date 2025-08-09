import geopandas as gpd
import pandas as pd

# Read LA County census tracts GeoJSON file as a GeoDataFrame
tracts = gpd.read_file('la_geo.geojson')

# Reproject census tracts to WGS84 (lat/lon) CRS to match traffic data CRS
# EPSG:4326 is the standard for geographic coordinates (latitude, longitude)
# This ensures both datasets use the same coordinate system for accurate spatial analysis
tracts = tracts.to_crs("EPSG:4326")

# Read traffic density CSV data for LA
traffic = pd.read_csv('TrafficLA2023.csv')

# Convert traffic DataFrame into a GeoDataFrame using longitude and latitude columns
traffic_gdf = gpd.GeoDataFrame(
    traffic,
    geometry=gpd.points_from_xy(traffic['Longitude'], traffic['Latitude']),
    crs="EPSG:4326"
)

# Perform spatial join to associate each traffic point with the census tract
joined = gpd.sjoin(traffic_gdf, tracts[['GEOID', 'geometry']], how="left", predicate='within')

# Aggregate total daily traffic density per census tract
traffic_by_tract = joined.groupby('GEOID')['Daily'].sum().reset_index()

# Rename the aggregated traffic column for clarity
traffic_by_tract.rename(columns={'Daily': 'TrafficDensity'}, inplace=True)

# Merge aggregated traffic data back into the tracts GeoDataFrame
tracts = tracts.merge(traffic_by_tract, on='GEOID', how='left')

# Fill any tracts with no traffic data with zero
tracts['TrafficDensity'] = tracts['TrafficDensity'].fillna(0)

# Check
#print(tracts.columns)
#print(tracts.head())

# Save
tracts.to_file('la_traffic_merged.geojson', driver='GeoJSON')