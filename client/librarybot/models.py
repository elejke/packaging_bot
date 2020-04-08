import json

from django.db import models


class ImageUpload(models.Model):
    image = models.ImageField(upload_to="")


class BotUser(models.Model):
    name = models.CharField(max_length=1000, null=True, blank=True)
    username = models.CharField(max_length=1000)
    userID = models.CharField(max_length=200, null=True, blank=True)
    event = models.CharField(max_length=1000, null=True, blank=True)
    participant_number = models.CharField(max_length=1000, null=True, blank=True)


    def __str__(self):
        return f"@{self.username}"



class Chat(models.Model):
    """
    Telegram chat state.
    """

    # fmt: off
    (
        IDLE, 
        END,
        MAINMENU,
        ADD_NEW_PRODUCT_MAINMENU,
        ADD_NEW_PRODUCT_ASK_FIRST,
        ADD_NEW_PRODUCT_CROSS,
        ADD_NEW_PRODUCT_WAIT_FOR_PHOTO,
        ADD_NEW_PRODUCT_WAIT_FOR_NUMBER,
        ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME,
        ADD_NEW_PRODUCT_CONFIRM_PRODUCT_NAME,
        ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME,
        ADD_NEW_PRODUCT_ASK_TYPE_OF_WRAPPER,
        ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_NAME,
        ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_EMAIL,
        ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_ADDRESS,
        ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_PHONE,
        ADD_NEW_PRODUCT_WAIT_FOR_USER_NAME,
        ADD_NEW_PRODUCT_WAIT_FOR_USER_EMAIL,
        ADD_NEW_PRODUCT_WAIT_FOR_DATA_CHECK,
        ADD_NEW_PRODUCT_PETITION_AND_QUIT,
        ADD_NEW_PRODUCT_SIGN_APPEAL,
        ADD_NEW_PRODUCT_END
    ) = range(22)

    # for verbosity
    CHAT_STATES = (
        (IDLE, "<<Idle>>"),
        (END, "<<Chat ended>>"),
        (MAINMENU, "/main"),
        (ADD_NEW_PRODUCT_MAINMENU, "/add_new_product/main_menu"),
        (ADD_NEW_PRODUCT_ASK_FIRST, '/add_new_product/ask_first'),
        (ADD_NEW_PRODUCT_CROSS, '/add_new_product/cross'),
        (ADD_NEW_PRODUCT_WAIT_FOR_PHOTO, '/add_new_product/wait_for_photo'),
        (ADD_NEW_PRODUCT_WAIT_FOR_NUMBER, '/add_new_product/wait_for_number'),
        (ADD_NEW_PRODUCT_WAIT_FOR_PRODUCT_NAME, '/add_new_product/wait_for_product_name'),
        (ADD_NEW_PRODUCT_CONFIRM_PRODUCT_NAME, '/add_new_product/confirm_product_name'),
        (ADD_NEW_PRODUCT_CROSS_PRODUCT_NAME, '/add_new_product/cross_product_name'),
        (ADD_NEW_PRODUCT_ASK_TYPE_OF_WRAPPER, '/add_new_product/ask_type_of_wrapper'),
        (ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_NAME, '/add_new_product/wait_for_manufacturer_name'),
        (ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_EMAIL, '/add_new_product/wait_for_manufacturer_email'),
        (ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_ADDRESS, '/add_new_product/wait_for_manufacturer_address'),
        (ADD_NEW_PRODUCT_WAIT_FOR_MANUFACTURER_PHONE, '/add_new_product/wait_for_manufacturer_phone'),
        (ADD_NEW_PRODUCT_WAIT_FOR_USER_NAME, '/add_new_product/wait_for_user_name'),
        (ADD_NEW_PRODUCT_WAIT_FOR_USER_EMAIL, '/add_new_product/wait_for_user_email'),
        (ADD_NEW_PRODUCT_WAIT_FOR_DATA_CHECK, '/add_new_product/wait_for_data_check'),
        (ADD_NEW_PRODUCT_PETITION_AND_QUIT, '/add_new_product/petition_and_quit'),
        (ADD_NEW_PRODUCT_SIGN_APPEAL, '/add_new_product/sign_appeal'),
        (ADD_NEW_PRODUCT_END, '/add_new_product/end'),
    )
    # fmt: on

    state = models.IntegerField(choices=CHAT_STATES, default=IDLE)
    agent = models.CharField(max_length=255)
    meta = models.CharField(max_length=255, default="{}")

    def __str__(self):
        return "chat with @{} on state {}".format(self.agent, self.state)

    def update_meta(self, new_meta):
        meta = self.get_meta()
        meta.update(new_meta)
        self.save_meta(meta)
        return self.get_meta()

    def get_meta(self):
        meta = self.meta
        if meta is None or meta == "":
            return {}
        loaded = json.loads(meta)
        if type(loaded) != dict:
            return {}
        return loaded

    def save_meta(self, data):
        strdata = json.dumps(data)
        self.meta = strdata
        self.save()
        return strdata
