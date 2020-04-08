import logging
import requests

from uuid import uuid4

from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent
from telegram.utils.helpers import escape_markdown

from lxml import html
from bs4 import BeautifulSoup
from .db_requests import *


def inlinequery(bot, update):
    """Handle the inline query.

    Example of api_results:
    >>> results_parsed = [{
    >>>         "result_id": 0,
    >>>         "name": "Молоко М Лианозовское ультрапастеризованное 3,2%, 950г",
    >>>        "img_url": "https://www.utkonos.ru/images/photo/3074/3074902H.jpg"
    >>> }]

    """
    inline_bot_type = None
    results = []

    if ':' in update.inline_query.query:
        query = update.inline_query.query.split(':')
        inline_bot_type = query[0]
        if len(query) > 1:
            query = query[1].strip()
        else:
            query = ''
    else:
        query = update.inline_query.query

    if inline_bot_type == 'Каталог':
        # api_results = get_product_inline_by_name(query)
        api_results = api_request(query)
        results = []

        for result_ in api_results:
            bar_code = 'Арт. %s' % result_['art']
            # bar_code = result_['ean'] if result_['ean'] is not None else \
            #            result_['upc'] if result_['upc'] is not None else str(0)
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=result_['name'],
                    thumb_url=result_['img_url'],
                    input_message_content=InputTextMessageContent('%s %s' % (bar_code, result_['name'])))
                # input_message_content=InputTextMessageContent(result_['name']))
                # result_['name']))

                # result_['name'])
                #
            )
        results = results + [InlineQueryResultArticle(
            id=uuid4(),
            title="Здесь нет моего продукта",
            # thumb_url=result_['img_url'],
            input_message_content=InputTextMessageContent("000 Здесь нет моего продукта"))]
    elif inline_bot_type == 'Упаковки':
        api_results = get_all_wrappings()
        results = []

        for result_ in api_results:
            results.append(
                InlineQueryResultArticle(
                    id=uuid4(),
                    title=result_['name'],
                    description=result_['description'],
                    thumb_url=result_['img_url'],
                    input_message_content=InputTextMessageContent('%s. %s' % (result_['id'],
                                                                              result_['name'])))
                # result_['name']))

                # result_['name'])
                #
            )

    update.inline_query.answer(results)
