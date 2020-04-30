# Generated by Django 2.2.8 on 2020-04-30 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tt_discord', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nick',
            name='account',
            field=models.ForeignKey(db_column='account', on_delete=django.db.models.deletion.CASCADE, related_name='+', to='tt_discord.Account', unique=True),
        ),
    ]
