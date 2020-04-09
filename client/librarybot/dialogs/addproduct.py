import logging
import uuid

logger = logging.getLogger(__package__)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler

# from django.conf import settings
# from django_telegrambot.apps import DjangoTelegramBot

# from .models import Book, BookAuthor, BookLanguage, Chat, BotUser
from librarybot.models import BotUser, Chat, ImageUpload
from .utility import tg_handler
from .messages import msg
from .db_requests import *
# from telegram import ParseMode
# import numpy as np

from pyzbar import pyzbar
from PIL import Image
# import cv2


def decode_photo(path_to_photo):
    # image = cv2.imread(path_to_photo)
    image = Image.open(path_to_photo)
    barcodes = pyzbar.decode(image)
    barcodeData = None
    for barcode in barcodes:
        barcodeData = barcode.data.decode("utf-8")
    return barcodeData


def _save_photo(bot_photo_file):
    fn = "uploads/{}.jpg".format(uuid.uuid4())
    bot_photo_file.download(fn)
    iu = ImageUpload.objects.create(image=fn)
    code = decode_photo(fn)
    return iu.id, fn, code


@tg_handler(state=Chat.ADD_NEW_PRODUCT_MAINMENU)
def add_new_product_mainmenu(bot, update, agent, chat, botuser):
    reply = ([msg("mainmenu")],
             {'reply_markup': ReplyKeyboardMarkup([[state_map["__meta__"]["caption"]]], one_time_keyboard=True)})
    return reply, Chat.ADD_NEW_PRODUCT_ASK_FIRST


@tg_handler(state=Chat.ADD_NEW_PRODUCT_ASK_FIRST)
def add_new_product_ask_first(bot, update, agent, chat, botuser):
    reply = (["Привет, я Эко-бот, и я помогу тебе зарегистрировать новый продукт"], {
        'reply_markup': ReplyKeyboardMarkup(
            [['Cфотографировать штрих код или ввести номер'], ['Ввести вручную название'],
             # ['Ввести вручную номер штрих-кода']
             ], one_time_keyboard=True)})
    return reply, Chat.ADD_NEW_PRODUCT_CROSS


