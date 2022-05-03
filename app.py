from flask import Flask, jsonify
import requests
from my_fake_useragent import UserAgent
import json
import random


#get Random USER AGENT
def getRandomUA():
    relatives = ['chrome', 'firefox', 'opera','safari']
    ua = UserAgent(family=random.shuffle(relatives)) #shuffle UA family
    return ua.random().strip()


app = Flask(__name__)
@app.route('/') 
def multi_shipping_rates():
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
    citylink_req = session.post('https://www.citylinkexpress.com/wp-json/wp/v2/getShippingRate',headers=headers, params=payload)
    dataList = []
    result = json.loads(citylink_req.text)
    for key in result:
        value = result[key]['data']['rate']
        dataList.append({'courier': 'citylink', 'rate':float(value)})
    return jsonify({'data':dataList})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)