import logging
from biomatools.utils.components import BioMALocationTable, BioMAWeatherTable, InvalidLocationDictionaryError, InvalidWeatherDictionaryError
import pandas as pd

from biomatools.utils.naming import BIOMA_LOCATION_COLUMNS, BIOMA_WEATHER_COLUMNS

class ModelRun():

    def __init__(self, weather:BioMAWeatherTable=None, locations:BioMALocationTable=None, params=None, configuration = None):
        self.weather = weather
        self.locations = locations
        self.params = params
        self.configuration = configuration


    def set_weather_data(self, data = None, *args, **kwargs):
        f'''sets the weather data table no matter what you throw in it.
        
        Parameters
        ----------
        data: dict | pd.DataFrame default:None
            the weather data you want to include in the model run.
            Use this argument if you already have the all of it into a data structure
            and that data structure is a dictionary already formatted as a BioMA table
            or a pandas DataFrame. If you don't have such a data structure, just pass
            data series as individual arguments
        renaming: dict default:None
            a dictionary of mappings between your data format names and BioMA tables
            variables names. You need this only if you are passing a pandas DataFrame
            and column names are not set properly.
        *args and **kwargs
            if what you have is a bunch of lists, pass them individually as *named arguments*
            valid variable names are {BIOMA_WEATHER_COLUMNS}
        
        '''
        if isinstance(data, dict):
            try:
                self.weather = BioMAWeatherTable.from_dict(data)
            except InvalidWeatherDictionaryError as e:
                # wrong dictionary structure and/or naming
                logging.error('Invalid dictionary structure and/or naming. Check the documentation.')
                logging.info(help(BioMAWeatherTable))
                raise e
        elif isinstance(data, pd.DataFrame):
            # this fails rather silently: if the dataframe is not parsed correctly, it will
            # just create an empty one
            self.weather = BioMAWeatherTable.from_df(data, *args, **kwargs)
       
        elif data is None:
            self.weather = BioMAWeatherTable.from_series(*args, **kwargs)

    def set_locations(self, data, *args, **kwargs):
        f'''sets the weather data table no matter what you throw in it.
        
        Parameters
        ----------
        data: dict | pd.DataFrame default:None
            the location data you want to include in the model run.
            Use this argument if you already have the all of it into a data structure
            and that data structure is a dictionary already formatted as a BioMA table
            or a pandas DataFrame. If you don't have such a data structure, just pass
            data series as individual arguments
        renaming: dict default:None
            a dictionary of mappings between your data format names and BioMA tables
            variables names. You need this only if you are passing a pandas DataFrame
            and column names are not set properly.
        *args and **kwargs
            if what you have is a bunch of lists, pass them individually as *named arguments*
            valid variable names are {BIOMA_LOCATION_COLUMNS}
        
        '''
        if isinstance(data, dict):
            try:
                self.locations = BioMALocationTable.from_dict(data)
            except InvalidLocationDictionaryError as e:
                # wrong dictionary structure and/or naming
                logging.error('Invalid dictionary structure and/or naming. Check the documentation.')
                logging.info(help(BioMALocationTable))
                raise e
        elif isinstance(data, pd.DataFrame):
            # this fails rather silently: if the dataframe is not parsed correctly, it will
            # just create an empty one
            self.locations = BioMALocationTable.from_df(data, *args, **kwargs)
       
        elif data is None:
            self.locations= BioMALocationTable.from_series(*args, **kwargs)

    def set_configuration(self,):
        pass

    def set_parameters(self,):
        pass

    def build_request(self):
        out = {'tables': [self.locations.toJSON(), 
                          self.weather.toJSON()]}
        return out


class SimplifiedModelRun(ModelRun):
    
    def __init__(self, weather):
        super().__init__(weather, None, None, None)