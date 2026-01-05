#!/usr/bin/env python3
"""
NYC Crime Data Consolidator
Downloads weekly crime stats for all precincts and creates unified dataset with crime type breakdown
"""

import json
import requests
import pandas as pd
from pathlib import Path
import time
from io import BytesIO
from precinct_data_mapping import PRECINCT_DATA
# Import precinct data


# Cache file for storing crime data
CACHE_FILE = './public/crime_data_cache.csv'
CACHE_DATE_FILE = './public/crime_data_cache_date.txt'

def should_refresh_cache():
    """Check if cache should be refreshed based on week"""
    from datetime import datetime, timedelta
    
    if not Path(CACHE_FILE).exists():
        return True  # No cache, need to download
    
    if not Path(CACHE_DATE_FILE).exists():
        return True  # No date file, need to download
    
    # Read last download date
    try:
        with open(CACHE_DATE_FILE, 'r') as f:
            last_download = datetime.fromisoformat(f.read().strip())
    except:
        return True  # Can't read date, refresh
    
    current_date = datetime.now()
    
    # Calculate days since last download
    days_since = (current_date - last_download).days
    
    # Always refresh if it's been more than 7 days
    if days_since >= 7:
        print(f"📅 Cache is {days_since} days old - refreshing...")
        return True
    
    if current_date.weekday() == 0:  # Monday
        if last_download.date() < current_date.date():
            print(f"New week detected (Monday) - refreshing data...")
            return True
    
    print(f"✓ Cache is current (updated {days_since} days ago)")
    return False

def save_cache_date():
    """Save current date as cache date"""
    from datetime import datetime
    with open(CACHE_DATE_FILE, 'w') as f:
        f.write(datetime.now().isoformat())
    print(f"✓ Cache timestamp saved")
CACHE_DATE_FILE = 'crime_data_cache_date.txt'

def should_refresh_cache():
    """Check if cache should be refreshed based on week"""
    from datetime import datetime, timedelta
    
    if not Path(CACHE_FILE).exists():
        return True  # No cache, need to download
    
    if not Path(CACHE_DATE_FILE).exists():
        return True  # No date file, need to download
    
    # Read last download date
    try:
        with open(CACHE_DATE_FILE, 'r') as f:
            last_download = datetime.fromisoformat(f.read().strip())
    except:
        return True  # Can't read date, refresh
    
    current_date = datetime.now()
    
    days_since = (current_date - last_download).days
    
    # loading fresh data
    if days_since >= 7:
        return True
    
    # Check if current day is Monday and last download was before this Monday
    if current_date.weekday() == 0:  # Monday
        # Get last Monday
        days_since_monday = current_date.weekday()
        last_monday = current_date - timedelta(days=days_since_monday)
        
        if last_download.date() < last_monday.date():
            return True
    
    return False

def save_cache_date():
    """Save current date as cache date"""
    from datetime import datetime
    with open(CACHE_DATE_FILE, 'w') as f:
        f.write(datetime.now().isoformat())

def format_precinct_number(precinct):
    """Format precinct number with leading zeros"""
    precinct_num = int(precinct)
    if precinct_num > 99:
        return str(precinct_num)
    elif precinct_num > 9:
        return f"0{precinct_num}"
    else:
        return f"00{precinct_num}"