@tg_handler(state=Chat.ADD_NEW_PRODUCT_CROSS)
def add_new_product_cross(bot, update, agent, chat, botuser):
    if (
            update.message.text == 'Cфотографировать штрих код или ввести номер'):  # or (update.message.text == 'Закончить'):
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PHOTO
        reply = "Пожалуйста, сфотографируйте штрих-код так, чтобы не было бликов и заломов"
    # elif (update.message.text == 'Ввести вручную номер штрих-кода'):
    #     next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_NUMBER
    #     reply = "Введите номер штрих-кода"
    else:
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME
        reply = (["Пожалуйста, найдите продукт в каталоге"], {'reply_markup': InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Войти в каталог", switch_inline_query_current_chat="Каталог: ")]])})
    return reply, next_state, {'': ''}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_PHOTO)
def add_new_product_wait_for_photo(bot, update, agent, chat, botuser):
    if (update.message.text == 'Ввести название вручную'):
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME
        reply = (["Пожалуйста, найдите продукт в каталоге"], {'reply_markup': InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Войти в каталог", switch_inline_query_current_chat="Каталог: ")]])})
        upd_dict = {"": ""}
    elif (update.message.text == 'Нет, спасибо я позже'):
        next_state = Chat.ADD_NEW_PRODUCT_MAINMENU  # Chat.ADD_NEW_PRODUCT_END
        reply = (['Будем ждать вас снова!'],
                 {'reply_markup': ReplyKeyboardMarkup([['Вернуться в главное меню']], one_time_keyboard=True)})
    elif len(update.message.photo) != 0:
        photo = bot.get_file(update.message.photo[-1].file_id)
        photo_id, path_to_image, product_number = _save_photo(photo)
        if product_number is None:
            reply = (["Штрих-код не распознался, попробуйте снова"],
                     {'reply_markup': ReplyKeyboardMarkup([['Ввести название вручную']], one_time_keyboard=True)})
            next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PHOTO
            upd_dict = {"": ""}
        else:
            product_number = int(update.message.text)
            product_name, product_id = get_product_by_bar_code(str(product_number))
            logger.debug('PRODUCT DATA %s %s' % (product_name, product_id))
            if product_id is None:
                reply = (["Этот товар отсутвует в нашей базе, пожалуйста, попробуйте найти его в каталоге"], {
                    'reply_markup': InlineKeyboardMarkup([
                        [InlineKeyboardButton(text="Войти в каталог", switch_inline_query_current_chat="Каталог: ")]])})
                next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME
                upd_dict = {'product_number': int(product_number)}
            else:

                reply = (['%s\nШтрих-код: %d' % (product_name, product_number)], {
                    'reply_markup': ReplyKeyboardMarkup([['Да'], ['Нет, ввести штрих-код'], ['Нет, ввести название']],
                                                        one_time_keyboard=True)})
                next_state = Chat.ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME
                upd_dict = {'product_name': product_name, 'product_id': product_id,
                            'product_number': int(product_number)}
    else:
        product_number = int(update.message.text)
        product_name, product_id = get_product_by_bar_code(str(product_number))
        if product_id is None:
            reply = (["Этот товар отсутвует в нашей базе, пожалуйста, попробуйте найти его в каталоге"], {
                'reply_markup': InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Войти в каталог", switch_inline_query_current_chat="Каталог: ")]])})
            next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME
            upd_dict = {'product_number': int(product_number)}
        else:

            reply = (['%s\nШтрих-код: %d' % (product_name, product_number)], {
                'reply_markup': ReplyKeyboardMarkup([['Да'], ['Нет, ввести штрих-код'], ['Нет, ввести название']],
                                                    one_time_keyboard=True)})
            next_state = Chat.ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME
            upd_dict = {'product_name': product_name, 'product_id': product_id, 'product_number': int(product_number)}
    return reply, next_state, upd_dict


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_NUMBER)
def add_new_product_wait_for_number(bot, update, agent, chat, botuser):
    product_number = int(update.message.text)
    product_name = get_product_by_bar_code(str(product_number))
    reply = (['%s\nШтрих-код: %d' % (product_name, product_number)],
             {'reply_markup': ReplyKeyboardMarkup([['Да'], ['Нет, ввести название вручную']], one_time_keyboard=True)})
    return reply, Chat.ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME, {'product_name': product_name,
        'product_number': int(product_number)}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME)
def add_new_product_wait_for_product_name(bot, update, agent, chat, botuser):
    art_flag = False
    meta_data = chat.get_meta()
    if update.message.text.startswith('Арт.'):
        art_flag = True
        # code = try_to_find_bar_code(art)
        # if code is not None:
        #     product_number = int(code)
        # else:
        product_number = update.message.text.replace('Арт.', '').strip().split(' ')[0]
        product_number = int(product_number)
        product_name = update.message.text.replace('Арт.', '').replace(str(product_number) + ' ', '', 1)
    elif ('product_number' in meta_data.keys()) and (not '000 Здесь нет моего продукта' in update.message.text):
        product_number = meta_data['product_number']
        product_name = update.message.text
    else:
        # try:
        product_number = update.message.text.split(' ')[0]
        product_name = update.message.text.replace(product_number + ' ', '', 1)
        product_number = int(
            product_number)  # except:  #     reply = (["Пожалуйста, выберете товар из каталога"],  #              {'reply_markup': InlineKeyboardMarkup(  #                  [  #                      # [InlineKeyboardButton(text="Вернуться в главное меню")],  #                   [InlineKeyboardButton(text="Войти в каталог",  #                                         switch_inline_query_current_chat="Каталог: ")]])}  #               )  #     next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME  #     return reply, next_state
    if ('Здесь нет моего продукта' in product_name):
        chat_meta = chat.get_meta()
        if 'product_number' in chat_meta.keys():
            next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME  # Chat.ADD_NEW_PRODUCT_END
            reply = ([
                         "Возможно, в нашей базе еще нет этого товара. Вы можете ввести сейчас название нового товара или попробовать поискать в нашем каталоге еще раз."],
                     {'reply_markup': InlineKeyboardMarkup([# [InlineKeyboardButton(text="Вернуться в главное меню")],
                         [InlineKeyboardButton(text="Войти в каталог",
                                               switch_inline_query_current_chat="Каталог: ")]])})
            upd_dict = {"absolutely_new_product": "True"}
        else:
            next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PHOTO
            reply = (["Давайте попробуем найти по штрихкоду. Сфотографируйте его или введите номер"],
                     {'reply_markup': ReplyKeyboardMarkup([['Нет, спасибо я позже']], one_time_keyboard=True)})
            upd_dict = {"": ""}
    else:
        reply = (['Правильно ли мы определили продукт?\n%s\n%s: %s' % (
        product_name, 'Артикул' if art_flag else 'Штрих-код', product_number)], {
                     'reply_markup': ReplyKeyboardMarkup([['Да'], ['Нет, ввести штрихкод'], ['Нет, ввести название']],
                                                         one_time_keyboard=True)})
        next_state = Chat.ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME
        # if art_flag:
        upd_dict = {'product_name': product_name, 'product_number': int(product_number),
                    'art_flag': art_flag}  # else:  #     upd_dict = {'product_name': product_name,  #                 'product_number': int(product_number),  #                 'art_flag':art_flag}
    return reply, next_state, upd_dict


@tg_handler(state=Chat.ADD_NEW_PRODUCT_CONFIRM_PRODUCT_NAME)
def add_new_product_confirm_product_name(bot, update, agent, chat, botuser):
    productname = chat.get_meta()['product_name']
    reply = (["Продукт определен верно?"], # ["Вы подтверждаете, что это %s?"%productname],
             {'reply_markup': ReplyKeyboardMarkup([['Да'], ['Нет, ввести название вручную']], one_time_keyboard=True)})
    return reply, Chat.ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME, {"": ""}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME)
def add_new_product_cross_product_name(bot, update, agent, chat, botuser):
    if (update.message.text == 'Да'):
        next_state = Chat.ADD_NEW_PRODUCT_ASK_TYPE_OF_WRAPPER
        reply = (["Пожалуйста, выберите нужную упаковку в каталоге"], {'reply_markup': InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Войти в каталог", switch_inline_query_current_chat="Упаковки: ")]])})

    elif ('Нет, ввести название' in update.message.text):
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME
        reply = (["Пожалуйста, найдите продукт в каталоге"], {'reply_markup': InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Войти в каталог", switch_inline_query_current_chat="Каталог: ")]])})
    elif ('Нет, ввести штрихкод' in update.message.text):
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_NUMBER
        reply = "Пожалуйста, введите номер продукта или сфотографируйте штрих-код"
    return reply, next_state, {"": ""}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_ASK_TYPE_OF_WRAPPER)
def add_new_product_ask_type_of_wrapper(bot, update, agent, chat, botuser):
    # try:
    # types_of_wrapper = [int(num.strip()) for num in update.message.text.split(',')]
    # number_of_wrapper = len(types_of_wrapper)
    ids_of_wrapper = update.message.text.split('.')[0]
    types_of_wrapper = update.message.text.replace(ids_of_wrapper + '.', '')
    number_of_wrapper = 1
    next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_NAME
    reply = (
    ['Введите имя производителя'], {'reply_markup': ReplyKeyboardMarkup([['Пропустить']], one_time_keyboard=True)})

    # next_state = Chat.ADD_NEW_PRODUCT_MAINMENU  # Chat.ADD_NEW_PRODUCT_END
    # reply = (['Хорошо, спасибо. Вы ввели %d упаков%s' % (len(types_of_wrapper),
    #                                                    'ку' if len(types_of_wrapper) == 1 else 'ок' if len(
    #                                                        types_of_wrapper) > 5 else 'ки')],
    #          {'reply_markup': ReplyKeyboardMarkup([['Вернуться в главное меню']], one_time_keyboard=True)})
    # except ValueError:
    #     types_of_wrapper = []
    #     number_of_wrapper = 0
    #     reply = 'Кажется, вы ошиблись и ввели какие-то буквы. Пожалуйста, попробуйте снова'
    #     next_state = Chat.ADD_NEW_PRODUCT_ASK_TYPE_OF_WRAPPER
    # dict_to_untype = {}
    return reply, next_state, {"types_of_wrapper": types_of_wrapper, 'number_of_wrapper': number_of_wrapper,
                               'ids_of_wrapper': ids_of_wrapper}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_NAME)
def add_new_product_wait_for_manufacturer_name(bot, update, agent, chat, botuser):
    if update.message.text != 'Пропустить':
        manufacturer_name = update.message.text
    else:
        manufacturer_name = ''
    reply = (
    ['Введите почту производителя'], {'reply_markup': ReplyKeyboardMarkup([['Пропустить']], one_time_keyboard=True)})
    next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_EMAIL
    return reply, next_state, {"manufacturer_name": manufacturer_name}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_EMAIL)
def add_new_product_wait_for_manufacturer_email(bot, update, agent, chat, botuser):
    if update.message.text != 'Пропустить':
        manufacturer_email = update.message.text
    else:
        manufacturer_email = ''
    reply = (
    ['Введите адрес производителя'], {'reply_markup': ReplyKeyboardMarkup([['Пропустить']], one_time_keyboard=True)})
    next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_ADDRESS
    return reply, next_state, {"manufacturer_email": manufacturer_email}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_ADDRESS)
def add_new_product_wait_for_manufacturer_address(bot, update, agent, chat, botuser):
    if update.message.text != 'Пропустить':
        manufacturer_address = update.message.text
    else:
        manufacturer_address = ''
    reply = (['Введите номер телефона производителя'],
             {'reply_markup': ReplyKeyboardMarkup([['Пропустить']], one_time_keyboard=True)})
    next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_PHONE
    return reply, next_state, {"manufacturer_address": manufacturer_address}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_PHONE)
def add_new_product_wait_for_manufacturer_phone(bot, update, agent, chat, botuser):
    if update.message.text != 'Пропустить':
        manufacturer_phone = update.message.text
    else:
        manufacturer_phone = ''
    #   reply = (['Введите ваше ФИО'],
    #            {'reply_markup': ReplyKeyboardMarkup([['Пропустить']], one_time_keyboard=True)})
    meta_data = chat.get_meta()
    if 'user_name' not in meta_data.keys():
        reply = (['Введите ваше ФИО'], {'reply_markup': ReplyKeyboardRemove()})
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_USER_NAME
    else:
        reply = (['Проверьте правильность введенных данных',
                  add_new_product_string_generation(chat, manufacturer_phone=manufacturer_phone)[0]], {
                     'reply_markup': ReplyKeyboardMarkup(
                         [['Все верно'], ['Исправить информацию о прозводителе'], ['Исправить информацию о себе'],
                          ['Заполнить товар заново']], one_time_keyboard=True)})
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_DATA_CHECK
    return reply, next_state, {"manufacturer_phone": manufacturer_phone}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_USER_NAME)
