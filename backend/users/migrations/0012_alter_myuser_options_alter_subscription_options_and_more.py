# Generated by Django 4.2.7 on 2023-11-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_myuser_is_blocked'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='myuser',
            options={'ordering': ('username',), 'verbose_name': 'Пользователь', 'verbose_name_plural': 'Пользователи'},
        ),
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ('user__username',), 'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterField(
            model_name='myuser',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='myuser',
            name='username',
            field=models.CharField(max_length=150, unique=True, verbose_name='Имя пользователя'),
        ),
    ]
