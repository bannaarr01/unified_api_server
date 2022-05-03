from flask import Flask, jsonify
import requests
from my_fake_useragent import UserAgent
import json
import random
from lxml import html
from concurrent.futures import ThreadPoolExecutor


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

app = Flask(__name__)
@app.route('/shippingrate') 
def multi_shipping_rates():
    parsedList = parseJt()
    headers = { 'accept': 'application/json, text/javascript, */*; q=0.01',
                'User-Agent': getRandomUA()}
    ctl_payload = {'origin_country': 'MY',
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
    lc_payload = { 
                'zipfrom': '63000',
                'zipto':'71800',
                'weight': 23,
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
    return jsonify({"data":dataList})

 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)