def add_new_product_wait_for_user_name(bot, update, agent, chat, botuser):
    if update.message.text != 'Пропустить':
        user_name = update.message.text
    else:
        user_name = ''
    reply = 'Введите вашу почту'
    # reply = (['Введите вашу почту'],
    #          {'reply_markup': ReplyKeyboardMarkup([['Пропустить']], one_time_keyboard=True)})
    next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_USER_EMAIL
    return reply, next_state, {"user_name": user_name}


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_USER_EMAIL)
def add_new_product_wait_for_user_email(bot, update, agent, chat, botuser):
    if update.message.text != 'Пропустить':
        user_email = update.message.text
    else:
        user_email = ''
    reply = (
    ['Проверьте правильность введенных данных', add_new_product_string_generation(chat, user_email=user_email)[0]], {
        'reply_markup': ReplyKeyboardMarkup(
            [['Все верно'], ['Исправить информацию о прозводителе'], ['Исправить информацию о себе'],
             ['Заполнить товар заново']], one_time_keyboard=True)})
    next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_DATA_CHECK
    return reply, next_state, {"user_email": user_email}


def add_new_product_string_generation(chat, user_email=None, manufacturer_phone=None):
    meta_data = chat.get_meta()
    product_name = meta_data['product_name']
    product_number = str(meta_data['product_number'])
    product_data = ', '.join([product_name, product_number])
    packing_data = meta_data['types_of_wrapper']
    packing_number = meta_data['number_of_wrapper']
    manufacturer_name = meta_data['manufacturer_name']
    manufacturer_email = meta_data['manufacturer_email']
    manufacturer_address = meta_data['manufacturer_address']
    manufacturer_phone = meta_data['manufacturer_phone'] if manufacturer_phone is None else manufacturer_phone
    manufacturer_data = ''
    for part_data in [manufacturer_email, manufacturer_address, manufacturer_phone]:
        if part_data != '':
            manufacturer_data = manufacturer_data + part_data + ', '
    manufacturer_data = manufacturer_data if manufacturer_data == '' else manufacturer_data[:-2]
    user_name = meta_data['user_name']
    if user_email is None:
        user_email = meta_data['user_email']
    user_data = ', '.join([user_name, user_email])
    base_string = '''Продукт: %s
Упаковка: %s
Производитель:%s, 
%s
Ваши данные: %s''' % (product_data, packing_data, manufacturer_name, manufacturer_data, user_data)
    materials = 'этот материал' if packing_number == 1 else 'эти материалы'
    petition_string = 'Я, %s [%s], прошу компанию %s [%s], заменить на товаре %s следующую упаковку: %s. Ввиду того, что %s являются трудноперерабатываемыми и загрящняю окружающую среду.' % (
        user_name, user_email, manufacturer_name, manufacturer_data, product_data, packing_data, materials)
    return base_string, petition_string


