
import re

from . import conf


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
