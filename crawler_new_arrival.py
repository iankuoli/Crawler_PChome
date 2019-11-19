# -*- coding: utf-8 -*-

from utils import *
from crawler_all_products import crawl_all_products


product_records = {}

url = 'https://ecapi.pchome.com.tw/mall/cateapi/v1/sign' \
      '&tag=newarrival' \
      '&fields=Id,Name,Sort,Nodes' \
      '&_callback=jsonpcb_newarrival&{}'.format(millis)
jd = convert2json(url, 'jsonpcb_newarrival')

for cat_layer1 in jd:
    cat_layer1_name = cat_layer1['Name']
    for cat_layer2 in cat_layer1['Nodes']:
        cat_layer2_name = cat_layer2['Name']
        cat_layer2_id = cat_layer2['Id']
        page_id = 1
        for page in range(1, 100):
            product_records_cat = crawl_all_products(cat_layer2_id, page_id, millis)
            if product_records_cat:
                for key in product_records_cat.keys():
                    if key not in product_records:
                        product_records[key] = {}
                    for sub_key in product_records_cat[key].keys():
                        if sub_key not in product_records[key]:
                            product_records[key][sub_key] = []
                        product_records[key][sub_key] = product_records[key][sub_key] + product_records_cat[key][sub_key]
                page_id += 50
                time.sleep(8)
            else:
                break
        # Write into a json file
        with open('data/{}/{}/info.json'.format(key.replace('/', '-'), sub_key.replace('/', '-')), 'w') as f:
            json.dump(product_records, f)



