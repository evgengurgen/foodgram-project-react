# Generated by Django 4.2.7 on 2023-11-09 22:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_remove_recipeingredient_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ingredient',
            name='amount',
        ),
        migrations.AddField(
            model_name='recipeingredient',
            name='amount',
            field=models.IntegerField(default=1, help_text='Колличество ингредиента', verbose_name='Колличество'),
            preserve_default=False,
        ),
    ]
