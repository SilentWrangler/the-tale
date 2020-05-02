
import uuid
import logging

from discord.ext import commands as discord_commands

from . import relations
from . import operations


REQUIRED_PERMISSIONS = {'manage_nicknames'}


class Bot(discord_commands.Bot):

    # @discord_commands.has_guild_permissions(manage_nicknames=True)
    async def on_ready(self):
        logging.info('logged as "%s"', self.user)

        for guild in self.guilds:
            await self.check_permissions(guild)

    async def check_permissions(self, guild):
        member = guild.get_member(self.user.id)

        for name in REQUIRED_PERMISSIONS:
            if not getattr(member.guild_permissions, name):
                logging.error('Bot has no permission "%(permission)s" on guild "%(guild_name)s" [%(guild_id)s]',
                              {'permission': name,
                               'guild_name': guild.name,
                               'guild_id': guild.id})


def construct(bot, config):

    @bot.command()
    async def bind(context, bind_code: uuid.UUID):
        logging.info('bind command received, code: "%s", discord id: "%s"', bind_code, context.author.id)

        result = await operations.bind_discord_user(bind_code=bind_code,
                                                    discord_id=context.author.id)

        if result not in relations.BIND_RESULT_MESSAGES:
            raise NotImplementedError('unknown bind result')

        await context.send(relations.BIND_RESULT_MESSAGES[result])

        if not result.is_success():
            return

        account_info = await operations.get_account_info_by_discord_id(context.author.id)

        await synchronize(bot, account_info)


async def synchronize(bot, account_info):

    if not account_info.is_binded():
        NotImplementedError('game account not bind to discord')

    data, update_times = await operations.get_new_game_data(account_info.id)

    for data_type, value in data.items():
        if data_type is relations.GAME_DATA_TYPE.NICKNAME:
            await sync_nickname(bot, account_info, value, sync_time=update_times[data_type])


async def sync_nickname(bot, account_info, data, sync_time):

    nickname = data['nickname']

    for guild in bot.guilds:
        member = guild.get_member(account_info.discord_id)

        if guild.owner.id == member.id:
            await member.send('Я не могу изменить ваш ник, так как вы являетесь владельцем сервера.')
            continue

        await member.edit(nick=nickname, reason='Синхронизация с ником в игре.')
        await member.send('Я изменил ваш ник, чтобы он соответствовал нику в игре.')

    await operations.mark_game_data_synced(account_info.id,
                                           type=relations.GAME_DATA_TYPE.NICKNAME,
                                           synced_at=sync_time)
