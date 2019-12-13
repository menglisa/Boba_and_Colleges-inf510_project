import requests
import json
api_key = 'AIzaSyD5Jbf2eVNoNa4T_DA_XLz1uceKoNlot2Q'

# use Google Maps "Place Details" to convert place_ids to lat,long of colleges
def coordinates(dataframe):
    coordinates = {}
    coordinates['latitude'] = []
    coordinates['longitude'] = []
    
    googlemaps_places_details_endpoint = 'https://maps.googleapis.com/maps/api/geocode/json?'
    
    list_of_place_ids = dataframe['place_id']
    
    for i in list_of_place_ids:
        if i == None:
            coordinates['latitude'].append(None)
            coordinates['longitude'].append(None)
        else:
            details_params = {'place_id': i, 'fields': 'formatted_address', 'key': api_key}
    
            try:
                json_response = requests.get(googlemaps_places_details_endpoint, params=details_params)
                json_response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                print(e)
            else:
                print(f'{json_response.url} was successfully retrieved with status code {json_response.status_code}')

            # dicts in dicts
            result = json_response.json()

            # get lat and long into lists
            lat = result['results'][0]['geometry']['location']['lat']
            coordinates['latitude'].append(lat)

            long = result['results'][0]['geometry']['location']['lng']
            coordinates['longitude'].append(long)
        
    return coordinates

if __name__ == "__main__":
    print('You called me from the command line! Please import as module in meng_lisa.py')
else:
    print(__name__ , 'was imported as a module!')