# -*- coding: utf-8 -*-

import time
import requests
import json

from crawler_product_page import crawl_product_page
from utils import convert2json


def crawl_all_products(cat_id, page, millis):
    product_records = {}

    url = 'https://ecapi.pchome.com.tw/cdn/mall/prodapi/v1/newarrival/prod' \
          '&region={}' \
          '&offset={}' \
          '&limit=50' \
          '&_callback=jsonpcb_newarrival'.format(cat_id, page)
    jd = convert2json(url, 'jsonpcb_newarrival')

    if jd['Rows']:
        products = (jd['Rows'][:])

        for product in products:
            #
            # Profile Parsing -------------------------------------------------------------------------------
            #
            pd_id = product['Id']
            pd_name = product['Name']
            product_record = crawl_product_page(pd_id, millis)
            time.sleep(2)

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
            print('{} / {} ==> ID: {} ; Name: {}'.format(product_record['cat_layer1'], product_record['cat_layer2'],
                                                     product_record['id'], product_record['name']))

        return product_records
    else:
        return None
