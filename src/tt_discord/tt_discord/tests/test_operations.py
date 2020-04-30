
import uuid
import time
import datetime

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import operations

from . import helpers


class CreateAccountTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_account(self):
        account_id = await operations.create_account(game_id=666)

        self.assertNotEqual(account_id, None)

        result = await db.sql('SELECT * FROM accounts')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], account_id)
        self.assertEqual(result[0]['discord_id'], None)
        self.assertEqual(result[0]['game_id'], 666)

    @test_utils.unittest_run_loop
    async def test_duplicate(self):
        account_1_id = await operations.create_account(game_id=666)

        account_2_id = await operations.create_account(game_id=666)

        self.assertEqual(account_1_id, account_2_id)

        result = await db.sql('SELECT * FROM accounts')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], account_2_id)
        self.assertEqual(result[0]['discord_id'], None)
        self.assertEqual(result[0]['game_id'], 666)

    @test_utils.unittest_run_loop
    async def test_multuiple(self):
        account_1_id = await operations.create_account(game_id=666)

        account_2_id = await operations.create_account(game_id=777)

        self.assertNotEqual(account_1_id, account_2_id)

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['id'], account_1_id)
        self.assertEqual(result[0]['discord_id'], None)
        self.assertEqual(result[0]['game_id'], 666)

        self.assertEqual(result[1]['id'], account_2_id)
        self.assertEqual(result[1]['discord_id'], None)
        self.assertEqual(result[1]['game_id'], 777)


class GetAccountIdTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_account_exists(self):
        accounts_ids = await helpers.create_accounts(game_ids=(666, 777, 888))

        found_account_id = await operations.get_account_id(game_id=777)

        self.assertEqual(found_account_id, accounts_ids[1])

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 3)

    @test_utils.unittest_run_loop
    async def test_account_does_not_exist(self):
        accounts_ids = await helpers.create_accounts(game_ids=(666, 777, 888))

        found_account_id = await operations.get_account_id(game_id=999)

        self.assertNotIn(found_account_id, accounts_ids)

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 4)


class UpdateDiscordNicknameTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_nickname_record(self):
        accounts_ids = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_discord_nickname(accounts_ids[1], 'test nick')

        result = await db.sql('SELECT * FROM nicknames ORDER BY account')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['account'], accounts_ids[1])
        self.assertEqual(result[0]['nickname'], 'test nick')
        self.assertEqual(result[0]['synced_at'], None)

    @test_utils.unittest_run_loop
    async def test_has_nickname_record(self):
        accounts_ids = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_discord_nickname(accounts_ids[1], 'test nick')

        result = await db.sql('UPDATE nicknames SET synced_at=NOW() RETURNING synced_at')

        synced_at = result[0]['synced_at']

        await operations.update_discord_nickname(accounts_ids[1], 'test nick 2')

        result = await db.sql('SELECT * FROM nicknames ORDER BY account')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['account'], accounts_ids[1])
        self.assertEqual(result[0]['nickname'], 'test nick 2')
        self.assertEqual(result[0]['synced_at'], synced_at)

        self.assertLess(result[0]['created_at'], result[0]['updated_at'])


class GetBindCodeTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_code(self):
        accounts_ids = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_ids[1], expire_timeout=60)

        self.assertTrue(isinstance(code.code, uuid.UUID))
        self.assertEqual(code.created_at + datetime.timedelta(seconds=60), code.expire_at)

    async def check_renew(self, timeout_1, timeout_2, sleep_between):
        accounts_ids = await helpers.create_accounts(game_ids=(666, 777, 888))

        code_1 = await operations.get_bind_code(accounts_ids[1], expire_timeout=timeout_1)

        time.sleep(sleep_between)

        code_2 = await operations.get_bind_code(accounts_ids[1], expire_timeout=timeout_2)

        self.assertNotEqual(code_1.code, code_2.code)
        self.assertLess(code_1.created_at, code_2.created_at)
        self.assertLess(code_1.expire_at, code_2.expire_at)

        self.assertEqual(code_2.created_at + datetime.timedelta(seconds=timeout_2), code_2.expire_at)

    @test_utils.unittest_run_loop
    async def test_has_active_code(self):
        await self.check_renew(timeout_1=60, timeout_2=120, sleep_between=0.1)

    @test_utils.unittest_run_loop
    async def test_has_expired_code(self):
        await self.check_renew(timeout_1=0, timeout_2=60, sleep_between=0.1)
