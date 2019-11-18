# -*- coding: utf-8 -*-

from utils import *
from crawler_all_products import crawl_all_products


product_records = {}

# Pretend to be a common user
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/78.0.3904.97 Safari/537.36'
headers = {'User-Agent': user_agent,
           'server': 'PChome/1.0.4',
           'Referer': 'https://mall.pchome.com.tw/newarrival/'}

url = 'https://ecapi.pchome.com.tw/mall/cateapi/v1/sign' \
      '&tag=newarrival' \
      '&fields=Id,Name,Sort,Nodes' \
      '&_callback=jsonpcb_newarrival&{}'.format(millis)

# Get the response
res_text = requests.get(url=url, headers=headers).text

# Parse the content in json format
res_text = res_text.replace("try{jsonpcb_newarrival(", "")
res_text_json = res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
jd = json.loads(res_text_json)

for cat_layer1 in jd[0:1]:
    cat_layer1_name = cat_layer1['Name']
    for cat_layer2 in cat_layer1['Nodes']:
        cat_layer2_name = cat_layer2['Name']
        cat_layer2_id = cat_layer2['Id']
        page_id = 1
        for page in range(1, 100):
            product_records_cat = crawl_all_products(cat_layer2_id, page_id, millis, headers)
            for key in product_records_cat.keys():
                if key not in product_records:
                    product_records[key] = {}
                for sub_key in product_records_cat[key].keys():
                    if sub_key not in product_records[key]:
                        product_records[key][sub_key] = []
                    product_records[key][sub_key] = product_records[key][sub_key] + product_records_cat[key][sub_key]
            if product_records_cat:
                page_id += 50
                time.sleep(8)
            else:
                break
        # Write into a json file
        with open('data/{}/{}/info.json'.format(key, sub_key), 'w') as f:
            json.dump(product_records, f)



