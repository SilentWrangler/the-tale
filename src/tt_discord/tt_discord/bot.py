
import uuid
import logging

from discord.ext import commands as discord_commands

from . import relations
from . import operations


class Bot(discord_commands.Bot):

    async def on_ready(self):
        logging.info('logged as "%s"', self.user)

    async def on_message(self, message):
        logging.info(f'Message from {message.author}: {message.content}')


def construct(bot, config):

    @bot.command()
    async def bind(context, bind_code: uuid.UUID):
        result = await operations.bind_discord_user(bind_code=bind_code,
                                                    discord_id=context.author.id)

        if result not in relations.BIND_RESULT_MESSAGES:
            raise NotImplementedError('unknown bind result')

        context.send(relations.BIND_RESULT_MESSAGES[result])

        if not relations.BIND_RESULT.is_success(result):
            return

        account_info = await operations.get_account_info_by_discord_id(discord_id)

        await synchronize(bot, account_info)


async def synchronize(bot, account_info):

    if not account_info.is_binded():
        NotImplementedError('game account not bind to discord')

    data = await operations.get_new_game_data(account_info.id)

    for data_type, value in data.items():
        if data_type is relations.GAME_DATA_TYPE.NICKNAME:
            await sync_nickname(bot, account_info, value)


async def sync_nickname(bot, account_info, data):

    nickname = data['nickname']

    for guild in bot.guilds:
        member = guild.get_member(account_info.discord_id)
        member.edit(nick=nickname, reason='Синхронизация с ником в игре')

    await operations.mark_discord_nickname_synced(account_id)