def download_and_convert_precinct(precinct):
    """Download XLSX from URL and return as DataFrame"""
    formatted_precinct = format_precinct_number(precinct)
    base_url = f'https://www.nyc.gov/assets/nypd/downloads/excel/crime_statistics/cs-en-us-{formatted_precinct}pct.xlsx'
    
    try:
        response = requests.get(base_url, timeout=30)
        
        if response.status_code == 200:
            # Read XLSX from bytes directly into DataFrame
            df = pd.read_excel(BytesIO(response.content), header=None)
            return df
        else:
            print(f"✗ {formatted_precinct} - HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print(f"✗ {formatted_precinct} - Error: {str(e)}")
        return None


def extract_crime_stats(df):
    """Extract crime statistics from precinct DataFrame including breakdown by type"""
    try:
        # Crime types mapping (row indices in the CSV)
        crime_types = {
            'Murder': 13,
            'Rape': 14,
            'Robbery': 15,
            'Felony Assault': 16,
            'Burglary': 17,
            'Grand Larceny': 18,
            'Grand Larceny Auto': 19
        }
        
        # Extract individual crime counts
        crime_breakdown = {}
        for crime_name, row_idx in crime_types.items():
            try:
                # Column 2 is "Week to Date" 2026
                count = int(float(df.iloc[row_idx, 2])) if pd.notna(df.iloc[row_idx, 2]) else 0
                crime_breakdown[crime_name] = count
            except (IndexError, ValueError):
                crime_breakdown[crime_name] = 0
        
        # Extract totals from rows 13-32
        crime_data = df.iloc[13:33]
        
        week_to_date_total = 0
        month_to_date_total = 0
        year_to_date_total = 0
        
        for idx, row in crime_data.iterrows():
            try:
                # Column 2 = Week to Date, Column 5 = 28 Day, Column 8 = Year to Date
                week_val = int(float(row[2])) if pd.notna(row[2]) else 0
                month_val = int(float(row[5])) if pd.notna(row[5]) else 0
                year_val = int(float(row[8])) if pd.notna(row[8]) else 0
                
                week_to_date_total += week_val
                month_to_date_total += month_val
                year_to_date_total += year_val
            except (ValueError, TypeError):
                continue
        
        return {
            'weekToDate': week_to_date_total,
            'monthToDate': month_to_date_total,
            'yearToDate': year_to_date_total,
            'crimeBreakdown': crime_breakdown
        }
    except Exception as e:
        print(f"Error extracting stats: {e}")
        return None


def consolidate_all_data(force_refresh=False):
    """Consolidate all precinct crime data into a single DataFrame"""
    
    if not force_refresh:
        force_refresh = should_refresh_cache()
    
    if not force_refresh and Path(CACHE_FILE).exists():
        print("=" * 70 + "\nLOADING CACHED CRIME DATA\n" + "=" * 70)
        consolidated_df = pd.read_csv(CACHE_FILE)
        
        # Ensure crimeBreakdown is parsed back to dictionary
        if 'crimeBreakdown' in consolidated_df.columns:
            consolidated_df['crimeBreakdown'] = consolidated_df['crimeBreakdown'].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x
            )
        
        print(f"✓ Loaded {len(consolidated_df)} precincts from cache")
        return consolidated_df
    
    # --- Download Fresh Data ---
    print("=" * 70 + "\nNYC CRIME DATA CONSOLIDATOR\n" + "=" * 70)
    all_data = []
    
    for data in PRECINCT_DATA:
        precinct = data['Precinct']
        df = download_and_convert_precinct(precinct)
        
        if df is not None:
            stats = extract_crime_stats(df)
            if stats:
                all_data.append({
                    'precinct': int(precinct),
                    'borough': data['Borough'],
                    'neighborhoods': data['Neighborhoods'],
                    'crimeCount': stats['weekToDate'],
                    'monthToDate': stats['monthToDate'],
                    'yearToDate': stats['yearToDate'],
                    'crimeBreakdown': stats['crimeBreakdown']
                })
                print(f"✓ {format_precinct_number(precinct)} processed")
        
        time.sleep(0.5)
    
    consolidated_df = pd.DataFrame(all_data)
    
    # --- CRITICAL FIX: CALCULATE WEIGHTS BEFORE SAVING ---
    if not consolidated_df.empty:
        print("\nCalculating weighted safety metrics...")
        
        # 1. Apply weighting logic
        consolidated_df['weightedCrimeVal'] = consolidated_df['crimeBreakdown'].apply(calculate_weighted_score)
        
        # 2. Normalize Safety Score
        min_val = consolidated_df['weightedCrimeVal'].min()
        max_val = consolidated_df['weightedCrimeVal'].max()
        
        if max_val > min_val:
            consolidated_df['safetyScore'] = 1 - ((consolidated_df['weightedCrimeVal'] - min_val) / (max_val - min_val))
        else:
            consolidated_df['safetyScore'] = 1.0

    # 3. Save to cache with all new columns included
    df_to_save = consolidated_df.copy()
    df_to_save['crimeBreakdown'] = df_to_save['crimeBreakdown'].apply(json.dumps)
    df_to_save.to_csv(CACHE_FILE, index=False)
    
    save_cache_date()
    print(f"✓ Data fully consolidated and cached with Weighted Metrics.")
    
    return consolidated_df

def calculate_weighted_score(breakdown):
    """Calculates a total weighted crime value for a precinct"""
    # Severity weights: Violent crimes carry much more weight than property theft
    weights = {
        'Murder': 50,
        'Rape': 25,
        'Robbery': 10,
        'Felony Assault': 8,
        'Burglary': 5,
        'Grand Larceny Auto': 3,
        'Grand Larceny': 1
    }
    
    if not isinstance(breakdown, dict):
        return 0
        
    return sum(breakdown.get(crime, 0) * weight for crime, weight in weights.items())

if __name__ == "__main__":
    # 1. Load data (Cache or Fresh)
    consolidated_df = consolidate_all_data(force_refresh=False)
    
    if not consolidated_df.empty:
        # 2. Apply Weighting
        # This converts specific crime counts into a single "Severity Value"
        consolidated_df['weightedCrimeVal'] = consolidated_df['crimeBreakdown'].apply(calculate_weighted_score)
        
        # 3. Normalize the Safety Score (0.0 to 1.0)
        # 1.0 = Safest (lowest weighted crime), 0.0 = Least Safe (highest weighted crime)
        min_val = consolidated_df['weightedCrimeVal'].min()
        max_val = consolidated_df['weightedCrimeVal'].max()
        
        if max_val > min_val:
            consolidated_df['safetyScore'] = 1 - ((consolidated_df['weightedCrimeVal'] - min_val) / (max_val - min_val))
        else:
            consolidated_df['safetyScore'] = 1.0
            
        # 4. Add a Safety Rank (1 = Safest Precinct in NYC)
        consolidated_df['safetyRank'] = consolidated_df['safetyScore'].rank(ascending=False, method='min').astype(int)

        # Sort by safety for the final display
        consolidated_df = consolidated_df.sort_values('safetyRank')

        # Display results
        print("\n" + "=" * 70)
        print(f"TOP 10 SAFEST PRECINCTS (Weighted by Severity)")
        print("=" * 70)
        # Select key columns for a clean table view
        view_cols = ['safetyRank', 'precinct', 'borough', 'neighborhoods', 'safetyScore']
        print(consolidated_df[view_cols].head(10).to_string(index=False))
        
        print("\n" + "=" * 70)
        print("LEAST SAFE PRECINCTS (Weighted by Severity)")
        print("=" * 70)
        print(consolidated_df[view_cols].tail(5).to_string(index=False))