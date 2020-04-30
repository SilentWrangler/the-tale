
import uuid

from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects


async def create_account(game_id):

    result = await db.sql('''INSERT INTO accounts (discord_id, game_id, created_at, updated_at)
                             VALUES (NULL, %(game_id)s, NOW(), NOW())
                             ON CONFLICT DO NOTHING
                             RETURNING id''',
                          {'game_id': game_id})

    if result:
        return result[0]['id']

    return await get_account_id(game_id)


async def get_account_id(game_id):

    result = await db.sql('SELECT id FROM accounts WHERE game_id=%(game_id)s',
                          {'game_id': game_id})

    if result:
        return result[0]['id']

    return await create_account(game_id)


async def update_discord_nickname(account_id, nickname):

    await db.sql('''INSERT INTO nicknames (account, nickname, created_at, updated_at, synced_at)
                    VALUES (%(account_id)s, %(nickname)s, NOW(), NOW(), NULL)
                    ON CONFLICT (account) DO UPDATE SET nickname=%(nickname)s,
                                                        updated_at=NOW()''',
                 {'account_id': account_id,
                  'nickname': nickname})


def row_to_bind_code(row):
    return objects.BindCode(code=row['code'],
                            created_at=row['created_at'],
                            expire_at=row['expire_at'])


async def get_bind_code(account_id, expire_timeout):

    await db.sql('DELETE FROM bind_codes WHERE account=%(account_id)s',
                 {'account_id': account_id})

    result = await db.sql('''INSERT INTO bind_codes (code, account, created_at, expire_at)
                             VALUES (%(code)s, %(account_id)s, NOW(), NOW() + %(expire_timeout)s * INTERVAL '1 second')
                             RETURNING code, created_at, expire_at''',
                         {'account_id': account_id,
                          'expire_timeout': expire_timeout,
                          'code': uuid.uuid4()})

    return row_to_bind_code(result[0])


async def clean_database():
    await db.sql('TRUNCATE accounts, nicknames, bind_codes')
