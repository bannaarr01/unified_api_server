from flask import Flask, jsonify
import requests
from my_fake_useragent import UserAgent
import json
import random
from lxml import html


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

app = Flask(__name__)
@app.route('/') 
def multi_shipping_rates():
    parsedList = parseJt()
    headers = { 'accept': 'application/json, text/javascript, */*; q=0.01',
                'User-Agent': getRandomUA()}
    payload = {'origin_country': 'MY',
                'origin_state': 'Selangor',#Invalid but required
                'origin_postcode': 46000,
                'destination_country': 'MY',
                'destination_state': 'Selangor',
                'destination_postcode': 63000,#Invalid but required
                'length': 4,
                'width': 3,
                'height': 6,
                'selected_type': 1,
                'parcel_weight': 44,
                'document_weight': ''
                }
    #Session object to increase performance          
    session = requests.Session()
    # citylink_req = session.post('https://www.citylinkexpress.com/wp-json/wp/v2/getShippingRate',headers=headers, params=payload)
    # dataList = []
    # result = json.loads(citylink_req.text)
    # for key in result:
    #     value = result[key]['data']['rate']
    #     dataList.append({'courier': 'citylink', 'rate':float(value)})
    # return jsonify({'data':dataList})


    jt_payload = { '_token': str(parsedList[0]),
                'shipping_rates_type': 'domestic',
                'sender_postcode': 63000,
                'receiver_postcode': 71800,
                'destination_country': 'BWN',
                'shipping_type': 'EX',
                'weight': 50,
                'length': 12,
                'width': 23,
                'height': 7,
                'item_value': ''
                }

    jt_req = session.post('https://www.jtexpress.my/shipping-rates',headers=headers, params=jt_payload, cookies=parsedList[1], verify = False)

    tree = html.fromstring(jt_req.content)
    table = tree.xpath("//table[@class='table table-bordered mb-0']//td[@class='col-4']/text()")[6].strip()
    return jsonify({"courier": "jt", "data":float(table)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)