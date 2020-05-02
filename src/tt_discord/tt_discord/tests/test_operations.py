
import uuid
import time
import datetime
import dataclasses

from aiohttp import test_utils

from tt_web import postgresql as db

from .. import objects
from .. import relations
from .. import operations

from . import helpers


class CreateAccountTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_account(self):
        account_info = await operations.create_account(game_id=666)

        self.assertNotEqual(account_info.id, None)
        self.assertEqual(account_info.discord_id, None)
        self.assertEqual(account_info.game_id, 666)

        result = await db.sql('SELECT * FROM accounts')

        self.assertEqual(len(result), 1)

        self.assertEqual(operations.row_to_account_info(result[0]),
                         account_info)

    @test_utils.unittest_run_loop
    async def test_duplicate(self):
        account_1_info = await operations.create_account(game_id=666)

        account_2_info = await operations.create_account(game_id=666)

        self.assertEqual(account_1_info, account_2_info)

        result = await db.sql('SELECT * FROM accounts')

        self.assertEqual(len(result), 1)

        self.assertEqual(operations.row_to_account_info(result[0]),
                         account_2_info)

    @test_utils.unittest_run_loop
    async def test_multuiple(self):
        account_1_info = await operations.create_account(game_id=666)

        account_2_info = await operations.create_account(game_id=777)

        self.assertNotEqual(account_1_info, account_2_info)

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 2)

        self.assertEqual(operations.row_to_account_info(result[0]),
                         account_1_info)

        self.assertEqual(operations.row_to_account_info(result[1]),
                         account_2_info)


class GetAccountInfoByGameIdTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_account_exists(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        found_account_info = await operations.get_account_info_by_game_id(game_id=777, create_if_not_exists=False)

        self.assertEqual(found_account_info, accounts_infos[1])

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 3)

    @test_utils.unittest_run_loop
    async def test_account_does_not_exist__create(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        found_account_info = await operations.get_account_info_by_game_id(game_id=999, create_if_not_exists=True)

        self.assertNotIn(found_account_info, accounts_infos)

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 4)

    @test_utils.unittest_run_loop
    async def test_account_does_not_exist__do_not_create(self):
        await helpers.create_accounts(game_ids=(666, 777, 888))

        found_account_info = await operations.get_account_info_by_game_id(game_id=999, create_if_not_exists=False)

        self.assertEqual(found_account_info, objects.AccountInfo(id=None,
                                                                 game_id=999,
                                                                 discord_id=None))

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 3)


class GetAccountInfoByDiscordIdTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_account_exists(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)
        await operations.bind_discord_user(code.code, discord_id=100500)

        found_account_info = await operations.get_account_info_by_discord_id(discord_id=100500)

        self.assertEqual(found_account_info, dataclasses.replace(accounts_infos[1], discord_id=100500))

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 3)

    @test_utils.unittest_run_loop
    async def test_account_does_not_exist(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)
        await operations.bind_discord_user(code.code, discord_id=100500)

        found_account_info = await operations.get_account_info_by_discord_id(discord_id=100600)

        self.assertEqual(found_account_info,
                         objects.AccountInfo(id=None,
                                             game_id=None,
                                             discord_id=100600))

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 3)


class GetAccountInfoByIdTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_account_exists(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        found_account_info = await operations.get_account_info_by_id(accounts_infos[1].id)

        self.assertEqual(found_account_info, accounts_infos[1])

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 3)

    @test_utils.unittest_run_loop
    async def test_account_does_not_exist(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        found_account_info = await operations.get_account_info_by_id(accounts_infos[2].id + 1)

        self.assertEqual(found_account_info,
                         objects.AccountInfo(id=None,
                                             game_id=None,
                                             discord_id=None))

        result = await db.sql('SELECT * FROM accounts ORDER BY game_id')

        self.assertEqual(len(result), 3)


class UpdateGameDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_record(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')

        result = await db.sql('SELECT * FROM game_data ORDER BY account')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['account'], accounts_infos[1].id)
        self.assertEqual(relations.GAME_DATA_TYPE(result[0]['type']), relations.GAME_DATA_TYPE.NICKNAME)
        self.assertEqual(result[0]['data'], {'nickname': 'test nick'})
        self.assertEqual(result[0]['synced_at'], None)

    @test_utils.unittest_run_loop
    async def test_has_record(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')

        result = await db.sql('UPDATE game_data SET synced_at=NOW() RETURNING synced_at')

        synced_at = result[0]['synced_at']

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick 2')

        result = await db.sql('SELECT * FROM game_data ORDER BY account')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['account'], accounts_infos[1].id)
        self.assertEqual(relations.GAME_DATA_TYPE(result[0]['type']), relations.GAME_DATA_TYPE.NICKNAME)
        self.assertEqual(result[0]['data'], {'nickname': 'test nick 2'})
        self.assertEqual(result[0]['synced_at'], synced_at)

        self.assertLess(result[0]['created_at'], result[0]['updated_at'])

    @test_utils.unittest_run_loop
    async def test_not_changed(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')

        result = await db.sql('UPDATE game_data SET synced_at=NOW() RETURNING synced_at, updated_at')

        old_synced_at = result[0]['synced_at']
        old_updated_at = result[0]['updated_at']

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')

        result = await db.sql('SELECT * FROM game_data ORDER BY account')

        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['data'], {'nickname': 'test nick'})
        self.assertEqual(result[0]['synced_at'], old_synced_at)
        self.assertEqual(result[0]['updated_at'], old_updated_at)

    @test_utils.unittest_run_loop
    async def test_multiple_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id,
                                          nickname='test nick',
                                          roles=['role_1', 'role_2'])

        result = await db.sql('SELECT * FROM game_data ORDER BY (account, type)')

        self.assertEqual(len(result), 2)

        self.assertEqual(result[0]['account'], accounts_infos[1].id)
        self.assertEqual(relations.GAME_DATA_TYPE(result[0]['type']), relations.GAME_DATA_TYPE.NICKNAME)
        self.assertEqual(result[0]['data'], {'nickname': 'test nick'})

        self.assertEqual(result[1]['account'], accounts_infos[1].id)
        self.assertEqual(relations.GAME_DATA_TYPE(result[1]['type']), relations.GAME_DATA_TYPE.ROLES)
        self.assertCountEqual(result[1]['data']['roles'], ['role_1', 'role_2'])


class GetNewGameDataTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666,))

        data, update_times = await operations.get_new_game_data(accounts_infos[0].id)

        self.assertEqual(data, {})
        self.assertEqual(update_times, {})

    @test_utils.unittest_run_loop
    async def test_has_new_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')
        await operations.update_game_data(accounts_infos[2].id, nickname='test nick 2')

        data, update_times = await operations.get_new_game_data(accounts_infos[1].id)

        self.assertEqual(data, {relations.GAME_DATA_TYPE.NICKNAME: {'nickname': 'test nick'}})

        result = await db.sql('SELECT updated_at FROM game_data WHERE account=%(account_id)s',
                              {'account_id': accounts_infos[1].id})

        self.assertEqual(update_times, {relations.GAME_DATA_TYPE.NICKNAME: result[0]['updated_at']})

    @test_utils.unittest_run_loop
    async def test_has_multiple_new_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id,
                                          nickname='test nick',
                                          roles=['role_1', 'role_3'])

        await operations.update_game_data(accounts_infos[2].id,
                                          nickname='test nick 2')

        data, update_times = await operations.get_new_game_data(accounts_infos[1].id)

        self.assertEqual(data, {relations.GAME_DATA_TYPE.NICKNAME: {'nickname': 'test nick'},
                                relations.GAME_DATA_TYPE.ROLES: {'roles': ['role_1', 'role_3']}})

        result = await db.sql('SELECT updated_at FROM game_data WHERE account=%(account_id)s ORDER BY type',
                              {'account_id': accounts_infos[1].id})

        self.assertEqual(update_times, {relations.GAME_DATA_TYPE.NICKNAME: result[0]['updated_at'],
                                        relations.GAME_DATA_TYPE.ROLES: result[1]['updated_at']})

    @test_utils.unittest_run_loop
    async def test_no_new_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')
        await operations.update_game_data(accounts_infos[2].id, nickname='test nick 2')

        await operations.mark_game_data_synced(accounts_infos[1].id,
                                               type=relations.GAME_DATA_TYPE.NICKNAME,
                                               synced_at=datetime.datetime.now())

        data, update_times = await operations.get_new_game_data(accounts_infos[1].id)

        self.assertEqual(data, {})
        self.assertEqual(update_times, {})

    @test_utils.unittest_run_loop
    async def test_has_new_records_after_sync(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')
        await operations.update_game_data(accounts_infos[2].id, nickname='test nick 2')

        await operations.mark_game_data_synced(accounts_infos[1].id,
                                               type=relations.GAME_DATA_TYPE.NICKNAME,
                                               synced_at=datetime.datetime.now())

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick 3')

        data, update_times = await operations.get_new_game_data(accounts_infos[1].id)

        self.assertEqual(data, {relations.GAME_DATA_TYPE.NICKNAME: {'nickname': 'test nick 3'}})

        result = await db.sql('SELECT updated_at FROM game_data WHERE account=%(account_id)s',
                              {'account_id': accounts_infos[1].id})

        self.assertEqual(update_times, {relations.GAME_DATA_TYPE.NICKNAME: result[0]['updated_at']})


class MarkGameDataSyncedTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')
        await operations.update_game_data(accounts_infos[2].id, nickname='test nick 2')

        await operations.mark_game_data_synced(accounts_infos[0].id,
                                               type=relations.GAME_DATA_TYPE.NICKNAME,
                                               synced_at=datetime.datetime.now())

        data, update_times = await operations.get_new_game_data(accounts_infos[0].id)

        self.assertEqual(data, {})

    @test_utils.unittest_run_loop
    async def test_has_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id, nickname='test nick')

        await operations.mark_game_data_synced(accounts_infos[1].id,
                                               type=relations.GAME_DATA_TYPE.NICKNAME,
                                               synced_at=datetime.datetime.now())

        data, update_times = await operations.get_new_game_data(accounts_infos[1].id)

        self.assertEqual(data, {})

    @test_utils.unittest_run_loop
    async def test_multiple_records(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        await operations.update_game_data(accounts_infos[1].id,
                                          nickname='test nick',
                                          roles=['role_1', 'rol_2'])

        await operations.mark_game_data_synced(accounts_infos[1].id,
                                               type=relations.GAME_DATA_TYPE.ROLES,
                                               synced_at=datetime.datetime.now())

        data, update_times = await operations.get_new_game_data(accounts_infos[1].id)

        self.assertEqual(data, {relations.GAME_DATA_TYPE.NICKNAME: {'nickname': 'test nick'}})


class GetBindCodeTests(helpers.BaseTests):

    @test_utils.unittest_run_loop
    async def test_no_code(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)

        self.assertTrue(isinstance(code.code, uuid.UUID))
        self.assertEqual(code.created_at + datetime.timedelta(seconds=60), code.expire_at)

    async def check_renew(self, timeout_1, timeout_2, sleep_between):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code_1 = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=timeout_1)

        time.sleep(sleep_between)

        code_2 = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=timeout_2)

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