@tg_handler(state=Chat.ADD_NEW_PRODUCT_WAIT_FOR_DATA_CHECK)
def add_new_product_wait_for_data_check(bot, update, agent, chat, botuser):
    if update.message.text == 'Все верно':
        meta_data = chat.get_meta()
        if 'absolutely_new_product' in meta_data.keys():
            bar_code = meta_data['product_number']
            art_flag = False
            if 'art_flag' in meta_data.keys():
                art_flag = meta_data['art_flag']
            bar_code_type = 'utkonos_id' if art_flag else 'upc' if len(str(art_flag)) == 12 else 'ean'
            data = {'name': meta_data['product_name'],  # обязательный
                bar_code_type: bar_code, 'packing_type_ids': [meta_data['ids_of_wrapper']]
                # 'img_link': 'https://i.pinimg.com/736x/24/81/35/2481351b7b8249144b6983d8c3c19a20.jpg',
                # 'upc': '123456789012',
                # 'ean': '1234567890123',
                # 'category_id': '1234567890123',
                # 'packing_type_ids': ['21', '1'],
                # 'brand_id': '1'
                # 'utkonos_id': '12345'
            }
            add_the_new_product(data)
            reply = ([
                         'Мы сохранили добавленный вами продукт! Надеемся, что вы отправите производителю обращение с просьбой, заменить упаковку.'],
                     {'reply_markup': ReplyKeyboardMarkup(
                         [['Получить текст петиции'], ['Подписать коллективное обращение'],
                          ['Вернуться в главное меню']], one_time_keyboard=True)})
            next_state = Chat.ADD_NEW_PRODUCT_PETITION_AND_QUIT
        else:
            bar_code = meta_data['product_number']
            art_flag = False
            if 'art_flag' in meta_data.keys():
                art_flag = meta_data['art_flag']
            bar_code_type = 'utkonos_id' if art_flag else 'upc' if len(str(art_flag)) == 12 else 'ean'
            data = {'product_id': meta_data['product_name'],  # обязательный
                'name': meta_data['product_name'], bar_code_type: bar_code,
                'packing_type_ids': [meta_data['ids_of_wrapper']]}
            update_the_existing_product(data)
            reply = (['Надеемся, что вы отправите производителю обращение с просьбой, заменить упаковку.'], {
                'reply_markup': ReplyKeyboardMarkup(
                    [['Получить текст петиции'], ['Подписать коллективное обращение'], ['Вернуться в главное меню']],
                    one_time_keyboard=True)})
            next_state = Chat.ADD_NEW_PRODUCT_PETITION_AND_QUIT
    elif update.message.text == 'Исправить информацию о прозводителе':
        reply = 'Пожалуйста, введите имя производителя'
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_NAME
    elif update.message.text == 'Исправить информацию о себе':
        reply = (['Пожалуйста, введите свое ФИО'], {'reply_markup': ReplyKeyboardRemove()})
        next_state = Chat.ADD_NEW_PRODUCT_WAIT_FOR_USER_NAME
    elif update.message.text == 'Заполнить товар заново':
        meta = chat.get_meta()
        for key in ['product_name', 'product_number', 'types_of_wrapper', 'number_of_wrapper', 'manufacturer_name',
                    'manufacturer_email', 'manufacturer_address', 'manufacturer_phone', 'user_name', 'user_email']:
            meta.pop(key)
        chat.save_meta(meta)
        reply = (["Выберете поиск товар по штрих коду или по название"], {'reply_markup': ReplyKeyboardMarkup(
            [['Cфотографировать штрих код или ввести номер'], ['Ввести вручную название'],
             # ['Ввести вручную номер штрих-кода']
             ], one_time_keyboard=True)})
        next_state = Chat.ADD_NEW_PRODUCT_CROSS
    return reply, next_state


