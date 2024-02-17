import requests

def search_toponym(toponym_to_find):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"
    search_params = {
        "apikey": api_key,
        "text": toponym_to_find,
        "lang": "ru_RU",
        "type": "biz"
    }

    response = requests.get(search_api_server, params=search_params)

    if not response:
        return ""

    # Преобразуем ответ в json-объект
    json_response = response.json()
    print(json_response)
    organization = json_response["features"][0]
    return organization


def get_coord(toponym):
    toponym_coodrinates = toponym["geometry"]["coordinates"]
    toponym_longitude, toponym_lattitude = toponym_coodrinates
    return float(toponym_longitude), float(toponym_lattitude)


def get_spn(toponym):
    lcx, lcy = toponym["properties"]["boundedBy"][0]
    rcx, rcy = toponym["properties"]["boundedBy"][1]
    return rcx - lcx, rcy - lcy


def get_address(toponym):
    return toponym["properties"]["CompanyMetaData"]['address']


def get_postal_code(address):
    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": address,
        "format": "json"}

    proxies = {
        'http': 'http://192.168.221.131:3128',
        'https': 'http://192.168.221.131:3128'
    }

    response = requests.get(geocoder_api_server, params=geocoder_params)

    if not response:
        # обработка ошибочной ситуации
        return ""

    json_response = response.json()
    toponym = json_response["response"]["GeoObjectCollection"][
        "featureMember"][0]["GeoObject"]
    print(toponym)
    return toponym['metaDataProperty']['GeocoderMetaData']['Address'].get("postal_code", "")
