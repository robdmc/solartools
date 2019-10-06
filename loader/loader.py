import pandas as pd
import easier as ezr

class Loader:
    def __init__(self, file_name):
        self.file_name = file_name
        
    def load(self):
        # Import data and make python friendly
        df = pd.read_csv(self.file_name)
        df.columns = ezr.slugify(df.columns)
        
        # Clean out NaN values
        df = df[df.data_monitor_.notnull() & df.zip.notnull()]
        return df
        
    def extract(self, df, monitor_types, monitor_regex, meter_tag):
        # Make column values lower case
        df = df[df.data_monitor_types.str.lower().isin(monitor_types)].copy()
        df['meter_id'] = df.data_monitor_.str.lower().str.extract(monitor_regex)[1]
        
        # Assign meter_tag values to new column named meter_type
        df['meter_type'] = meter_tag
        
        # Change zip from float to string
        df.loc[:,'zip'] = ['' if z == '' else str(int(z)) for z in df.zip.fillna('')]
        
        # Concatenate address, city, and zip into one column
        df['address'] = df.address_line + ' ' + df.city + ', TX ' + df.zip
        
        # Select important columns
        df = df[['address', 'meter_id', 'meter_type']]
        return df
    
    def clean(self, df):
        # Ignore corrupted data (repeated addresses or meter_id's)
        df = df.drop_duplicates(['meter_id', 'meter_type'])
        dfx = df.groupby(by = ['meter_id', 'meter_type'])[['address']].count().sort_values(by = ['address'], ascending = [False])
        dfx = dfx[dfx['address'] > 1].reset_index()
        df = df[~df.meter_id.isin(dfx.meter_id)]
        df = df.dropna(subset = ['meter_id', 'address', 'meter_type'])
        return df
    
    @property
    def df(self):
        return self._df.copy()
    
    @ezr.cached_property
    def _df(self):
        # Load dataframe
        df = self.load()
        
        # Extract meter_id numbers for lightgauge, egauge, and enphase, pLacing them in two new dataframes
        df_lg = self.extract(df, monitor_types = ['lightgauge', 'egauge'], monitor_regex = r'^(lg)?(\d+)$', meter_tag = 'lightgauge')
        df_en = self.extract(df, monitor_types = ['enphase envoy wifi'], monitor_regex = r'([^\d]*)(\d+)$', meter_tag = 'enphase')
        
        # Concatenating two new dataframes (formed above) into one
        df = pd.concat([df_lg,df_en], ignore_index = True)
        
        # Use clean method on dataframe
        df = self.clean(df)
        
        return df