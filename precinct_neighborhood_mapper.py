import csv
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Define the precinct data
precinct_data = [
    {'Precinct': '1', 'Borough': 'Manhattan', 'Neighborhoods': 'Battery Park, Tribeca'},
    {'Precinct': '5', 'Borough': 'Manhattan', 'Neighborhoods': 'Lower East Side, Chinatown'},
    {'Precinct': '6', 'Borough': 'Manhattan', 'Neighborhoods': 'Greenwich Village, Soho'},
    {'Precinct': '7', 'Borough': 'Manhattan', 'Neighborhoods': 'Lower East Side, Chinatown'},
    {'Precinct': '9', 'Borough': 'Manhattan', 'Neighborhoods': 'Lower East Side, Chinatown'},
    {'Precinct': '10', 'Borough': 'Manhattan', 'Neighborhoods': 'Chelsea, Clinton'},
    {'Precinct': '13', 'Borough': 'Manhattan', 'Neighborhoods': 'Stuyvesant Town, Turtle Bay'},
    {'Precinct': '14', 'Borough': 'Manhattan', 'Neighborhoods': 'Midtown Business District'},
    {'Precinct': '17', 'Borough': 'Manhattan', 'Neighborhoods': 'Stuyvesant Town, Turtle Bay'},
    {'Precinct': '18', 'Borough': 'Manhattan', 'Neighborhoods': 'Chelsea, Clinton'},
    {'Precinct': '19', 'Borough': 'Manhattan', 'Neighborhoods': 'Upper East Side'},
    {'Precinct': '20', 'Borough': 'Manhattan', 'Neighborhoods': 'West Side, Upper West Side'},
    {'Precinct': '22', 'Borough': 'Manhattan', 'Neighborhoods': 'Central Park'},
    {'Precinct': '23', 'Borough': 'Manhattan', 'Neighborhoods': 'East Harlem'},
    {'Precinct': '24', 'Borough': 'Manhattan', 'Neighborhoods': 'West Side, Upper West Side'},
    {'Precinct': '25', 'Borough': 'Manhattan', 'Neighborhoods': 'East Harlem'},
    {'Precinct': '26', 'Borough': 'Manhattan', 'Neighborhoods': 'Manhattanville, Hamilton Heights'},
    {'Precinct': '28', 'Borough': 'Manhattan', 'Neighborhoods': 'Central Harlem'},
    {'Precinct': '30', 'Borough': 'Manhattan', 'Neighborhoods': 'Manhattanville, Hamilton Heights'},
    {'Precinct': '32', 'Borough': 'Manhattan', 'Neighborhoods': 'Central Harlem'},
    {'Precinct': '33', 'Borough': 'Manhattan', 'Neighborhoods': 'Washington Heights, Inwood'},
    {'Precinct': '34', 'Borough': 'Manhattan', 'Neighborhoods': 'Washington Heights, Inwood'},
    {'Precinct': '40', 'Borough': 'The Bronx', 'Neighborhoods': 'Melrose, Mott Haven, Port Morris'},
    {'Precinct': '41', 'Borough': 'The Bronx', 'Neighborhoods': 'Hunts Point, Longwood'},
    {'Precinct': '42', 'Borough': 'The Bronx', 'Neighborhoods': 'Morrisania, Crotona Park East'},
    {'Precinct': '43', 'Borough': 'The Bronx', 'Neighborhoods': 'Soundview, Parkchester'},
    {'Precinct': '44', 'Borough': 'The Bronx', 'Neighborhoods': 'Highbridge, Concourse Village'},
    {'Precinct': '45', 'Borough': 'The Bronx', 'Neighborhoods': 'Throgs Neck, Co-op City, Pelham Bay'},
    {'Precinct': '46', 'Borough': 'The Bronx', 'Neighborhoods': 'University Heights, Fordham, Mt. Hope'},
    {'Precinct': '47', 'Borough': 'The Bronx', 'Neighborhoods': 'Wakefield, Williamsbridge'},
    {'Precinct': '48', 'Borough': 'The Bronx', 'Neighborhoods': 'East Tremont, Belmont'},
    {'Precinct': '49', 'Borough': 'The Bronx', 'Neighborhoods': 'Pelham Parkway, Morris Park, Laconia'},
    {'Precinct': '50', 'Borough': 'The Bronx', 'Neighborhoods': 'Riverdale, Kingsbridge, Marble Hill'},
    {'Precinct': '52', 'Borough': 'The Bronx', 'Neighborhoods': 'Bedford Park, Norwood, Fordham'},
    {'Precinct': '60', 'Borough': 'Brooklyn', 'Neighborhoods': 'Coney Island, Brighton Beach'},
    {'Precinct': '61', 'Borough': 'Brooklyn', 'Neighborhoods': 'Sheepshead Bay, Gerritsen Beach'},
    {'Precinct': '62', 'Borough': 'Brooklyn', 'Neighborhoods': 'Bensonhurst, Bath Beach'},
    {'Precinct': '63', 'Borough': 'Brooklyn', 'Neighborhoods': 'Canarsie, Flatlands'},
    {'Precinct': '66', 'Borough': 'Brooklyn', 'Neighborhoods': 'Borough Park, Ocean Parkway'},
    {'Precinct': '67', 'Borough': 'Brooklyn', 'Neighborhoods': 'East Flatbush, Rugby, Farragut'},
    {'Precinct': '68', 'Borough': 'Brooklyn', 'Neighborhoods': 'Bay Ridge, Dyker Heights'},
    {'Precinct': '69', 'Borough': 'Brooklyn', 'Neighborhoods': 'Canarsie, Flatlands'},
    {'Precinct': '70', 'Borough': 'Brooklyn', 'Neighborhoods': 'Flatbush, Midwood'},
    {'Precinct': '71', 'Borough': 'Brooklyn', 'Neighborhoods': 'Crown Heights South, Wingate'},
    {'Precinct': '72', 'Borough': 'Brooklyn', 'Neighborhoods': 'Sunset Park, Windsor Terrace'},
    {'Precinct': '73', 'Borough': 'Brooklyn', 'Neighborhoods': 'Brownsville, Ocean Hill'},
    {'Precinct': '75', 'Borough': 'Brooklyn', 'Neighborhoods': 'East New York, Starrett City'},
    {'Precinct': '76', 'Borough': 'Brooklyn', 'Neighborhoods': 'Park Slope, Carroll Gardens'},
    {'Precinct': '77', 'Borough': 'Brooklyn', 'Neighborhoods': 'Crown Heights North'},
    {'Precinct': '78', 'Borough': 'Brooklyn', 'Neighborhoods': 'Park Slope, Carroll Gardens'},
    {'Precinct': '79', 'Borough': 'Brooklyn', 'Neighborhoods': 'Bedford Stuyvesant'},
    {'Precinct': '81', 'Borough': 'Brooklyn', 'Neighborhoods': 'Bedford Stuyvesant'},
    {'Precinct': '83', 'Borough': 'Brooklyn', 'Neighborhoods': 'Bushwick'},
    {'Precinct': '84', 'Borough': 'Brooklyn', 'Neighborhoods': 'Brooklyn Heights, Fort Greene'},
    {'Precinct': '88', 'Borough': 'Brooklyn', 'Neighborhoods': 'Brooklyn Heights, Fort Greene'},
    {'Precinct': '90', 'Borough': 'Brooklyn', 'Neighborhoods': 'Williamsburg, Greenpoint'},
    {'Precinct': '94', 'Borough': 'Brooklyn', 'Neighborhoods': 'Williamsburg, Greenpoint'},
    {'Precinct': '100', 'Borough': 'Queens', 'Neighborhoods': 'The Rockaways, Broad Channel'},
    {'Precinct': '101', 'Borough': 'Queens', 'Neighborhoods': 'The Rockaways, Broad Channel'},
    {'Precinct': '102', 'Borough': 'Queens', 'Neighborhoods': 'Woodhaven, Richmond Hill'},
    {'Precinct': '103', 'Borough': 'Queens', 'Neighborhoods': 'Jamaica, St. Albans, Hollis'},
    {'Precinct': '104', 'Borough': 'Queens', 'Neighborhoods': 'Ridgewood, Glendale, Maspeth'},
    {'Precinct': '105', 'Borough': 'Queens', 'Neighborhoods': 'Queens Village, Rosedale'},
    {'Precinct': '106', 'Borough': 'Queens', 'Neighborhoods': 'Ozone Park, Howard Beach'},
    {'Precinct': '107', 'Borough': 'Queens', 'Neighborhoods': 'Fresh Meadows, Briarwood'},
    {'Precinct': '108', 'Borough': 'Queens', 'Neighborhoods': 'Sunnyside, Woodside'},
    {'Precinct': '109', 'Borough': 'Queens', 'Neighborhoods': 'Flushing, Bay Terrace'},
    {'Precinct': '110', 'Borough': 'Queens', 'Neighborhoods': 'Elmhurst, South Corona'},
    {'Precinct': '111', 'Borough': 'Queens', 'Neighborhoods': 'Bayside, Douglaston, Little Neck'},
    {'Precinct': '112', 'Borough': 'Queens', 'Neighborhoods': 'Forest Hills, Rego Park'},
    {'Precinct': '113', 'Borough': 'Queens', 'Neighborhoods': 'Jamaica, St. Albans, Hollis'},
    {'Precinct': '114', 'Borough': 'Queens', 'Neighborhoods': 'Astoria, Long Island City'},
    {'Precinct': '115', 'Borough': 'Queens', 'Neighborhoods': 'Jackson heights, North Corona'},
    {'Precinct': '120', 'Borough': 'Staten Island', 'Neighborhoods': 'Stapleton, Port Richmond'},
    {'Precinct': '122', 'Borough': 'Staten Island', 'Neighborhoods': 'New Springville, South Beach'},
    {'Precinct': '123', 'Borough': 'Staten Island', 'Neighborhoods': 'Tottenville, Woodrow, Great Kills'} ]
