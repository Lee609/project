import requests
import json


def get_location(ip):
    # werkzeug.middleware.proxy_fix获取访问者ip
    gaode_url = "https://restapi.amap.com/v3/ip?" \
                "key=228987a182eccc691838518d6c15ad0e&output=json&ip={}".format(ip)
    response = requests.get(gaode_url)
    result = json.loads(response.text)
    return result['city']


def get_location_baidu(ip):
    baidu_url = "http://api.map.baidu.com/location/ip" \
                "?ak=YZaG1GnZLQKNnfmrzpzb08PuSzGesDXL&coor=bd09ll&ip={}".format(ip)
    response = requests.get(baidu_url)
    result = json.loads(response.text)
    return result['content']['address_detail']['city']


def location_yes(ip):
    location = get_location(ip)
    return location


def get_location_without_ip():
    baidu_url = "http://api.map.baidu.com/location/ip" \
                "?ak=YZaG1GnZLQKNnfmrzpzb08PuSzGesDXL&coor=bd09ll"
    response = requests.get(baidu_url)
    result = json.loads(response.text)
    return result['content']['address_detail']['city']

# print(get_location())
# print(get_location_baidu())
# print(get_location())
