#!/usr/bin/env python3
"""
Map NYC Crime Data to ZIP Codes
Takes consolidated crime data and maps it to ZIP code GeoJSON for 3D visualization.
"""

import json
import pandas as pd
import numpy as np
import random
from pathlib import Path
from precinct_data_mapping import zip_to_precinct

# File paths
CRIME_CACHE = './public/crime_data_cache.csv'
ZIP_GEOJSON = './public/nyc-zip-code-tabulation-areas-polygons.geojson'
OUTPUT_GEOJSON = './public/nyc_zipcodes_with_crime.geojson'

class NYCDataEncoder(json.JSONEncoder):
    """Custom encoder to handle Pandas/Numpy types for JSON export"""
    def default(self, obj):
        if isinstance(obj, (np.int64, np.int32, np.integer)):
            return int(obj)
        if isinstance(obj, (np.float64, np.float32, np.floating)):
            return float(obj)
        if isinstance(obj, (np.ndarray,)):
            return obj.tolist()
        return super(NYCDataEncoder, self).default(obj)

def load_crime_data():
    """Load consolidated crime data from cache"""
    if not Path(CRIME_CACHE).exists():
        print(f"Error: {CRIME_CACHE} not found!")
        return None
    
    df = pd.read_csv(CRIME_CACHE)
    
    if 'crimeBreakdown' in df.columns:
        df['crimeBreakdown'] = df['crimeBreakdown'].apply(
            lambda x: json.loads(x) if isinstance(x, str) else x
        )
    
    print(f"✓ Loaded {len(df)} precincts from {CRIME_CACHE}")
    return df

def load_zip_geojson():
    """Load ZIP code GeoJSON"""
    if not Path(ZIP_GEOJSON).exists():
        print(f"Error: {ZIP_GEOJSON} not found!")
        return None
    
    with open(ZIP_GEOJSON, 'r') as f:
        geojson = json.load(f)
    
    print(f"✓ Loaded {len(geojson['features'])} ZIP codes from {ZIP_GEOJSON}")
    return geojson

def get_safety_label(score):
    if score > 0.8: return "Very Safe"
    if score > 0.6: return "Safe"
    if score > 0.4: return "Moderate"
    if score > 0.2: return "High Crime"
    return "Extreme Alert"

def map_crime_to_zipcodes(crime_df, zip_geojson):
    """Map crime data to ZIP codes using a precise ZIP-to-Precinct Bridge"""
    
    # Create a lookup: Precinct ID -> Data Row
    precinct_lookup = crime_df.set_index('precinct').to_dict('index')

    random.seed(42) 
    enriched_count = 0
    
    for feature in zip_geojson['features']:
        props = feature['properties']
        zip_code = str(props.get('postalCode', ''))
        
        target_precinct = zip_to_precinct.get(zip_code)
        
        if target_precinct and target_precinct in precinct_lookup:
            data = precinct_lookup[target_precinct]
            
            props['neighborhood'] = data['neighborhoods'] 
            props['precinct'] = target_precinct
            props['weightedCrimeVal'] = data['weightedCrimeVal']
            props['crimeCount'] = data['crimeCount']
            props['safetyScore'] = data['safetyScore']
            props['monthToDate'] = data['monthToDate']
            props['yearToDate'] = data['yearToDate']
            props['crimeBreakdown'] = data['crimeBreakdown']
            
            enriched_count += 1
        else:
            props['neighborhood'] = props.get('PO_NAME', 'NYC Area')
            props['safetyScore'] = 0.5
            props['weightedCrimeVal'] = crime_df['weightedCrimeVal'].mean()
            props['crimeCount'] = 0
            props['crimeBreakdown'] = {}

        props['safetyLabel'] = get_safety_label(props.get('safetyScore', 0.5))
            
    print(f"✓ Mapped {enriched_count} ZIP codes to Precincts successfully.")
    return zip_geojson

def save_enriched_geojson(geojson, output_file):
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2, cls=NYCDataEncoder)
    print(f"✓ Saved enriched GeoJSON to: {output_file}")

def main():
    print("="*70 + "\nNYC CRIME TO ZIP CODE MAPPER\n" + "="*70)
    
    crime_df = load_crime_data()
    if crime_df is None: return
    
    zip_geojson = load_zip_geojson()
    if zip_geojson is None: return
    
    enriched_geojson = map_crime_to_zipcodes(crime_df, zip_geojson)
    save_enriched_geojson(enriched_geojson, OUTPUT_GEOJSON)
    
    print("\n✓ Processing Complete. Run 'npm run dev' to visualize.")

if __name__ == "__main__":
    main()