class BindDiscordUserCodeTests(helpers.BaseTests):

    async def check_no_bind(self, discord_id):
        result = await db.sql('SELECT 1 FROM accounts WHERE discord_id=%(discord_id)s',
                              {'discord_id': discord_id})
        self.assertEqual(len(result), 0)

    async def check_has_bind(self, account_id, discord_id):
        result = await db.sql('SELECT id FROM accounts WHERE discord_id=%(discord_id)s',
                              {'discord_id': discord_id})
        self.assertEqual(len(result), 1)

        self.assertEqual(result[0]['id'], account_id)

    @test_utils.unittest_run_loop
    async def test_no_code_found(self):
        await helpers.create_accounts(game_ids=(666, 777, 888))

        result = await operations.bind_discord_user(uuid.uuid4().hex, discord_id=100500)

        self.assertEqual(relations.BIND_RESULT.CODE_NOT_FOUND, result)

        await self.check_no_bind(discord_id=100500)

    @test_utils.unittest_run_loop
    async def test_code_expired(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=0)

        result = await operations.bind_discord_user(code.code, discord_id=100500)

        self.assertEqual(relations.BIND_RESULT.CODE_EXPIRED, result)

        await self.check_no_bind(discord_id=100500)

    @test_utils.unittest_run_loop
    async def test_success_new(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)

        result = await operations.bind_discord_user(code.code, discord_id=100500)

        self.assertEqual(relations.BIND_RESULT.SUCCESS_NEW, result)

        await self.check_has_bind(accounts_infos[1].id, discord_id=100500)

    @test_utils.unittest_run_loop
    async def test_already_binded(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)

        await operations.bind_discord_user(code.code, discord_id=100500)

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)

        result = await operations.bind_discord_user(code.code, discord_id=100500)

        self.assertEqual(relations.BIND_RESULT.ALREADY_BINDED, result)

        await self.check_has_bind(accounts_infos[1].id, discord_id=100500)

    @test_utils.unittest_run_loop
    async def test_success_rebind(self):
        accounts_infos = await helpers.create_accounts(game_ids=(666, 777, 888))

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)

        await operations.bind_discord_user(code.code, discord_id=100500)

        code = await operations.get_bind_code(accounts_infos[1].id, expire_timeout=60)

        result = await operations.bind_discord_user(code.code, discord_id=100501)

        self.assertEqual(relations.BIND_RESULT.SUCCESS_REBIND, result)

        await self.check_no_bind(discord_id=100500)
        await self.check_has_bind(accounts_infos[1].id, discord_id=100501)
