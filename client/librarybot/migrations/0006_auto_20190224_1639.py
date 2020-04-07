# Generated by Django 2.1.7 on 2019-02-24 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("librarybot", "0005_auto_20190224_1614")]

    operations = [
        migrations.AddField(
            model_name="botuser",
            name="name",
            field=models.CharField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name="book",
            name="author",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="librarybot.BookAuthor",
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="language",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="librarybot.BookLanguage",
            ),
        ),
    ]