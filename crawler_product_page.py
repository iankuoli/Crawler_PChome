# -*- coding: utf-8 -*-

import time
import requests
import json
import os

from utils import find_cat_id, load_json, save_img_from_url


def crawl_product_page(pd_id, millis, headers):
    #
    # Product Page Parsing --------------------------------------------------------------------------
    #
    product_url = 'https://mall.pchome.com.tw/ecapi/ecshop/prodapi/v2/prod/{}-000&fields=' \
                  'Seq,Id,Name,Nick,Store,' \
                  'Price,Pic' \
                  '&_callback=jsonp_prod&{}?_callback=jsonp_prod'.format(pd_id, millis)

    # Get the response of the product
    pd_res_text = requests.get(url=product_url, headers=headers).text
    pd_res_text = pd_res_text.replace("try{jsonp_prod(", "")
    pd_res_text_json = pd_res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
    pd_content = load_json(pd_res_text_json)
    while pd_content is None:
        time.sleep(8)
        pd_res_text = requests.get(url=product_url, headers=headers).text
        pd_res_text = pd_res_text.replace("try{jsonp_prod(", "")
        pd_res_text_json = pd_res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
        pd_content = load_json(pd_res_text_json)

    if len(pd_content) == 0:
        return None

    pd_content_key = list(pd_content.keys())[0]
    pd_content = pd_content[pd_content_key]
    pd_seq = pd_content['Seq']
    pd_id2 = pd_content['Id']
    pd_nick = pd_content['Nick']
    pd_store = pd_content['Store']
    pd_price_m = pd_content['Price']['M']
    pd_price_p = pd_content['Price']['P']
    pd_img_s = 'https://b.ecimg.tw' + pd_content['Pic']['S']
    pd_img_b = 'https://b.ecimg.tw' + pd_content['Pic']['B']

    # Get the product description
    pd_desc_url = 'https://ecapi.pchome.com.tw/cdn/ecshop/prodapi/v2/prod/{}/desc&fields=' \
                  'Id,Stmt,Kword,Slogan' \
                  '&_callback=jsonp_desc?_callback=jsonp_desc'.format(pd_id)
    pd_desc_res_text = requests.get(url=pd_desc_url, headers=headers).text
    pd_desc_res_text = pd_desc_res_text.replace("try{jsonp_desc(", "")
    pd_desc_res_text_json = pd_desc_res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
    pd_desc_content = json.loads(pd_desc_res_text_json)
    pd_desc_content_key = list(pd_desc_content.keys())[0]
    pd_desc_content = pd_desc_content[pd_desc_content_key]
    pd_stmt = pd_desc_content['Stmt']
    pd_slogan = pd_desc_content['Slogan']

    # Images
    pd_imgs_url = 'https://ecapi.pchome.com.tw/cdn/ecshop/prodapi/v2/prod/{}/intro&fields=' \
                  'Pic' \
                  '&_callback=jsonp_intro?_callback=jsonp_intro'.format(pd_id)
    pd_imgs_res_text = requests.get(url=pd_imgs_url, headers=headers).text
    pd_imgs_res_text = pd_imgs_res_text.replace("try{jsonp_intro(", "")
    pd_imgs_res_text_json = pd_imgs_res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
    pd_imgs_content = json.loads(pd_imgs_res_text_json)
    pd_imgs_content_key = list(pd_imgs_content.keys())[0]
    pd_imgs_content = pd_imgs_content[pd_imgs_content_key]
    pd_imgs_url_list = []
    for pd_img in pd_imgs_content:
        if pd_img['Pic']:
            pd_imgs_url_list.append('https://b.ecimg.tw'+pd_img['Pic'])

    # Store information
    store_url = 'https://ecapi.pchome.com.tw/cdn/ecshop/cateapi/v1.5/store&' \
                'id={}&_callback=jsonp_storestyle&{}'.format(pd_id.split('-')[0], millis)
    store_res_text = requests.get(url=store_url, headers=headers).text
    store_res_text = store_res_text.replace("try{jsonp_storestyle(", "")
    store_res_text_json = store_res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
    store_name = json.loads(store_res_text_json)[0]['Name']

    pd_cat_id = pd_id[:4]
    pd_cat_layer1, pd_cat_layer2 = find_cat_id(pd_cat_id)

    product_record = {
        'id': pd_id,
        'id2': pd_id2,
        'cat_id': pd_cat_id,
        'cat_layer1': pd_cat_layer1,
        'cat_layer2': pd_cat_layer2,
        'seq': pd_seq,
        'img_s_url': pd_img_s,
        'img_b_url': pd_img_b,
        'imgs_list_url': pd_imgs_url_list,
        'nick': pd_nick,
        'store': pd_store,
        'price_m': pd_price_m,
        'price_p': pd_price_p,
        'stmt': pd_stmt,
        'slogan': pd_slogan,
        'store_name': store_name,
    }

    root_path = 'data/{}'.format(pd_cat_layer1)
    root_path2 = 'data/{}/{}'.format(pd_cat_layer1.replace('/', '-'), pd_cat_layer2.replace('/', '-'))
    if not os.path.isdir(root_path):
        os.mkdir(root_path)
    if not os.path.isdir(root_path2):
        os.mkdir(root_path2)

    pd_img_s_write_path = os.path.join(root_path2, pd_img_s.split('/')[-1])
    save_img_from_url(pd_img_s, pd_img_s_write_path)

    pd_img_b_write_path = os.path.join(root_path2, pd_img_b.split('/')[-1])
    save_img_from_url(pd_img_b, pd_img_b_write_path)

    for img_url in pd_imgs_url_list:
        img_write_path = os.path.join(root_path2, img_url.split('/')[-1])
        save_img_from_url(img_url, img_write_path)

    return product_record
