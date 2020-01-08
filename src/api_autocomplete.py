import pandas as pd
import requests
import json

api_key = ''

def normalize_college_name(dataframe):
    api_autocomplete = {}
    api_autocomplete['normalize_name'] = []
    api_autocomplete['place_id'] = []
    
    googlemaps_places_autocomplete_endpoint = 'https://maps.googleapis.com/maps/api/place/autocomplete/json?'
    
    list_of_college_names = dataframe['college_name'].tolist()
    
    for i in list_of_college_names:
        autocomplete_params = {'input': i, 'key': api_key}
    
        try:
            json_response = requests.get(googlemaps_places_autocomplete_endpoint, params=autocomplete_params)
            json_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
        else:
            print(f'{json_response.url} was successfully retrieved with status code {json_response.status_code}')
    
        # dicts in dicts
        result = json_response.json()
        
        if len(result['predictions']) == 0:
            api_autocomplete['normalize_name'].append(None)
            api_autocomplete['place_id'].append(None)
        else:
            full_college_name = result['predictions'][0]['description']
            api_autocomplete['normalize_name'].append(full_college_name)
            place_id = result['predictions'][0]['place_id']
            api_autocomplete['place_id'].append(place_id)
        
    return api_autocomplete


if __name__ == "__main__":
    print('You called me from the command line! Please import as module in meng_lisa.py')
else:
    print(__name__ , 'was imported as a module!')
