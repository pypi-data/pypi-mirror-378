import logging
import os

from biomatools.bioma_model import BioMAConfiguration
from biomatools.model_result import ModelResult
from biomatools.utils.abs import AbstractBioMAComponent
from biomatools.utils.connection import call_restful_api

class ModelClient():
    '''The client for a BioMA cloud model'''

    def __init__(self, url, key=None, env_variable_name = 'BIOMA_API_KEY'):
        self.url =url
        self.runs = {} # here we store model run requests
        self.outputs = {} # here we store results
        if key is None:
            env_key = os.environ.get(env_variable_name)
            if env_key is None:
                logging.warning('No API key found in environment')
                self.key = None
            else:
                logging.info(f'Using variable {env_variable_name} from local environment as API key')
                self.key = env_key
        else:
            self.key = key
        self.initial_con = self.get_initial_configuration()

    def get_initial_configuration(self):
        '''This returns the intial configuration of all
        models that this client can run. This information is used to
        build model runner instances'''
        r = call_restful_api('InitialConfiguration', base_url=self.url, key = self.key, method='GET')
        if isinstance(r, dict):
            return BioMAConfiguration.from_dict(r, client=self)
        else:
            logging.warning('Unable to retrieve Initial Configuration. Check you access level.')
            return {}
    
    def get_object_configuration(self, assembly_qualified_name:str):
        '''Returns all configurable items the passed BioMA object could possibly accept'''
        r = call_restful_api('DocumentObject', data= assembly_qualified_name, base_url=self.url, key = self.key, method='POST')
        if isinstance(r, dict):
            return r
        else:
            logging.warning('Unable to retrieve Object configuration. Check you access level.')
            return {}

    def get_object_subtypes(self, assembly_qualified_name:str):
        '''Returns all sub-types the passed BioMA object has on the server'''
        r = call_restful_api('DocumentType', data= assembly_qualified_name, base_url=self.url, key = self.key, method='POST')
        if isinstance(r, dict):
            return r
        else:
            #logging.warning('Unable to retrieve subtypes. Check you access level.')
            return {}

    def add_model_run(self, label:str, model:AbstractBioMAComponent):
        self.runs[label] = model


    def list_models(self):
        '''Returns a list of all ready-made models available on the server.
        
        each string is the assembly-qualified name of a model'''
        r = call_restful_api('ListModels', base_url=self.url, key = self.key, method='GET')
        if isinstance(r, list):
            return [BioMAConfiguration(i, self) for i in r]
        else:
            logging.warning('Unable to retrieve available models. Check you access level.')
            return []
        
    def run(self, idx):
        run = self.runs.get(idx)
        r = call_restful_api('ModelExecution', data= run.json_serialize(), base_url=self.url, key = self.key, method='POST')
        if isinstance(r, dict):
            return ModelResult.from_dict(r)
        else:
            return r

    def run_all(self):
        '''Runs all the loaded model runs'''
        # for each model run, we call the ModelExecution endpoint
        for idx, run in self.runs.items():
            r = call_restful_api('ModelExecution', data= run.json_serialize(), base_url=self.url, key = self.key, method='POST')
            if isinstance(r, dict):
                out = ModelResult.from_dict(r)
                self.outputs[idx] = out
            else:
                logging.warning(f'Model did not return a valid BioMA output for run #{idx}')
                self.outputs[idx] = out



class CalibrationClient():

    def __init__(self, url, key = None, env_variable_name = 'BIOMA_API_KEY'):
        self.url =url
        self.jobs = []
        if key is None:
            env_key = os.environ.get(env_variable_name)
            if env_key is None:
                logging.warning('No API key found in environment')
                self.key = None
            else:
                logging.info(f'Using variable {env_variable_name} from local environment as API key')
                self.key = env_key
        else:
            self.key = key

    def create_job(self, reference_data, alg_params):
        pass