
import uuid
import random

from aiohttp import test_utils

from tt_protocol.protocol import discord_pb2

from tt_web import postgresql as db

from .. import protobuf
from .. import operations

from . import helpers


def random_user(id=None, nickname=None):
    if id is None:
        id = random.randint(1, 100000000)

    if nickname is None:
        nickname = uuid.uuid4().hex

    return discord_pb2.User(id=id,
                            nickname=nickname)


class GetBindCodeTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_success(self):

        user = random_user()

        request = await self.client.post('/get-bind-code',
                                         data=discord_pb2.GetBindCodeRequest(user=user,
                                                                             expire_timeout=60).SerializeToString())
        data = await self.check_success(request, discord_pb2.GetBindCodeResponse)

        account_id = await operations.get_account_id(user.id)

        result = await db.sql('SELECT * FROM bind_codes WHERE account=%(account_id)s',
                              {'account_id': account_id})

        self.assertEqual(data.code,
                         protobuf.from_bind_code(operations.row_to_bind_code(result[0])))

        result = await db.sql('SELECT * FROM nicknames WHERE account=%(account_id)s',
                              {'account_id': account_id})

        self.assertEqual(result[0]['nickname'], user.nickname)

    @test_utils.unittest_run_loop
    async def test_normalize_nick(self):

        user = random_user(nickname='problem@nick')

        await self.client.post('/get-bind-code',
                               data=discord_pb2.GetBindCodeRequest(user=user,
                                                                   expire_timeout=60).SerializeToString())
        account_id = await operations.get_account_id(user.id)

        result = await db.sql('SELECT * FROM nicknames WHERE account=%(account_id)s',
                              {'account_id': account_id})

        self.assertEqual(result[0]['nickname'], 'problem?nick')
