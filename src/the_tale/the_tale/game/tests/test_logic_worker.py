
import smart_imports

smart_imports.all()


class LogicWorkerTests(utils_testcase.TestCase):

    def setUp(self):
        super(LogicWorkerTests, self).setUp()

        self.p1, self.p2, self.p3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=self.account.id)

        amqp_environment.environment.deinitialize()
        amqp_environment.environment.initialize()

        self.worker = amqp_environment.environment.workers.logic_1
        self.worker.process_initialize(game_turn.number(), 'logic')

    def tearDown(self):
        pass

    def test_process_initialize(self):
        self.assertTrue(self.worker.initialized)
        self.assertEqual(self.worker.worker_id, 'logic')
        self.assertEqual(self.worker.turn_number, 0)
        self.assertEqual(self.worker.storage.heroes, {})
        self.assertEqual(self.worker.queue, [])

    def test_process_start_hero_caching(self):
        current_time = datetime.datetime.now()
        self.worker.process_register_account(self.account.id)
        self.assertTrue(self.worker.storage.heroes[self.hero.id].ui_caching_started_at < current_time)
        self.worker.process_start_hero_caching(self.account.id)
        self.assertTrue(self.worker.storage.heroes[self.hero.id].ui_caching_started_at > current_time)

    def test_process_next_turn(self):

        game_turn.increment()

        self.worker.process_register_account(self.account.id)

        with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_account_release_required') as release_required_counter:
            with mock.patch('the_tale.game.heroes.logic.save_hero') as save_counter:
                self.worker.process_next_turn(game_turn.number())

        self.assertEqual(save_counter.call_count, 1)
        self.assertEqual(release_required_counter.call_count, 0)

    def test_process_next_turn_with_skipped_hero(self):

        game_turn.increment()

        self.worker.process_register_account(self.account.id)

        self.worker.storage.skipped_heroes.add(self.hero.id)

        with mock.patch('the_tale.game.actions.prototypes.ActionBase.process_turn') as action_process_turn:
            with mock.patch('the_tale.game.workers.supervisor.Worker.cmd_account_release_required') as release_required_counter:
                with mock.patch('the_tale.game.heroes.logic.save_hero') as save_counter:
                    with mock.patch('the_tale.game.conf.settings.SAVED_UNCACHED_HEROES_FRACTION', 0):
                        self.worker.process_next_turn(game_turn.number())

        self.assertEqual(action_process_turn.call_count, 0)
        self.assertEqual(save_counter.call_count, 1)
        self.assertEqual(release_required_counter.call_count, 1)

    def test_process_update_hero_with_account_data(self):
        self.worker.process_register_account(self.account.id)

        with mock.patch('the_tale.game.heroes.objects.Hero.update_with_account_data') as update_method:
            self.worker.process_update_hero_with_account_data(account_id=self.account.id,
                                                              is_fast=False,
                                                              premium_end_at=666,
                                                              active_end_at=666666,
                                                              ban_end_at=777777,
                                                              might=8888,
                                                              actual_bills=99,
                                                              clan_id=1010)
        args = update_method.call_args[1]
        self.assertFalse(args['is_fast'])
        self.assertEqual(args['premium_end_at'], datetime.datetime.fromtimestamp(666))
        self.assertEqual(args['active_end_at'], datetime.datetime.fromtimestamp(666666))
        self.assertEqual(args['ban_end_at'], datetime.datetime.fromtimestamp(777777))
        self.assertEqual(args['might'], 8888)
        self.assertEqual(args['actual_bills'], 99)
        self.assertEqual(args['clan_id'], 1010)

    def test_stop(self):
        with mock.patch('the_tale.game.logic_storage.LogicStorage.save_all') as save_all:
            self.worker.process_stop()
        self.assertEqual(save_all.call_count, 1)

    def test_release_account(self):
        self.worker.process_register_account(self.account.id)

        with mock.patch('the_tale.game.logic_storage.LogicStorage.release_account_data') as release_account_data:
            self.worker.release_account(self.account.id)

        self.assertEqual(release_account_data.call_count, 1)
        self.assertEqual(release_account_data.call_args_list[0][0][0], self.account.id)

    def test_release_account__account_not_in_logic(self):
        self.worker.process_register_account(self.account.id)

        with mock.patch('the_tale.game.logic_storage.LogicStorage.release_account_data') as release_account_data:
            self.worker.release_account(666)

        self.assertEqual(release_account_data.call_count, 0)

    def test_force_save(self):
        self.worker.process_register_account(self.account.id)

        with mock.patch('the_tale.game.logic_storage.LogicStorage.save_bundle_data') as save_bundle_data:
            self.worker.process_force_save(account_id=self.account.id)

        self.assertEqual(save_bundle_data.call_args_list, [mock.call(bundle_id=self.hero.actions.current_action.bundle_id)])