@tg_handler(state=Chat.ADD_NEW_PRODUCT_PETITION_AND_QUIT)
def add_new_product_petition_and_quit(bot, update, agent, chat, botuser):
    if update.message.text == 'Получить текст петиции':
        petition_text = add_new_product_string_generation(chat)[1]
        reply = (['Благодарим за отправку петиции! Также вы можете подписать коллективное обращение!', petition_text], {
            'reply_markup': ReplyKeyboardMarkup(
                [['Получить текст петиции'], ['Подписать коллективное обращение'], ['Вернуться в главное меню']],
                one_time_keyboard=True)})
        next_state = Chat.ADD_NEW_PRODUCT_PETITION_AND_QUIT
        upd_dict = {"petition": True}
    elif update.message.text == 'Подписать коллективное обращение':
        reply = ([
                     "Чтобы подписать обращение, пожалуйста, введите свой e-mail повторно. Внимание! Этот e-mail должен совпадать с e-mail'ом, введеным ранее, в противном случае ваша заявка в коллективное бращение будет отклонена."],
                 {'reply_markup': ReplyKeyboardRemove()})
        next_state = Chat.ADD_NEW_PRODUCT_SIGN_APPEAL
        upd_dict = {"": ""}  # upd_dict = {"appeal": True}
    elif update.message.text == 'Вернуться в главное меню':
        reply = (['Благодарим вас, за Ваш вклад!'],
                 {'reply_markup': ReplyKeyboardMarkup([[state_map["__meta__"]["caption"]]], one_time_keyboard=True)})
        upd_dict = {"": ""}
        next_state = Chat.ADD_NEW_PRODUCT_ASK_FIRST
    return reply, next_state, upd_dict


