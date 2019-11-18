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


# Category information
cat_url = 'https://ecapi.pchome.com.tw/cdn/mall/cateapi/v1/sign' \
          '&tag=newarrival' \
          '&fields=Id,Name,Sort,Nodes' \
          '&_callback=jsonpcb_newarrival' \
          '&{}'.format(millis)
cat_res_text = requests.get(url=cat_url, headers=headers).text
cat_res_text = cat_res_text.replace("try{jsonpcb_newarrival(", "")
cat_res_text_json = cat_res_text.replace(");}catch(e){if(window.console){console.log(e);}}", "")
cat_content = json.loads(cat_res_text_json)

category = {}

for cat in cat_content:
    cat_id = cat['Nodes'][0]['Id'][:2]
    category[cat_id] = cat.copy()
    category[cat_id]['Nodes'] = {}

    for node in cat['Nodes']:
        cat_id2 = node['Id']
        category[cat_id]['Nodes'][cat_id2] = node


def find_cat_id(cat_id):
    """
    Given a category ID, return 1st and 2nd layer name
    :param cat_id: category ID
    :return: 1st layer name, 2nd layer name
    """
    cat_name1 = category[cat_id[:2]]['Name']
    cat_name2 = category[cat_id[:2]]['Nodes'][cat_id]['Name']
    return cat_name1, cat_name2


def load_json(my_json):
    try:
        json_object = json.loads(my_json)
    except ValueError as e:
        return None
    return json_object


def save_img_from_url(img_url, save_path):

    with open(save_path, 'wb') as handle:
        response = requests.get(img_url, stream=True)

        if not response.ok:
            print(response)

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
