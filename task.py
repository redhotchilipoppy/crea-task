'''
Author:         Axel Nordin Fürdös
Date:           2025-01-09
URL:            https://github.com/redhotchilipoppy/crea-task
Info:           Script used to solve short technical task for CREA - Data scientist job application. 
                For full explanation on choices and approach, check out the notebook version available in the github repo.
                The following dependencies must be installed before you can run this script: pandas, requests, geopandas & tabulate
'''

# Imports
import pandas as pd      # Used to produce the final results table
import requests          # Used to grab data from online sources
import geopandas as gdp  # Used to handle geojson data 
import tabulate          # (Note: tabulate is indirectly used by pandas. I include it here so its more clear that it has to be installed)

# Calculating the country areas
countries_coordinates = requests.get("https://datahub.io/core/geo-countries/_r/-/data/countries.geojson")  # Grab the data from the url
gdf = gdp.GeoDataFrame.from_features(countries_coordinates.json()["features"], crs='EPSG:4326')            # Read the data as a geodataframe using the EPSG:4326 coordinate system
gdf = gdf.set_index('ADMIN',drop = True)                                                                   # Set the column "ADMIN" as index so that the full country name is used as index
gdf_2 = gdf.copy()                                                                                         # Make a copy of the geodataframe
gdf_2 = gdf_2.to_crs({'proj':'cea'})                                                                       # Change the copys projection, in this case I choose to use Lambert Cylindrical Equal 
areas = gdf_2.area/1000000                                                                                 # Calculate the area for every country in km^2
countries = ['United States of America','United Kingdom','Turkey','Thailand','Philippines','India']        # List the countries we are interrested in

# Calculating number of pm10 stations
pm10_stations = requests.get("https://api.energyandcleanair.org/stations?country=GB,US,TR,PH,IN,TH&format=geojson")  # Grab the data from the url
pm10_gdf = gdp.GeoDataFrame.from_features(pm10_stations.json()["features"])                                          # Read the data as a geodataframe
def has_pm10(i):                                                                                                     # Function to check if a station measures pm10
    try:                                                                                                             # Some stations dont have a proper list. I use try-except to return False instead of throwing an error.
        return 'pm10' in pm10_gdf.loc[i,'pollutants']
    except:
        return False
       
stations_with_pm10 = [has_pm10(i) for i in pm10_gdf.index]                                                           # Create a list with True for each station that has pm10 and False for all others 
pm10_gdf = pm10_gdf.iloc[stations_with_pm10]                                                                         # Remove all stations from the dataframe that do not have pm10
pm10_stations_per_county = pm10_gdf['country_id'].value_counts()                                                     # Count how often each country code appears
          
# Putting together the final results table
results = pd.DataFrame(index = countries,  columns = ['Number of PM10 Stations','Area (in square kilometers)','Density of PM10 Stations per 1000 sq. km']) # Create the dataframe
results.index.name = "Country Name"                                                                                                                        # Set the index name to "Country Name"
results['Number of PM10 Stations'] = pm10_stations_per_county.rename(index={'US': 'United States of America',                                              # Add number of pm10 stations, but replace country ids with full country names
                                                                            'GB': 'United Kingdom',
                                                                            'IN': 'India',
                                                                            'TR': 'Turkey',
                                                                            'TH': 'Thailand',
                                                                            'PH': 'Philippines'})
results['Area (in square kilometers)'] = areas                                                                                                             # Add country area to table
results['Density of PM10 Stations per 1000 sq. km'] = 1000 * results['Number of PM10 Stations'] / results['Area (in square kilometers)']                   # Calculate the station density
print(results.to_markdown(floatfmt=(".0f", ".0f", ".0f",".3f")))                                                                                           # Print the table as markdown