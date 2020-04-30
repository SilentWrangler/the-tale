
from tt_web import handlers

from tt_protocol.protocol import discord_pb2

from . import logic
from . import protobuf
from . import operations


@handlers.api(discord_pb2.GetBindCodeRequest)
async def get_bind_code(message, **kwargs):
    account_id = await operations.get_account_id(message.user.id)

    nickname = logic.normalize_nickname(message.user.nickname)

    await operations.update_discord_nickname(account_id, nickname)

    bind_code = await operations.get_bind_code(account_id, expire_timeout=message.expire_timeout)

    return discord_pb2.GetBindCodeResponse(code=protobuf.from_bind_code(bind_code))


@handlers.api(discord_pb2.DebugClearServiceRequest)
async def debug_clear_service(message, **kwargs):
    await operations.clean_database()
    return discord_pb2.DebugClearServiceResponse()
