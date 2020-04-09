import requests, json
# from .addproduct import _save_photo
# from lxml import html
from bs4 import BeautifulSoup


def get_all_wrappings():
    data = requests.get("http://84.201.157.204:5000/packing_types").text
    data = json.loads(data)
    data = data['result']
    new_data = []
    keys = ['code_gost', 'code_iso', 'description', 'examples']
    for data_instance in data:
        info = data_instance[keys[2]] if data_instance[keys[2]] is not None else ''
        add_info = ''
        for key in keys[:2]:
            if data_instance[key] is not None:
                add_info = add_info + data_instance[key]
        info = info + '(%s)' % add_info if add_info != '' else info
        descript = data_instance[keys[3]] if data_instance[keys[3]] is not None else ''
        img_url = data_instance['img_url'] if data_instance['img_url'] is not None else ''
        id_ = data_instance['id']
        if info != '':
            new_data.append({"name": info, 'description': descript, 'img_url': img_url, 'id': id_})
    return new_data


def get_product_by_bar_code(barcode):
    data = requests.get("http://84.201.157.204:5000/products?barcode=%s" % barcode).text
    data = json.loads(data)['result']
    if len(data) > 0:
        data = data[0]
        return data['name'], data['id']
    else:
        return 'Этот товар отсутвует в нашей базе', None


def get_product_inline_by_name(name):
    data = requests.get("http://84.201.157.204:5000/products?like=%s" % name).text
    data = json.loads(data)
    data = data['result']
    return data


# def get_product_by_id(id_number):
#     ######## здесь реквест не от нужного запроса!
#     data = requests.get("http://84.201.157.204:5000/products?like=%s" % name).text
#     data = json.loads(data)
#     data = data['result']
#     bar_code = data['ean'] if data['ean'] is not None else data['upc'] if data['upc'] is not None else str(0)
#     return data['name'], bar_code


def api_request(request):
    url = "https://www.utkonos.ru/search?query=" + "+".join(request.split(" ")) + "&search_id="
    text = requests.get(url).text

    soup = BeautifulSoup(text, "lxml")

    item_list = soup.findAll('img', {'decode': 'async'})
    item_list = list(filter(lambda x: "https://img.utkonos.ru/" in str(x), item_list))

    item_list_parsed = []

    for item_ in item_list[:10]:
        try:
            item_list_parsed.append(
                {
                    "utkonos_result_id": item_['src'].split("/")[-1].split(".")[0],
                    "img_url": item_['src'],
                    "name": item_['alt'],
                    "art": item_.parent['href'].replace('/item/', '').split('/')[0]
                }
            )
        except:
            pass

    return item_list_parsed


def try_to_find_bar_code(art):
    url = "https://www.utkonos.ru/item/%s" % art
    text = requests.get(url).text
    soup = BeautifulSoup(text, "lxml")
    images_list = soup.findAll('a', {'class': "goods_view_item - variant_item"})
    for img in images_list:
        if 'data-pic-high' in img.keys():
            pass
            # img_link = "https://www.utkonos.ru" + img['data-pic-high']
            # iu.id, fn, code = _save_photo(img_link)
            # if code is not None:
            #     break


def update_the_existing_product(data):
    requests.put(
        f'http://84.201.157.204:5000/product',
        headers={'Content-Type': 'application/json;charset=utf-8'},
        json=data
    )


def add_the_new_product(data):
    requests.post(
        f'http://84.201.157.204:5000/product',
        headers={'Content-Type': 'application/json;charset=utf-8'},
        json=data
    )
