# Generated by Django 2.2.1 on 2020-01-30 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('librarybot', '0016_auto_20200130_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='state',
            field=models.IntegerField(choices=[(0, '<<Idle>>'), (1, '<<Chat ended>>'), (2, '/main'), (3, '/addevent/ask_name'), (4, '/addevent/ask_participants'), (5, '/addevent/end'), (6, '/addspending/ask_event_name'), (7, '/addspending/ask_name'), (8, '/addspending/ask_sum'), (9, '/addspending/ask_who_paid'), (10, '/addspending/ask_participants'), (11, '/addspending/ask_image'), (12, '/addspending/end'), (13, '/registration/email'), (14, '/registration/end'), (15, '/regbook/ask_name'), (16, '/regbook/ask_author'), (17, '/regbook/ask_language'), (18, '/regbook/ask_hostname'), (19, '/regbook/ask_photo'), (20, '/regbook/ask_isbn'), (21, '/regbook/end'), (22, '/borrow/ask_search'), (23, '/borrow/search_results'), (24, '/borrow/search_result_confirm'), (25, '/borrow/confirm_borrow'), (26, '/borrow/confirm_return')], default=0),
        ),
    ]
