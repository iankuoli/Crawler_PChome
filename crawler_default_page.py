import time
import requests
import json
import os

from crawler_product_page import crawl_product_page
from utils import *


product_records = {}

# Category
cat4_id = 'QDAI'
cat4_name = category[cat4_id[:2]]['Nodes'][cat4_id]['Name']
key = category[cat4_id[:2]]['Name']
sub_key = cat4_name

side_bar_url = 'https://ecapi.pchome.com.tw/cdn/ecshop/cateapi/v1.6/region/{}/menu' \
               '&_callback=jsonp_menu&{}?_callback=jsonp_menu'.format(cat4_id, millis)
side_bar_content = convert2json(side_bar_url, 'jsonp_menu')

# Crawling
for cat_layer_1st in side_bar_content:
    for cat_layer_2nd in cat_layer_1st['Nodes']:
        cat6_id = cat_layer_2nd['Id'][:6]
        cat_name = cat_layer_2nd['Name']

        print('Crawling: {} / {} --------------------------------------------------------'.format(cat4_name, cat_name))

        page_id = 1
        for page in range(1, 100):

            # cat6_id = 'QDAI49'
            url_page30 ='https://ecapi.pchome.com.tw/cdn/ecshop/prodapi/v2/store/{}/prod' \
                        '&offset={}&limit=30' \
                        '&fields=Id,Nick,Pic,Price,Discount,isSpec,Name,isCarrier,isSnapUp,isBigCart,isPrimeOnly,PreOrdDate' \
                        '&_callback=top_prod?_callback=top_prod'.format(cat6_id, page_id)
            jd = convert2json(url_page30, 'top_prod')

            if jd:
                for product in jd:
                    time.sleep(2)
                    #
                    # Profile Parsing -------------------------------------------------------------------------------
                    #
                    pd_id = product['Id'][:-4]
                    pd_name = product['Name']
                    pd_nick = product['Nick']
                    pd_img_b = 'https://b.ecimg.tw' + product['Pic']['B']
                    pd_img_s = 'https://b.ecimg.tw' + product['Pic']['S']
                    pd_link = 'https://mall.pchome.com.tw/prod/' + product['Id']
                    product_record = crawl_product_page(pd_id, millis)

                    if not product_record:
                        print(' --------------- 尚未販售! id = {} ; name = {} --------------- '.format(pd_id, pd_name))
                        continue

                    pd_cat_layer1 = product_record['cat_layer1']
                    pd_cat_layer2 = product_record['cat_layer2']
                    if pd_cat_layer1 not in product_records.keys():
                        product_records[pd_cat_layer1] = {}
                    if pd_cat_layer2 not in product_records[pd_cat_layer1].keys():
                        product_records[pd_cat_layer1][pd_cat_layer2] = []
                    product_records[pd_cat_layer1][pd_cat_layer2].append(product_record)
                    print('{} / {} ==> ID: {} ; Name: {}'.format(product_record['cat_layer1'],
                                                                 product_record['cat_layer2'],
                                                                 product_record['id'], product_record['name']))
                page_id += 30
                time.sleep(8)
            else:
                break

# Write into a json file
with open('data/{}/{}/info.json'.format(key.replace('/', '-'), sub_key.replace('/', '-')), 'w') as f:
    json.dump(product_records, f)
