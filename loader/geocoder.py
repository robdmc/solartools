import geocoder
import pandas as pd
import numpy as np

DEFAULT_PATH = './data/geocoded_addresses.csv'

"""
This class expects a dataframe with columns: address, meter_id, and meter_type.

It will add two columns to this dataframe named lat and lng with values of ROOFTOP accuracy only.

If an error occurs with geocoding the address, an error will be printed with the geocoder's active status and accuracy.

"""

class Geocoder: 
    def __init__(self, file_name=DEFAULT_PATH):
        api_key = "AIzaSyBWXwoKIB3lLg2HxMdL5uTVy4S_Jy-4jQo"
        # Define file_name in constructor
        self.file_name = file_name
        
    def load_from_file(self, file_name=None):
        # If file_name not specified, use default file_name in constructor
        if file_name is None:
            file_name = self.file_name
        self.df = pd.read_csv(file_name)
        
    def geocode(self, df):
        # Create empty lists to append lat and lng values
        lat = []
        lng = []

        for a in df['address']:
            # Selects geocoder (osm, google, etc.)
            g = geocoder.google(a, key=api_key)
            # Create variable for method that pulls out lat and lng values
            lat_lng = g.latlng
            # Create variable for checking if meter_id has ROOFTOP accuracy
            accuracy_is_good = g.geojson['features'][0]['properties']['accuracy'] == 'ROOFTOP'
            # If geocoder working and accuracy ROOFTOP, pull lat and lng values and append them to list
            if g.ok and accuracy_is_good:
                lat.append(lat_lng[0])
                lng.append(lat_lng[1])
            # Otherwise, print error explaining why and append NaN values to list
            else:
                print(f'problem with {a}.g.ok = {g.ok} accuracy good = {accuracy_is_good}')
                lat.append(np.NaN)
                lng.append(np.NaN)
        # Add lat_lng to dataframe
        df['lat'] = lat
        df['lng'] = lng
        
        # Define df in geocode method
        self.df = df
        
    def save(self, file_name=DEFAULT_PATH):
        # Save final dataframe to csv file
        self.df.to_csv(file_name, index = False)