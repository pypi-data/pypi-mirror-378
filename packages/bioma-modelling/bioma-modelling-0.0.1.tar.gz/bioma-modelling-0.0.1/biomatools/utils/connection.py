import json
import requests
from urllib.parse import urljoin

def call_restful_api(function, data={}, params = {}, base_url=None, key=None, method='POST'):
    '''
    Calls a RESTful API
    
        Parameters:
            function (string): the name of the API method to invoke
            data (dictionary): the data payload for POST requests
            params (dictrionary): key/value pairs to be translated into http parameters
            bas_url (string): the base addres of the API
            key (string): the service key you registered
            method(string): the HTTP method you want to use, defaults to POST

        Returns:
            service response (str or dictionary): Web service response, either a dictionary or a string.
    
    '''
    function_url = urljoin(base_url, function)
    # set request headers    
    headers = {'Ocp-Apim-Subscription-Key': key}
    response = None
    # invoke the Web Service
    if method in ['POST', 'post']:
        headers['Content-Type'] =  'application/json'
        if isinstance(data, str) or isinstance(data, bytes):
            response = requests.post(function_url, data=str(data), params=params, headers=headers)
        else:
            # serialize request data into a json object if needed
            payload = json.dumps(data)
            response = requests.post(function_url, data=payload, params=params, headers=headers)
    else:
        response=requests.get(function_url, params=params, headers=headers)
    if (response.status_code == 200) or (response.status_code == 202): # the 20X status means 'success'
        try:
            return response.json() 
        except:
            try:
                return response.text
            except:
                print('Unable to decode server response')
    else:
        print('Request failed with code ' + str(response.status_code))
    return None