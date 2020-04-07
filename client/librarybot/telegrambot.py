import logging

logger = logging.getLogger(__package__)

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, InlineQueryHandler
from django.conf import settings
from django_telegrambot.apps import DjangoTelegramBot

from .models import Chat, BotUser

from .dialogs.routes import config as route_config
from .dialogs.messages import msg
from .dialogs.inline_bot import inlinequery


def cancel(bot, update):
    logger.debug("/cancel @{}".format(update.message.from_user.username))
    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "{}" caused error "{}"'.format(update, error))


def start(bot, update):
    logger.debug("/start @{}".format(update.message.from_user.username))
    agent = update.message.from_user.id

    # removing all previous chats with this agent
    Chat.objects.filter(agent=agent).delete()
    # starting chat
    chat = Chat.objects.create(agent=agent)
    chat.state = Chat.MAINMENU
    chat.save()

    botuser = BotUser.objects.filter(userID=agent).first()
    if botuser is None:
        botuser = BotUser.objects.create(userID=agent)

    update.message.reply_text(
        msg("mainmenu"),
        reply_markup=ReplyKeyboardMarkup(
            route_config().get_keyboard(), one_time_keyboard=True
        ),
    )

    return Chat.MAINMENU


def main():
    logger.info("Loading handlers for telegram bot")

    dispatcher = DjangoTelegramBot.dispatcher

    states = route_config().get_states()
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states=states,
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
    )
    dispatcher.add_handler(conv_handler)
    dispatcher.add_error_handler(error)
    dispatcher.add_handler(InlineQueryHandler(inlinequery))