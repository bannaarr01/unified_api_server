from flask import Blueprint, jsonify, request
import requests
from my_fake_useragent import UserAgent
import json
import random
from lxml import html
from concurrent.futures import ThreadPoolExecutor
from flask_jwt_extended import jwt_required
import validators

shippingrate = Blueprint('shippingrate', __name__, url_prefix='/api/v1/shippingrate')

#get Random USER AGENT
def getRandomUA():
    relatives = ['chrome', 'firefox', 'opera','safari']
    ua = UserAgent(family=random.shuffle(relatives)) #shuffle UA family
    return ua.random().strip()

def parseJt():
    session = requests.Session()
    jt_req = session.get('https://www.jtexpress.my/shipping-rates', verify = False)
    tree = html.fromstring(jt_req.content)
    form = tree.find('.//form')
    token = form.find('.//input[@name="_token"]').value
    parsedList = [token, jt_req.cookies]
    return parsedList

def urls(arg:tuple):
    return arg


@shippingrate.post('/')
@jwt_required()
def multi_shipping_rates():
        origin_postcode = request.get_json().get('origin_postcode', '')
        destination_postcode = request.get_json().get('destination_postcode', '')
        width = request.get_json().get('width', '')
        length = request.get_json().get('length', '')
        height = request.get_json().get('height', '')
        weight = request.get_json().get('weight', '')


        if not validators.length(origin_postcode, min=5, max=5):
            return jsonify({'error': 'Enter valid origin post code'})

        if not validators.length(destination_postcode, min=5, max=5):
            return jsonify({'error': 'Enter valid destination post code'})

        if not validators.between(int(width), min=1, max=999):
            return jsonify({'error': 'Enter valid width'}) 

        if not validators.between(int(length), min=1, max=999):
            return jsonify({'error': 'Enter valid length'})

        if not validators.between(int(height), min=1, max=999):
            return jsonify({'error': 'Enter valid height'})

        if not validators.between(int(weight), min=1, max=999):
            return jsonify({'error': 'Enter valid weight (kg)'})   

        parsedList = parseJt()

        headers = { 'accept': 'application/json, text/javascript, */*; q=0.01',
                    'User-Agent': getRandomUA()}

        ctl_payload = {'origin_country': 'MY',
                    'origin_state': 'Selangor',#Invalid but required
                    'origin_postcode': int(origin_postcode),
                    'destination_country': 'MY',
                    'destination_state': 'Selangor',#Invalid but required
                    'destination_postcode': int(destination_postcode),
                    'length': int(length),
                    'width': int(width),
                    'height': int(height),
                    'selected_type': 1,
                    'parcel_weight': int(weight),
                    'document_weight': ''
                    }
        jt_payload = { '_token': str(parsedList[0]),
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
        lc_payload = { 
                    'zipfrom': origin_postcode,
                    'zipto': destination_postcode,
                    'weight': int(weight),
                    'parceltype':'P'
                    }          
        #Session object to increase performance          
        session = requests.Session()

        list_of_urls = [
        session.post(url="https://www.citylinkexpress.com/wp-json/wp/v2/getShippingRate",  params=ctl_payload, headers=headers, verify=False),
        session.post(url="https://www.jtexpress.my/shipping-rates", params=jt_payload, verify=False, headers=headers,cookies=parsedList[1]),
        session.get('https://lineclearexpress.com/my/quote/quote.php', params=lc_payload, headers=headers, verify = False)
            ] 

        with ThreadPoolExecutor(max_workers=3) as pool:
            response_list =  list(pool.map(urls,list_of_urls))
        dataList = []    
        i = 0
        while i < len(response_list):
            if(i==0): #cityLink
                result = json.loads(response_list[i].text)
                for key in result:
                    value = result[key]["data"]["rate"]
                    dataList.append({"courier": "citylink", "rate":float(value)})
            elif(i==1): #jtexpress
                tree = html.fromstring(response_list[i].content)
                table = tree.xpath("//table[@class='table table-bordered mb-0']//td[@class='col-4']/text()")[6].strip()
                dataList.append({"courier": "jtexpress", "rate":float(table)})
            elif(i==2): #clearlineexpress    
                data = response_list[i].json()
                dataList.append({"courier": "lineclearexpress", "rate":float(data["price"])})     
            i += 1
        return jsonify({"data":dataList}), 200