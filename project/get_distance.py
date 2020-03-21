import requests
import json
from math import radians, cos, sin, asin, sqrt


def baiduMap_location(address):
    base_url = "http://api.map.baidu.com/geocoding/v3/" \
               "?address={address}&output=json&ak=LF0h5LjUXwzFSU8t0EjWWmbh2ZwG9LzE".format(address=address)
    response = requests.get(base_url)
    result = json.loads(response.text)
    '''
    location:lat－维度,lng－经度
    precise:位置的附加信息,是否精确查找,1为精确查找
    confidence:描述打点绝对精度
    comprehension:描述地址理解程度
    level:能精确理解的地址类型
    '''
    return result


def getCoordinate(address):
    baidu_result_address = baiduMap_location(address)
    coordinate_address = baidu_result_address['result']['location']
    return coordinate_address


def getDistance(address_a, address_b):
    coordinate_a = getCoordinate(address_a)
    coordinate_b = getCoordinate(address_b)
    lng_a = coordinate_a['lng']
    lat_a = coordinate_a['lat']
    lng_b = coordinate_b['lng']
    lat_b = coordinate_b['lat']
    # 将十进制度数转化为弧度
    lng_a, lat_a, lng_b, lat_b = map(radians, [lng_a, lat_a, lng_b, lat_b])
    # haversine公式
    dis_lng = lng_b - lng_a
    dis_lat = lat_b - lat_a
    a = sin(dis_lat/2)**2 + cos(lat_a) * cos(lat_b) * sin(dis_lng/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371    # 地球平均半径
    distance = c * r
    return round(distance, 1)    # 单位为公里


def gaodeMap_location(address):
    url = "https://restapi.amap.com/v3/geocode/geo" \
          "?key=228987a182eccc691838518d6c15ad0e&address={}".format(address)
    response = requests.get(url)
    result = json.loads(response.text)
    return result


def gaode_coordinate(address):
    location_dict = gaodeMap_location(address)
    location = location_dict['geocodes'][0]['location']
    location_list = list(location)
    lng_str = ''
    lat_str = ''
    flag = False
    for s in location_list:
        if not flag:
            if s != ',':
                lng_str = lng_str + s
            else:
                flag = True
        else:
            lat_str = lat_str + s

    return eval(lng_str), eval(lat_str)


def getDistance_gaode(address_a, address_b):
    coordinate_a = gaode_coordinate(address_a)
    coordinate_b = gaode_coordinate(address_b)
    lng_a = coordinate_a[0]
    lat_a = coordinate_a[1]
    lng_b = coordinate_b[0]
    lat_b = coordinate_b[1]
    # 将十进制度数转化为弧度
    lng_a, lat_a, lng_b, lat_b = map(radians, [lng_a, lat_a, lng_b, lat_b])
    # haversine公式
    dis_lng = lng_b - lng_a
    dis_lat = lat_b - lat_a
    a = sin(dis_lat / 2) ** 2 + cos(lat_a) * cos(lat_b) * sin(dis_lng / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # 地球平均半径
    distance = c * r
    return round(distance, 1)  # 单位为公里


# a = '长沙'
# b = '海口'
# distance_a_b = getDistance_gaode(a, b)
# print(distance_a_b)
#
# distance_a_b_baidu = getDistance(a, b)
# print(distance_a_b_baidu)

