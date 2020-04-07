import logging

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import src
from src.errors import HttpError

app = Flask(__name__)
db = SQLAlchemy(app)

from src.models import User, Product, PackingType, fill_product


app.config.from_object('src.config')

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger()

logger.debug('APP STARTED!')


# app.config.from_envvar('ECO_HACK_APP_SETTINGS')

@app.route('/user/<int:user_id>', methods=['GET'])
def user(user_id):
    user = User.query.filter_by(user_id=user_id).first()
    return {
        'id': user.user_id,
        'login': user.login,
        'user_name': user.user_name
    }


@app.route('/product/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    res = Product.query.get(product_id)
    if res is None:
        raise HttpError('Not found', 404)
    return {
        'id': res.product_id,
        'name': res.product_name,
        'img_url': res.product_photo_link,
        'upc': res.upc_a,
        'ean': res.ean_13,
        'packing_type_id': res.packing_type_id,
        'brand_id': res.brand_id
    }


@app.route('/packing_types', methods=['GET'])
def packing_types():
    result = list(
        map(
            lambda packing: {
                'id': packing.packing_type_id,
                'img_url': packing.packing_label_url,
                'code_iso': packing.code_iso,
                'code_gost': packing.code_gost,
                'description': packing.packing_description,
                'examples': packing.packing_examples
            },
            PackingType.query.order_by(
                PackingType.packing_type_id
            ).all()
        )
    )
    return {'result': result}


@app.route('/products', methods=['GET'])
def search_products():
    if 'barcode' in request.args and 'search_query' in request.args:
        raise HttpError('Invalid usage')

    if 'like' in request.args:
        mapped_result = src.models.search_products(request.args['like'])

        return {'result': mapped_result}

    elif 'barcode' in request.args:
        barcode = request.args['barcode']
        products = Product.query.filter_by(upc_a=barcode).all()
        print(products)
        if len(products) == 0:
            products = Product.query.filter_by(ean_13=barcode).all()

        result = list(
            map(
                lambda product: {
                    'id': product.product_id,
                    'name': product.product_name,
                    'img_url': product.product_photo_link
                },
                products
            )
        )

        return {'result': result}
    else:
        raise HttpError('Invalid usage')


@app.route('/product', methods=['PUT', 'POST'])
def add_or_update_product():
    try:
        payload = request.get_json()

        if request.method == 'POST':
            product = Product()
            product = fill_product(product, payload)
            db.session.add(product)

        if request.method == 'PUT':
            if 'product_id' not in payload:
                raise HttpError('Invalid usage')
            product = Product.query.get(payload['product_id'])
            product = fill_product(product, payload)

        db.session.commit()

        return {'id': product.product_id}

    except Exception:
        raise HttpError('Invalid usage. Some required data is not present in the request')


@app.route('/')
def hello():
    return '<h1>Open Recycle Team</h1><h3>Eco-Hack 2020</h2><ul><li>German Novikov</li>' \
           '<li>Polina Tikhonova</li><li>Jaroslav Petrik</li><li>Mikhail Popov</li>' \
           '<li>Dmitry Volovod</li></ul>'


@app.errorhandler(HttpError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response
