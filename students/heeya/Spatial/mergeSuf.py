import geopandas as gpd
import pandas as pd

path = r"C:\Users\patelh19\OneDrive - Wentworth Institute of Technology\Documents\yrs\4th\2nd\Spatial\MA_Shapefiles\tl_2023_25_tract.shp"
tracts = gpd.read_file(path)

# Confirm column is GEOID
if 'GEOID10' in tracts.columns:
    tracts = tracts.rename(columns={'GEOID10': 'GEOID'})

# Ensure GEOID is string for both sides
tracts['GEOID'] = tracts['GEOID'].astype(str).str.strip()

# Filter only Suffolk County GEOIDs
tracts = tracts[tracts['GEOID'].str.startswith('25025')]

print(tracts.columns)
print(tracts[['GEOID']].head())

# Read ACS CSV
acs = pd.read_csv('Suf_Demo_Tracts.csv', dtype={'GEOID': str})
acs['GEOID'] = acs['GEOID'].str.strip()  # Clean any whitespace

print(acs.columns)
print(acs[['GEOID']].head())

# Verify if GEOIDs match
intersection = set(tracts['GEOID']) & set(acs['GEOID'])
print(f'Matching GEOIDs found: {len(intersection)}')

# Merge
merged = tracts.merge(acs, on='GEOID', how='left')

merged.to_file('suf_geo.geojson', driver='GeoJSON')