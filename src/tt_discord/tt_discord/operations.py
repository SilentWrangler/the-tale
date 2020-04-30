
from psycopg2.extras import Json as PGJson

from tt_web import postgresql as db

from . import objects


    account_id = await operations.get_account_id(message.user.id)

    await operations.update_discord_nickname(account_id, message.user.nickname)

    bind_code = await operations.get_bind_code(account_id)
