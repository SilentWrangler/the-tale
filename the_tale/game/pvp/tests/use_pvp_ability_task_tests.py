# coding: utf-8
import random

from common.utils import testcase

from common.postponed_tasks import FakePostpondTaskPrototype, POSTPONED_TASK_LOGIC_RESULT

from accounts.prototypes import AccountPrototype
from accounts.logic import register_user

from game.logic_storage import LogicStorage
from game.logic import create_test_map

from game.pvp.prototypes import Battle1x1Prototype
from game.pvp.postponed_tasks import UsePvPAbilityTask, USE_PVP_ABILITY_TASK_STATE
from game.pvp.abilities import ABILITIES

class UsePvPAbilityTests(testcase.TestCase):

    def setUp(self):
        super(UsePvPAbilityTests, self).setUp()

        self.p1, self.p2, self.p3 = create_test_map()

        result, account_1_id, bundle_id = register_user('test_user', 'test_user@test.com', '111111')
        result, account_2_id, bundle_id = register_user('test_user_2', 'test_user_2@test.com', '111111')

        self.account_1 = AccountPrototype.get_by_id(account_1_id)
        self.account_2 = AccountPrototype.get_by_id(account_2_id)

        self.storage = LogicStorage()
        self.storage.load_account_data(self.account_1)
        self.storage.load_account_data(self.account_2)

        self.hero_1 = self.storage.accounts_to_heroes[self.account_1.id]
        self.hero_2 = self.storage.accounts_to_heroes[self.account_2.id]

        self.battle = Battle1x1Prototype.create(self.account_1)
        self.battle.set_enemy(self.account_2)
        self.battle.save()

        self.ability = random.choice(ABILITIES.values())

        self.task = UsePvPAbilityTask(battle_id=self.battle.id, account_id=self.account_1.id, ability_id=self.ability.TYPE)

    def test_create(self):
        self.assertEqual(self.task.state, USE_PVP_ABILITY_TASK_STATE.UNPROCESSED)
        self.assertEqual(self.task.battle_id, self.battle.id)
        self.assertEqual(self.task.account_id, self.account_1.id)
        self.assertEqual(self.task.ability_id, self.ability.TYPE)

    def test_serialize(self):
        self.assertEqual(self.task, UsePvPAbilityTask.deserialize(self.task.serialize()))

    def test_process_hero_not_found(self):
        self.storage.release_account_data(self.account_1)
        self.task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, USE_PVP_ABILITY_TASK_STATE.HERO_NOT_FOUND)

    def test_wrong_ability_id(self):
        task = UsePvPAbilityTask(battle_id=self.battle.id, account_id=self.account_1.id, ability_id=u'wrong_ability_id')
        task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(task.state, USE_PVP_ABILITY_TASK_STATE.WRONG_ABILITY_ID)

    def test_no_resources(self):
        self.task.process(FakePostpondTaskPrototype(), self.storage)
        self.assertEqual(self.task.state, USE_PVP_ABILITY_TASK_STATE.NO_ENERGY)

    def test_process_success(self):
        self.hero_1.pvp.energy = 1

        old_hero_1_last_message = self.hero_1.messages.messages[-1]
        old_hero_2_last_message = self.hero_2.messages.messages[-1]

        self.assertEqual(self.task.process(FakePostpondTaskPrototype(), self.storage), POSTPONED_TASK_LOGIC_RESULT.SUCCESS)
        self.assertEqual(self.task.state, USE_PVP_ABILITY_TASK_STATE.PROCESSED)

        self.assertNotEqual(old_hero_1_last_message, self.hero_1.messages.messages[-1])
        self.assertNotEqual(old_hero_2_last_message, self.hero_2.messages.messages[-1])

        self.assertNotEqual(old_hero_1_last_message[2], self.hero_1.messages.ui_info()[-1][2])
        self.assertEqual(old_hero_2_last_message[2], self.hero_2.messages.ui_info()[-1][2])

        self.assertEqual(self.hero_1.pvp.energy, 0)