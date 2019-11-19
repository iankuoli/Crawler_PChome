# -*- coding: utf-8 -*-

import requests
import json
import time

# Add a time stamp
millis = int(round(time.time() * 1000))
print(millis)

# Pretend to be a common user
user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) ' \
             'AppleWebKit/537.36 (KHTML, like Gecko) ' \
             'Chrome/78.0.3904.97 Safari/537.36'
headers = {'User-Agent': user_agent,
           'server': 'PChome/1.0.4',
           'Referer': 'https://mall.pchome.com.tw/newarrival/'}


def load_json(my_json):
    try:
        json_object = json.loads(my_json)
    except ValueError as e:
        return None
    return json_object


def convert2json(url, func_name):
    """
    Get the response & Parse the content in json format
    :param url:
    :param func_name:
    :return:
    """
    res_text = requests.get(url=url, headers=headers).text
    res_text = res_text.replace("try{" + func_name + "(", "")
    res_text_json = res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
    jd = load_json(res_text_json)
    while jd is None:
        print(res_text_json)
        time.sleep(8)
        res_text = requests.get(url=url, headers=headers).text
        res_text = res_text.replace("try{" + func_name + "(", "")
        res_text_json = res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
        jd = load_json(res_text_json)
    return jd


# Category information
cat_url = 'https://ecapi.pchome.com.tw/cdn/mall/cateapi/v1/sign' \
          '&tag=newarrival' \
          '&fields=Id,Name,Sort,Nodes' \
          '&_callback=jsonpcb_newarrival' \
          '&{}'.format(millis)
cat_content = convert2json(cat_url, 'jsonpcb_newarrival')
category = {}
for cat in cat_content:
    cat_id = cat['Nodes'][0]['Id'][:2]
    category[cat_id] = cat.copy()
    category[cat_id]['Nodes'] = {}

    for node in cat['Nodes']:
        cat_id2 = node['Id']
        category[cat_id]['Nodes'][cat_id2] = node


def find_cat4_id(cat4_id):
    """
    Given a category ID, return 1st and 2nd layer name
    :param cat4_id: category ID
    :return: 1st layer name, 2nd layer name
    """
    cat_name1 = category[cat4_id[:2]]['Name']
    cat_name2 = category[cat4_id[:2]]['Nodes'][cat4_id]['Name']
    return cat_name1, cat_name2


def save_img_from_url(img_url, save_path):

    with open(save_path, 'wb') as handle:
        response = requests.get(img_url, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)

