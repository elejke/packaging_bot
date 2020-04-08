msg_static = {
    "mainmenu": "Привет, ты в главном меню, выбери одно из действий ниже!",
    "error_general": "Oops! Something wrong happened, try /start again",
    "mention_user": "<a href='tg://user?id={telegram}'>link</a>",
}


def msg(key):
    return msg_static.get(key, key)
