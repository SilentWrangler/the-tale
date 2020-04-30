

from django.db import models

from django.contrib.postgres import fields as postgres_fields


DISCORD_NICKNAME_MAX_LENGTH = 32


class Account(models.Model):

    id = models.BigAutoField(primary_key=True)

    discord_id = models.BigIntegerField(null=True)

    game_id = models.BigIntegerField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = 'accounts'


class Nick(models.Model):

    account = models.ForeignKey(Account, related_name='+', on_delete=models.CASCADE, db_column='account')

    nickname = models.CharField(max_length=DISCORD_NICKNAME_MAX_LENGTH)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)
    synced_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'nicks'


class BindCode(models.Model):

    id = models.BigAutoField(primary_key=True)

    code = models.UUIDField()

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    expire_at = models.DateTimeField(db_index=True)

    class Meta:
        db_table = 'invites'
