from flask import Blueprint, jsonify, request
import requests
from my_fake_useragent import UserAgent
import json
import random
from lxml import html
from concurrent.futures import ThreadPoolExecutor
from flask_jwt_extended import jwt_required
import validators
from flasgger import swag_from
from flask_caching import Cache


cache = Cache()
# cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

shippingrate = Blueprint('shippingrate', __name__, url_prefix='/api/v1/shippingrate')

session = requests.Session()

#get Random USER AGENT and Header
def get_header():
    relatives = ['chrome', 'firefox', 'opera','safari']
    ua = UserAgent(family=random.shuffle(relatives)) #shuffle UA family
    header = { 'accept': 'application/json, text/javascript, */*; q=0.01',
                    'User-Agent': ua.random().strip()}  
    return header

#get jtexpress hidden token
def parseJt():
    session = requests.Session()
    try:
        jt_req = session.get('https://www.jtexpress.my/shipping-rates', verify = False, timeout=10)
        tree = html.fromstring(jt_req.content)
        form = tree.find('.//form')
        token = form.find('.//input[@name="_token"]').value
        parsedList = [token, jt_req.cookies]
        return parsedList
    except Exception as e:
        return 'error'


################## ############ ####### #########
def jt_express(origin_postcode, destination_postcode, length, width, height, weight):
    parsedList = parseJt()
    if parsedList != 'error':
        payload = { '_token': str(parsedList[0]),
                        'shipping_rates_type': 'domestic',
                        'sender_postcode': int(origin_postcode),
                        'receiver_postcode': int(destination_postcode),
                        'destination_country': 'BWN',
                        'shipping_type': 'EX',
                        'weight': int(weight),
                        'length': int(length),
                        'width': int(width),
                        'height': int(height),
                        'item_value': ''
                        } 
        headers = get_header()  
        try:
            req = session.post(url="https://www.jtexpress.my/shipping-rates", params=payload, verify=False, headers=headers,cookies=parsedList[1], timeout=10)

            tree = html.fromstring(req.content)
            table = tree.xpath("//table[@class='table table-bordered mb-0']//td[@class='col-4']/text()")[6].strip()

            return {"courier": "jtexpress", "rate":float(table)}
        except Exception as e:
            return 'error' 
    else:
        return 'error' 


###### ############ ############ ######
def line_clear_express(origin_postcode, destination_postcode, weight):
    payload = { 
                    'zipfrom': origin_postcode,
                    'zipto': destination_postcode,
                    'weight': int(weight),
                    'parceltype':'P'
                    }
    headers = get_header()   
    try:                                   
        req=session.get('https://lineclearexpress.com/my/quote/quote.php', params=payload, headers=headers, verify = False, timeout=10)
        data = req.json()
        return {"courier": "lineclearexpress", "rate":float(data["price"])}
    except Exception as e:
        return 'error' 


##################### ######### ######
def city_link(origin_postcode, destination_postcode, length, width, height, weight):

    headers = get_header()                   
    payload = {'origin_country': 'MY',
                'origin_state': 'Selangor', #Invalid but required
                'origin_postcode': int(origin_postcode),
                'destination_country': 'MY',
                'destination_state': 'Negeri Sembilan', #Invalid but required
                'destination_postcode': int(destination_postcode),
                'length': int(length),
                'width': int(width),
                'height': int(height),
                'selected_type': 1,
                'parcel_weight': weight,
                'document_weight': ''
                }
    try:            
        req = session.post('https://www.citylinkexpress.com/wp-json/wp/v2/getShippingRate',headers=headers, params=payload, timeout=10)
    
        result = json.loads(req.text)
        for key in result:
            value = result[key]["data"]["rate"]
            return {"courier": "citylink", "rate":float(value)}
    except Exception as e:
        return 'error'

########################################################################
@shippingrate.post('/')
@jwt_required()
@cache.cached(timeout=15, key_prefix="dataList", query_string=True)
@swag_from('./docs/shippingrate/shippingrate.yaml')
def multi_shipping_rates():
        origin_postcode = request.get_json().get('origin_postcode', '')
        destination_postcode = request.get_json().get('destination_postcode', '')
        width = request.get_json().get('width', '')
        length = request.get_json().get('length', '')
        height = request.get_json().get('height', '')
        weight = request.get_json().get('weight', '')

        #input validations
        if not validators.length(origin_postcode, min=5, max=5):
            return jsonify({'error': 'Enter valid origin post code'}), 422

        if not validators.length(destination_postcode, min=5, max=5):
            return jsonify({'error': 'Enter valid destination post code'}), 422

        if not validators.between(int(width), min=1, max=999):
            return jsonify({'error': 'Enter valid width'}), 422 

        if not validators.between(int(length), min=1, max=999):
            return jsonify({'error': 'Enter valid length'}), 422

        if not validators.between(int(height), min=1, max=999):
            return jsonify({'error': 'Enter valid height'}), 422

        if not validators.between(int(weight), min=1, max=999):
            return jsonify({'error': 'Enter valid weight (kg)'}), 422   

        #retrieve data
        dataList = []
        citylink = city_link(origin_postcode, destination_postcode, length, width, height, weight)
        if citylink != 'error': #cityLink
            dataList.append(citylink)
        jtexpress = jt_express(origin_postcode, destination_postcode, length, width, height, weight)
        if jtexpress != 'error': #jtExpress
            dataList.append(jtexpress)
        lineclearexpress = line_clear_express(origin_postcode,destination_postcode,weight)
        if lineclearexpress != 'error': #lineclearexpress
            dataList.append(lineclearexpress)

        return jsonify({'data': dataList}), 200
