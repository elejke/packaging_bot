from django.contrib import admin
from .models import Chat, ImageUpload


class ChatAdmin(admin.ModelAdmin):
    pass


class ImageUploadAdmin(admin.ModelAdmin):
    pass


admin.site.register(Chat, ChatAdmin)
admin.site.register(ImageUpload, ImageUploadAdmin)
