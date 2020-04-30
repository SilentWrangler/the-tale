

from django.db import models

from django.contrib.postgres import fields as postgres_fields

from . import conf


class Account(models.Model):

    id = models.BigAutoField(primary_key=True)

    discord_id = models.BigIntegerField(null=True, unique=True)

    game_id = models.BigIntegerField(unique=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = 'accounts'


class Nick(models.Model):

    account = models.ForeignKey(Account, unique=True, related_name='+', on_delete=models.CASCADE, db_column='account')

    nickname = models.CharField(max_length=conf.DISCORD_NICKNAME_MAX_LENGTH)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    synced_at = models.DateTimeField(null=True, db_index=True)

    class Meta:
        db_table = 'nicknames'


class BindCode(models.Model):

    id = models.BigAutoField(primary_key=True)

    code = models.UUIDField(unique=True)

    account = models.ForeignKey(Account, unique=True, related_name='+', on_delete=models.CASCADE, db_column='account')

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expire_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'bind_codes'