@tg_handler(state=Chat.ADD_NEW_PRODUCT_SIGN_APPEAL)
def add_new_product_sign_appeal(bot, update, agent, chat, botuser):
    signing_email = update.message.text
    user_email = chat.get_meta()['user_email']
    if signing_email != user_email:
        reply = (["Простите, но ваши e-mail'ы не свопадают"], {'reply_markup': ReplyKeyboardMarkup(
            [['Получить текст петиции'], ['Подписать коллективное обращение'], ['Вернуться в главное меню']],
            one_time_keyboard=True)})
        next_state = Chat.ADD_NEW_PRODUCT_PETITION_AND_QUIT
        upd_dict = {"": ""}
    else:
        reply = (["Спасибо, ваш голос учтен!"], {'reply_markup': ReplyKeyboardMarkup(
            [['Получить текст петиции'], ['Подписать коллективное обращение'], ['Вернуться в главное меню']],
            one_time_keyboard=True)})
        next_state = Chat.ADD_NEW_PRODUCT_PETITION_AND_QUIT
        upd_dict = {"appeal": True}
    return reply, next_state, upd_dict


@tg_handler(state=Chat.ADD_NEW_PRODUCT_END)
def add_new_product_end(bot, update, agent, chat, botuser):
    reply = (["конец"], {'reply_markup': ReplyKeyboardRemove()})
    return reply, Chat.MAINMENU, {"": ""}


