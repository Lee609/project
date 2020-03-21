import datetime

list = ["2018-06-01 14:54:34", "2018-06-01 14:55:02", "2018-06-01 15:55:02", "2018-06-01 14:55:01"]


def get_list(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()


ls = sorted(list, key=lambda date: get_list(date))
print(ls)



# def get_location_gaode():
#     gaode_url = "https://restapi.amap.com/v3/ip?" \
#                 "key=228987a182eccc691838518d6c15ad0e&output=json"
#     response = requests.get(gaode_url)
#     result = json.loads(response.text)
#     return result['city']
#
#
# def get_location_baidu():
#     baidu_url = "http://api.map.baidu.com/location/ip" \
#                 "?ak=LF0h5LjUXwzFSU8t0EjWWmbh2ZwG9LzE&coor=bd09ll"
#     response = requests.get(baidu_url)
#     result = json.loads(response.text)
#     return result['content']['address_detail']['city']
#
#
# print(get_location_baidu())
#