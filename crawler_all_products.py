# -*- coding: utf-8 -*-

import time
import requests
import json

from crawler_product_page import crawl_product_page
from utils import load_json


def crawl_all_products(cat_id, page, millis, headers):
    product_records = {}

    url = 'https://ecapi.pchome.com.tw/cdn/mall/prodapi/v1/newarrival/prod' \
          '&region={}' \
          '&offset={}' \
          '&limit=50' \
          '&_callback=jsonpcb_newarrival'.format(cat_id, page)

    # Parse the content in json format
    res_text = requests.get(url=url, headers=headers).text
    res_text = res_text.replace("try{jsonpcb_newarrival(", "")
    res_text_json = res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
    jd = load_json(res_text_json)
    while jd is None:
        time.sleep(8)
        res_text = requests.get(url=url, headers=headers).text
        res_text = res_text.replace("try{jsonpcb_newarrival(", "")
        res_text_json = res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
        jd = json.loads(res_text_json)

    if jd['Rows']:
        products = (jd['Rows'][:])

        for product in products:
            #
            # Profile Parsing -------------------------------------------------------------------------------
            #
            pd_id = product['Id']
            pd_name = product['Name']
            pd_img_s = 'https://b.ecimg.tw' + product['Pic']['S']
            pd_link = 'https://mall.pchome.com.tw/prod/' + product['Id']
            print('Name: {} ; Img: {} ; Link: {}'.format(pd_name, pd_img_s, pd_link))

            time.sleep(1)
            product_record = crawl_product_page(pd_id, millis, headers)

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

        return product_records
    else:
        return None
