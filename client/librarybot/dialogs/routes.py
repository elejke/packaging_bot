import logging

logger = logging.getLogger(__package__)

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler

from librarybot.models import Chat

from .addproduct import state_map as addproduct_state_map
from .utility import get_update_context
from .messages import msg


def crossroad(bot, update):
    logger.debug("/crossroad")
    agent, chat, botuser = get_update_context(update, state=Chat.MAINMENU)

    text = update.message.text
    logger.debug(config().get_handlers())
    for roadkey, (road_state, road) in config().get_handlers().items():
        if roadkey == text:
            chat.state = road_state
            chat.save()
            return road(bot, update)
    update.message.reply_text(msg("unrecognized_option_crossroad"))
    return ConversationHandler.END


class config:
    state_map_list = [
        addproduct_state_map
    ]

    def get_states(self):
        states = {Chat.MAINMENU: [MessageHandler(Filters.text, crossroad)]}
        for state_map in self.state_map_list:
            states.update(state_map["states"])
        return states

    def get_keyboard(self):
        return [[state_map["__meta__"]["caption"]] for state_map in self.state_map_list]

    def get_handlers(self):
        return {
            state_map["__meta__"]["caption"]: [
                state_map["__meta__"]["entry_state"],
                state_map["__meta__"]["entry_point"],
            ]
            for state_map in self.state_map_list
        }