def convert_to_csv(xlsx_file):
    read_file = pd.read_excel(xlsx_file, skiprows=11)
    csv_file = xlsx_file.replace('.xlsx', '.csv')
    read_file.to_csv(csv_file, index=True, header=True)
    df = pd.DataFrame(pd.read_csv(csv_file))
    
def download_Weekly_files():
    for data in precinct_data:
        precinct = int(data['Precinct'])
        if precinct > 99:
            formatted_precinct = str(precinct)
        elif precinct > 9:
            formatted_precinct = f"0{precinct}"
        else:
            formatted_precinct = f"00{precinct}"
            
        base_url = f'https://www.nyc.gov/assets/nypd/downloads/excel/crime_statistics/cs-en-us-{formatted_precinct}pct.xlsx'
        file_name = f'crime_stats_{formatted_precinct}pct.xlsx'
        convert_to_csv(file_name)
        try:
            response = requests.get(base_url)
            if response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {file_name}")
            else:
                print(f"Failed to download {file_name}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error downloading {file_name}: {str(e)}")

# used to download weekly files from the NYPD website
# download_Weekly_files()
def read_csv_andProcess(csv_file):
    df_first_part = pd.read_csv(csv_file, nrows=22, header=None)
    #stores historical data
    df_historical_data = pd.read_csv(csv_file, skiprows=22, header=None)
    df_first_part.columns = [
        'Index', 'Crime Type', 'Unnamed_1', 'Week to Date*', 'Unnamed_3','Unnamed_4',
        '28 Day', 'Unnamed_6', 'Unnamed_7', 'Year to Date*', 'Unnamed_9', 'Unnamed_10',
        '2 Year', '14 Year (2010)', '31 Year (1993)'
    ]
    df_first_part['Crime Type'] = df_first_part['Crime Type'].str.strip()
    stats = df_first_part[df_first_part['Crime Type'] == 'TOTAL']

    if not stats.empty:
        #stats to date
        stat_week_to_date = stats['Week to Date*'].values[0]
        # print(f"Total crime statistic for Week to Date*: {stat_week_to_date}")
    else:
        # print("statistics not found in the data.")
        print('test')
    return stats
 
