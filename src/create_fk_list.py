colleges_city_id = []
boba_shop_id = []

def fk_dict(value_list):
    i = 1
    seen = {value_list[0]: i}
    for word in value_list[1:]:
        if word in seen:
            pass
        else:
            i += 1
            seen[word] = i
    return seen

def city_fk_list(data, dic):
    for city_name in data["college_city"]:
        for k,v in dic.items():
            if city_name == k:
                colleges_city_id.append(v)
            else:
                pass
    return colleges_city_id
            
def shop_fk_list(data, dic):
    for shop_name in data:
        for k,v in dic.items():
            if shop_name == k:
                boba_shop_id.append(v)
            else:
                pass
    return boba_shop_id


if __name__ == "__main__":
    print('You called me from the command line! Please import as module in meng_lisa.py')
else:
    print(__name__ , 'was imported as a module!')