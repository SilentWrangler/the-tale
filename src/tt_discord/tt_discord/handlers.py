
from tt_web import handlers

from tt_protocol.protocol import discord_pb2

from . import logic
from . import protobuf
from . import operations


async def sync_user(user, create_if_not_exists):
    account_info = await operations.get_account_info_by_game_id(user.id, create_if_not_exists)

    if account_info.id is None:
        return account_info

    nickname = logic.normalize_nickname(user.nickname)

    await operations.update_game_data(account_info.id,
                                      nickname=nickname,
                                      roles=list(user.roles))

    return account_info


@handlers.api(discord_pb2.GetBindCodeRequest)
async def get_bind_code(message, **kwargs):
    account_info = await sync_user(message.user, create_if_not_exists=True)

    bind_code = await operations.get_bind_code(account_info.id, expire_timeout=message.expire_timeout)

    return discord_pb2.GetBindCodeResponse(code=protobuf.from_bind_code(bind_code))


@handlers.api(discord_pb2.UpdateUserRequest)
async def update_user(message, **kwargs):
    await sync_user(message.user, create_if_not_exists=False)

    return discord_pb2.UpdateUserResponse()


@handlers.api(discord_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return discord_pb2.DebugClearServiceResponse()
