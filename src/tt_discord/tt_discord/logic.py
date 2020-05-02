
import re
import logging

from tt_web.common import event

from . import bot
from . import conf
from . import operations


# https://discordapp.com/developers/docs/resources/user
def normalize_nickname(nickname, error_nick='unknown player', replacer='?'):
    nickname = nickname.strip()

    nickname = re.sub('\s+', ' ', nickname)

    if nickname in ('discordtag', 'everyone', 'here'):
        return error_nick

    for substring in ('@', '#', ':', '```'):
        nickname = nickname.replace(substring, replacer * len(substring))

    if nickname == '':
        return error_nick

    return nickname[:conf.DISCORD_NICKNAME_MAX_LENGTH]


async def sync_users(bot_instance, config):

    logging.info('synchonisation: start')

    sync_event = event.get(conf.SYNC_EVENT_NAME)

    while True:
        sync_event.clear()

        changes = await operations.get_any_new_game_data(config['sync_users_chank_size'])

        if not changes:
            logging.info('synchonisation: no changes detected, wait for changes')
            await sync_event.wait()
            continue

        logging.info('synchonisation: changes found (%s)', len(changes))

        for change in changes:
            import asyncio
            await asyncio.sleep(1)

            logging.info('synchonisation: process change <%s>', change)
            await bot.sync_change(change, bot_instance, config)
            logging.info('synchonisation: change processed')

        logging.info('synchonisation: all changes processed, go to next iteration')

        sync_event.set()
