import requests
import json
import time
api_key = ''

# Yelp maxes you out at 20 stores 
def boba_shops(dataframe):
    # create nested dictionary: each college is a key 
    boba_data = {}
    for i in range(len(dataframe['normalize_name'])):
        boba_data[dataframe['normalize_name'][i]] = {"store_name":[], "review_count":[], "rating":[], "latitude":[], "longitude":[], "price":[], "distance_from_college":[]}

        yelp_search_endpoint = 'https://api.yelp.com/v3/businesses/search?'

        details_params = {
            'latitude': dataframe['latitude'][i], 
            'longitude': dataframe['longitude'][i], 
            'radius': 16093, 
            'categories': 'bubbletea,coffee,tea'}
        headers = {'Authorization':'bearer %s' % api_key}

        try:
            json_response = requests.get(yelp_search_endpoint, params=details_params, headers=headers)
            json_response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(e)
            # if 500 error, pause for 3 sec and try again
            # in case 500 persists after 10 tries, break to stop infinite loop
            j = 0
            while json_response.status_code == 500 and j < 10:
                print("TRY AGAIN")
                time.sleep(3)
                json_response = requests.get(yelp_search_endpoint, params=details_params, headers=headers)
                json_response.status_code
                j += 1
            else:
                print(f'{json_response.url} was successfully retrieved on repeated try with status code {json_response.status_code}')
        else:
            print(f'{json_response.url} was successfully retrieved with status code {json_response.status_code}')

        # dicts in dicts
        result = json_response.json()

        for n in range(len(result['businesses'])):
            boba_data[dataframe['normalize_name'][i]]["store_name"].append(result['businesses'][n]['name'])
            boba_data[dataframe['normalize_name'][i]]["review_count"].append(result['businesses'][n]['review_count'])
            boba_data[dataframe['normalize_name'][i]]["rating"].append(result['businesses'][n]['rating'])
            boba_data[dataframe['normalize_name'][i]]["latitude"].append(result['businesses'][n]['coordinates']["latitude"])
            boba_data[dataframe['normalize_name'][i]]["longitude"].append(result['businesses'][n]['coordinates']["longitude"])
            boba_data[dataframe['normalize_name'][i]]["distance_from_college"].append(result['businesses'][n]['distance'])
            if 'price' in result['businesses'][n].keys(): 
                boba_data[dataframe['normalize_name'][i]]["price"].append(result['businesses'][n]['price'])
            else: 
                boba_data[dataframe['normalize_name'][i]]["price"].append(None)
                
    return boba_data


if __name__ == "__main__":
    print('You called me from the command line! Please import as module in meng_lisa.py')
else:
    print(__name__ , 'was imported as a module!')
