import requests
import json


def get_attraction(address):
    attraction_list = []
    url = "http://api.map.baidu.com/place/v2/search" \
          "?query=旅游景点&region={}&output=json&ak=LF0h5LjUXwzFSU8t0EjWWmbh2ZwG9LzE".format(address)
    response = requests.get(url)
    result = json.loads(response.text)
    for r in result['results']:
        attraction_list.append("{}:{}".format(r['name'], r['address']))
    return attraction_list


# address = '北京'
# ls = get_attraction(address)
# print(ls)

# ls = get_attraction('北京')
# for d in ls:
#     print(d)

# def get_detail(address):
#     uid_list = get_uid(address)
#     detail_list = []
#     for uid in uid_list:
#         detail_url = "http://api.map.baidu.com/place/v2/detail" \
#              "?uid={}&output=json&scope=2&ak=LF0h5LjUXwzFSU8t0EjWWmbh2ZwG9LzE".format(uid)
#         detail_response = requests.get(detail_url)
#         detail_result = json.loads(detail_response.text)
#         detail_list.append([detail_result['result']['name'],
#                             detail_result['result']['address'],
#                             detail_result['result']['detail_info']['tag'],
#                             detail_result['result']['detail_info']['overall_rating']])
#     return detail_list


