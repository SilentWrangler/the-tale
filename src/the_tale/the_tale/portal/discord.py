
import smart_imports

smart_imports.all()


class DISCORD_ROLE(rels_django.DjangoEnum):
    records = (('DEVELOPER', 0, 'Разработчик'),
               ('MODERATOR', 1, 'Модератор'),
               ('PILLAR_OF_WORLD', 2, 'Столп Мира'),
               ('MIGHTY_KEEPER', 3, 'Могучий Хранитель'),
               ('KEEPER', 4, 'Хранитель'),
               ('SPIRIT_OF_PANDORA', 5, 'Дух Пандоры'))


def construc_user_info(account):

    ##########
    # nickname
    ##########
    nickname = account.nick_verbose

    if account.clan_id is not None:
        membership = clans_logic.get_membership(account.id)
        nickname = f'[{clans_storage.infos[account.clan_id].abbr}] {membership.role.symbol} {nickname}'

    #######
    # roles
    #######

    roles = set()

    if account.id in accounts_conf.settings.DEVELOPERS_IDS:
        roles.add(DISCORD_ROLE.DEVELOPER)

    if account.id in accounts_conf.settings.MODERATORS_IDS:
        roles.add(DISCORD_ROLE.MODERATOR)

    if account.might >= 10000:
        roles.add(DISCORD_ROLE.PILLAR_OF_WORLD)

    elif account.might >= 1000:
        roles.add(DISCORD_ROLE.MIGHTY_KEEPER)

    elif account.might >= 100:
        roles.add(DISCORD_ROLE.KEEPER)

    else:
        roles.add(DISCORD_ROLE.SPIRIT_OF_PANDORA)

    ######################
    # communicate with bot
    ######################
    user = tt_protocol_discord_pb2.User(id=account.id,
                                        nickname=nickname,
                                        roles=[role.name.lower() for role in roles])

    return user