state_map = {"__meta__": {"caption": 'Зарегистрировать новый продукт', "entry_state": Chat.ADD_NEW_PRODUCT_ASK_FIRST,
    "entry_point": add_new_product_ask_first, },
    "states": {Chat.ADD_NEW_PRODUCT_ASK_FIRST: [MessageHandler(Filters.text, add_new_product_ask_first)],
        Chat.ADD_NEW_PRODUCT_CROSS: [MessageHandler(Filters.text, add_new_product_cross)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_PHOTO: [MessageHandler(Filters.photo, add_new_product_wait_for_photo),
                                              MessageHandler(Filters.text, add_new_product_wait_for_photo)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_NUMBER: [MessageHandler(Filters.text, add_new_product_wait_for_number)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME: [
            MessageHandler(Filters.text, add_new_product_wait_for_product_name)],
        Chat.ADD_NEW_PRODUCT_CONFIRM_PRODUCT_NAME: [MessageHandler(Filters.text, add_new_product_confirm_product_name)],
        Chat.ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME: [MessageHandler(Filters.text, add_new_product_cross_product_name)],
        Chat.ADD_NEW_PRODUCT_ASK_TYPE_OF_WRAPPER: [MessageHandler(Filters.text, add_new_product_ask_type_of_wrapper)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_NAME: [
            MessageHandler(Filters.text, add_new_product_wait_for_manufacturer_name)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_EMAIL: [
            MessageHandler(Filters.text, add_new_product_wait_for_manufacturer_email)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_ADDRESS: [
            MessageHandler(Filters.text, add_new_product_wait_for_manufacturer_address)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_PHONE: [
            MessageHandler(Filters.text, add_new_product_wait_for_manufacturer_phone)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_USER_NAME: [MessageHandler(Filters.text, add_new_product_wait_for_user_name)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_USER_EMAIL: [MessageHandler(Filters.text, add_new_product_wait_for_user_email)],
        Chat.ADD_NEW_PRODUCT_WAIT_FOR_DATA_CHECK: [MessageHandler(Filters.text, add_new_product_wait_for_data_check)],
        Chat.ADD_NEW_PRODUCT_PETITION_AND_QUIT: [MessageHandler(Filters.text, add_new_product_petition_and_quit)],
        Chat.ADD_NEW_PRODUCT_SIGN_APPEAL: [MessageHandler(Filters.text, add_new_product_sign_appeal)],
        Chat.ADD_NEW_PRODUCT_END: [MessageHandler(Filters.text, add_new_product_end)],
        Chat.ADD_NEW_PRODUCT_MAINMENU: [MessageHandler(Filters.text, add_new_product_mainmenu)]}, }

# remember that Filters filter the response to previous chain element :(
