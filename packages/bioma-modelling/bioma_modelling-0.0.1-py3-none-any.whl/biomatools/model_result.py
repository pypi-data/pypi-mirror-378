import inspect

from biomatools.utils.components import BioMALocationTable, BioMATable, BioMAWeatherTable
from biomatools.utils.formats import is_bioma_location, is_bioma_table, is_bioma_weather
from biomatools.utils.naming import BIOMA_LOCATION_NAME, BIOMA_WEATHER_NAME


class ModelResult():

    def __init__(self, Tables:list):
        self.data = {}
        for t in Tables:
            if is_bioma_table(t):
                if  is_bioma_location(t):
                    self.data[BIOMA_LOCATION_NAME] = BioMALocationTable.from_dict(t)
                elif is_bioma_weather(t):
                    self.data[BIOMA_WEATHER_NAME] = BioMAWeatherTable.from_dict(t)
                else:
                    self.data[t.get("Name")] = BioMATable.from_dict(t)
    
    def list_tables(self):
        return self.data.keys()
    
    def get_data_table(self, key:str):
        return self.data.get(key)


    @classmethod
    def from_dict(cls, env):
        '''This is mostly used to build the object from the output returned by Web Services'''
        return cls(**{
                k: v for k, v in env.items() 
                if k in inspect.signature(cls).parameters
            })
       