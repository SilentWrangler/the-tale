
import uuid

from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects
from . import relations


def row_to_account_info(row):
    return objects.AccountInfo(id=row['id'],
                               game_id=row['game_id'],
                               discord_id=row['discord_id'])


async def create_account(game_id):

    result = await db.sql('''INSERT INTO accounts (discord_id, game_id, created_at, updated_at)
                             VALUES (NULL, %(game_id)s, NOW(), NOW())
                             ON CONFLICT DO NOTHING
                             RETURNING *''',
                          {'game_id': game_id})

    if result:
        return row_to_account_info(result[0])

    return await get_account_info_by_game_id(game_id)


async def get_account_info_by_game_id(game_id):

    result = await db.sql('SELECT * FROM accounts WHERE game_id=%(game_id)s',
                          {'game_id': game_id})

    if result:
        return row_to_account_info(result[0])

    return await create_account(game_id)


async def get_account_info_by_discord_id(discord_id):

    result = await db.sql('SELECT * FROM accounts WHERE discord_id=%(discord_id)s',
                          {'discord_id': discord_id})

    if result:
        return row_to_account_info(result[0])

    return objects.AccountInfo(id=None,
                               game_id=None,
                               discord_id=discord_id)


async def get_account_info_by_id(account_id):

    result = await db.sql('SELECT * FROM accounts WHERE id=%(account_id)s',
                          {'account_id': account_id})

    if result:
        return row_to_account_info(result[0])

    return objects.AccountInfo(id=None,
                               game_id=None,
                               discord_id=None)


async def _update_game_data(account_id, type, data):

    await db.sql('''INSERT INTO game_data (account, type, data, created_at, updated_at, synced_at)
                    VALUES (%(account_id)s, %(type)s, %(data)s, NOW(), NOW(), NULL)
                    ON CONFLICT (account, type) DO UPDATE SET data=%(data)s,
                                                              updated_at=NOW()''',
                 {'account_id': account_id,
                  'data': PGJson(data),
                  'type': type.value})


async def update_game_data(account_id, nickname=None, roles=None):

    if nickname is not None:
        await _update_game_data(account_id,
                                type=relations.GAME_DATA_TYPE.NICKNAME,
                                data={'nickname': nickname})

    if roles is not None:
        await _update_game_data(account_id,
                                type=relations.GAME_DATA_TYPE.ROLES,
                                data={'roles': roles})


async def get_new_game_data(account_id):

    result = await db.sql('''SELECT type, data, updated_at FROM game_data
                             WHERE account=%(account_id)s AND
                                   (synced_at IS NULL OR synced_at < updated_at)''',
                          {'account_id': account_id})

    data = {}
    update_times = {}

    for row in result:
        data[relations.GAME_DATA_TYPE(row['type'])] = row['data']
        update_times[relations.GAME_DATA_TYPE(row['type'])] = row['updated_at']

    return data, update_times


async def mark_game_data_synced(account_id, type, synced_at):
    await db.sql('UPDATE game_data SET synced_at=%(synced_at)s WHERE account=%(account_id)s AND type=%(type)s',
                 {'synced_at': synced_at,
                  'account_id': account_id,
                  'type': type.value})


def row_to_bind_code(row):
    return objects.BindCode(code=row['code'],
                            created_at=row['created_at'],
                            expire_at=row['expire_at'])


async def get_bind_code(account_id, expire_timeout):

    result = await db.sql('''INSERT INTO bind_codes (code, account, created_at, expire_at)
                             VALUES (%(code)s, %(account_id)s, NOW(), NOW() + %(expire_timeout)s * INTERVAL '1 second')
                             ON CONFLICT (account) DO UPDATE SET code=%(code)s,
                                                                 created_at=NOW(),
                                                                 expire_at=NOW() + %(expire_timeout)s * INTERVAL '1 second'
                             RETURNING code, created_at, expire_at''',
                          {'account_id': account_id,
                           'expire_timeout': expire_timeout,
                           'code': uuid.uuid4()})

    return row_to_bind_code(result[0])


async def bind_discord_user(bind_code, discord_id):

    return await db.transaction(_bind_discord_user, {'bind_code': bind_code,
                                                     'discord_id': discord_id})


async def _bind_discord_user(execute, arguments):
    bind_code = arguments['bind_code']
    new_discord_id = arguments['discord_id']

    result = await execute('SELECT * FROM bind_codes WHERE code=%(code)s FOR UPDATE',
                           {'code': bind_code})

    if not result:
        return relations.BIND_RESULT.CODE_NOT_FOUND

    code = row_to_bind_code(result[0])

    if code.is_expired():
        return relations.BIND_RESULT.CODE_EXPIRED

    await execute('UPDATE bind_codes SET expire_at=NOW() WHERE code=%(code)s',
                  {'code': bind_code})

    account_id = result[0]['account']

    result = await execute('SELECT discord_id FROM accounts WHERE id=%(account_id)s',
                           {'account_id': account_id})

    old_discord_id = result[0]['discord_id']

    if old_discord_id == new_discord_id:
        return relations.BIND_RESULT.ALREADY_BINDED

    await execute('UPDATE accounts SET discord_id=%(discord_id)s, updated_at=NOW() WHERE id=%(account_id)s',
                  {'account_id': account_id,
                   'discord_id': new_discord_id})

    if old_discord_id is None:
        return relations.BIND_RESULT.SUCCESS_NEW

    return relations.BIND_RESULT.SUCCESS_REBIND


async def clean_database():
    await db.sql('TRUNCATE accounts, game_data, bind_codes')