def process_precinct_data(precinct_data):
    borough_totals = {}
    neighborhood_totals = {}
    precinct_crime_totals = {}  # Dictionary to store crime totals per precinct
    precinct_geojson = 'Police Precincts.geojson'
    gdf_precincts = gpd.read_file(precinct_geojson)
    
    for data in precinct_data:
        precinct = int(data['Precinct'])
        if precinct > 99:
            formatted_precinct = str(precinct)
        elif precinct > 9:
            formatted_precinct = f"0{precinct}"
        else:
            formatted_precinct = f"00{precinct}"

        csv_file = f'crime_stats_{formatted_precinct}pct.csv'
        week_to_date_stat = read_csv_andProcess(csv_file)

        if week_to_date_stat is not None:
            # Accumulate the week-to-date statistic to precinct total
            precinct_crime_totals[formatted_precinct] = int(week_to_date_stat['Week to Date*'].values[0])

            # Accumulate the week-to-date statistic to neighborhood and borough total
            neighborhood = data['Neighborhoods']
            if neighborhood not in neighborhood_totals:
                neighborhood_totals[neighborhood] = 0
            neighborhood_totals[neighborhood] += int(week_to_date_stat['Week to Date*'].values[0])
            borough = data['Borough']
            if borough not in borough_totals:
                borough_totals[borough] = 0
            borough_totals[borough] += int(week_to_date_stat['Week to Date*'].values[0])
       
    df_precinct_data = pd.DataFrame(precinct_data)
    df_precinct_data['Precinct'] = df_precinct_data['Precinct'].astype(str)
    if 'precinct' in gdf_precincts.columns:
        gdf_precincts['precinct'] = gdf_precincts['precinct'].astype(str)
    merged_gdf = gdf_precincts.merge(df_precinct_data, left_on='precinct', right_on='Precinct', how='left')
    
    df_neighborhood_totals = pd.DataFrame(list(neighborhood_totals.items()), columns=['Neighborhoods', 'Total_Crimes'])
    min_crimes = df_neighborhood_totals['Total_Crimes'].min()
    max_crimes = df_neighborhood_totals['Total_Crimes'].max()
    df_neighborhood_totals['Safety_Score'] = df_neighborhood_totals['Total_Crimes'].apply(
        lambda x: 1 - ((x - min_crimes) / (max_crimes - min_crimes))
    )
    
    # Add the Safety_Score to the merged_gdf
    merged_gdf = merged_gdf.merge(df_neighborhood_totals, on='Neighborhoods', how='left')
    
    for precinct, total_crimes in precinct_crime_totals.items():
        precinct_num = int(precinct)
        merged_gdf.loc[merged_gdf['precinct'] == f'{precinct_num}', 'Precinct_Total_Crimes'] = total_crimes
    
    return merged_gdf, df_neighborhood_totals

def generate_map(precinct_data):
    merged_gdf, df_neighborhood_totals = process_precinct_data(precinct_data)

    fig, ax = plt.subplots(1, 1, figsize=(30, 15))
    merged_gdf.plot(column='Precinct_Total_Crimes', ax=ax, legend=True, cmap='OrRd',
                    legend_kwds={'label': "Total Crimes by Precinct",
                                 'orientation': "horizontal"})

    for x, y, label, score in zip(merged_gdf.geometry.centroid.x, 
                                  merged_gdf.geometry.centroid.y, 
                                  merged_gdf['Neighborhoods'],
                                  merged_gdf['Safety_Score']):
        
        ax.text(x, y, label, fontsize=5, ha='center', va='center')
        ax.text(x, y - 0.01, f'Score: {score:.2f}', fontsize=5, ha='center', va='center', color='blue')

    plt.title('Crime Saturation by Precinct')
    plt.axis('off')
    plt.show()



# def generate_safety_scores()
# generate_map(precinct_data)
# df_neighborhood_totals = process_precinct_data(precinct_data)
generate_map(precinct_data)
# print(df_neighborhood_totals['Safety_Score'])