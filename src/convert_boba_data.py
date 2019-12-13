

def boba_data_dict(data):

    boba_data_dict = {}
    normalize_name_col = []
    price = []
    boba_data_dict['college_id'] = []
    boba_data_dict['store_name']=[]
    boba_data_dict['review_count']=[]
    boba_data_dict['rating']=[]
    boba_data_dict['latitude']=[]
    boba_data_dict['longitude']=[]
    boba_data_dict['price']=[]
    boba_data_dict['distance_from_college']=[]

    for k,v in data.items():
        # need to account for colleges that do not have any stores nearby
        if not v['store_name']:
            normalize_name_col.append(k)
        else: 
            for i in range(len(v['store_name'])):
                normalize_name_col.append(k)

    # create list for foreign key list that relates to College Table    
    n = 1
    seen = {normalize_name_col[0]: n}
    for word in normalize_name_col[1:]:
        if word in seen:
            pass
        else:
            n += 1
            seen[word] = n

    for name in normalize_name_col:
        boba_data_dict['college_id'].append(seen[name])


    for college in data:
        if not data[college]['store_name']:
            boba_data_dict['store_name'].append(None)
            boba_data_dict['review_count'].append(None)
            boba_data_dict['rating'].append(None)
            boba_data_dict['latitude'].append(None)
            boba_data_dict['longitude'].append(None)
            price.append(None)
            boba_data_dict['distance_from_college'].append(None)
        else:
            boba_data_dict['store_name'].extend(data[college]['store_name'])
            boba_data_dict['review_count'].extend(data[college]['review_count'])
            boba_data_dict['rating'].extend(data[college]['rating'])
            boba_data_dict['latitude'].extend(data[college]['latitude'])
            boba_data_dict['longitude'].extend(data[college]['longitude'])
            price.extend(data[college]['price'])
            boba_data_dict['distance_from_college'].extend(data[college]['distance_from_college'])

    # convert $ to int: from $-$$$$ to 1-4
    # must account for None
    for money in price:
        if money == None:
            boba_data_dict['price'].append(None)
        else:
            boba_data_dict['price'].append(len(money))

    return boba_data_dict

if __name__ == "__main__":
    print('You called me from the command line! Please import as module in meng_lisa.py')
else:
    print(__name__ , 'was imported as a module!')