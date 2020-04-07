from src.app import db


class User(db.Model):
    user_id = db.Column(db.BIGINT(), primary_key=True)
    user_name = db.Column(db.String(255), unique=False, nullable=False)
    login = db.Column(db.String(255), unique=True, nullable=True)

    def __repr__(self):
        return '<User %r>' % self.login


class Product(db.Model):
    product_id = db.Column(db.BIGINT(), primary_key=True)
    product_name = db.Column(db.String(511), nullable=False)
    product_photo_link = db.Column(db.String(1023))

    upc_a = db.Column(db.String(12))
    ean_13 = db.Column(db.String(13))
    ean_8 = db.Column(db.String(8))

    archived = db.Column(db.Boolean, nullable=False, default=False)

    product_category_id = db.Column(db.BIGINT())
    packing_type_id = db.Column(db.BIGINT())
    brand_id = db.Column(db.BIGINT())

    utkonos_id = db.Column(db.BIGINT())

    def __repr__(self):
        return '<Product %r>' % self.product_name


class Brand(db.Model):
    brand_id = db.Column(db.BIGINT(), primary_key=True, nullable=False)
    brand_name = db.Column(db.String(511), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(15))
    address = db.Column(db.String(511))

    archived = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return '<Brand %r>' % self.brand_name


class PackingType(db.Model):
    packing_type_id = db.Column(db.BIGINT(), primary_key=True, nullable=False)
    packing_label_url = db.Column(db.String(1023))
    code_iso = db.Column(db.String(15))
    code_gost = db.Column(db.String(15))
    packing_description = db.Column(db.String(511))
    packing_examples = db.Column(db.String(511))
    archived = db.Column(db.Boolean(), nullable=False, default=False)

    def __repr__(self):
        return '<Packing_Type %r>' % self.brand_name


class ProductCategory(db.Model):
    category_id = db.Column(db.Integer, primary_key=True, nullable=False)
    category_name = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Product_Category %r>' % self.brand_name


# Вариант поиска по базе продуктов:
# - полнотекстовый поиск по названию товара
# - результаты ранжируются по похожести на запрос
# - отсекается верхние 30
def search_products(search_query):
    regex = f'.*{search_query}.*'

    result_set = db.session.execute(
        'select product_id, product_photo_link, product_name, upc_a, ean_13, '
        'brand_id, similarity(product_name, :search_query) as sim '
        'from product '
        'where product_name ~* :regex order by sim desc limit 30',
        {'search_query': search_query, 'regex': regex})

    return list(map(lambda product: {
        'id': product.product_id,
        'name': product.product_name,
        'img_url': product.product_photo_link,
        'upc': product.upc_a,
        'ean': product.ean_13,
        'brand_id': product.brand_id
    }, result_set))


def fill_product(product: Product, payload: dict) -> Product:
    if 'name' in payload:
        product.product_name = payload['name']
    if 'img_link' in payload:
        product.product_photo_link = payload['img_link']
    if 'upc' in payload:
        product.upc_a = payload['upc']
    if 'ean' in payload:
        product.ean_13 = payload['ean']
    if 'category_id' in payload:
        product.product_category_id = payload['category_id']
    if 'packing_type_ids' in payload and len(payload['packing_type_ids']) > 0:
        # todo - передалать этот момент в базе и модели
        # нужно хранить много упаковок для одного товара
        product.packing_type_id = payload['packing_type_ids'][0]
    if 'brand_id' in payload:
        product.brand_id = payload['brand_id']
    if 'utkonos_id' in payload:
        product.utkonos_id = payload['utkonos_id']

    return product
