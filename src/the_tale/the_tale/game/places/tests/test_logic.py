
import smart_imports

smart_imports.all()


class GetAvailablePositionsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

    def test_get_available_positions(self):

        building = logic.create_building(self.place_1.persons[0], utg_name=game_names.generator().get_test_name(name='building-name'))

        positions = logic.get_available_positions(self.place_1.x, self.place_1.y)

        self.assertTrue(positions)

        for place in storage.places.all():
            self.assertFalse((place.x, place.y) in positions)

        for building in storage.buildings.all():
            self.assertFalse((building.x, building.y) in positions)

        for x, y in positions:
            self.assertTrue(0 <= x < map_conf.settings.WIDTH)
            self.assertTrue(0 <= y < map_conf.settings.HEIGHT)

    def test_dynamic_position_radius(self):
        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = logic.get_available_positions(-3, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2)]))

        with mock.patch('the_tale.game.balance.constants.BUILDING_POSITION_RADIUS', 2):
            positions = logic.get_available_positions(-4, -1)
            self.assertEqual(positions, set([(0, 0), (0, 1), (0, 2), (0, 3)]))


class TTPowerImpactsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.actor_type = tt_api_impacts.OBJECT_TYPE.HERO
        self.actor_id = 666
        self.amount = 100500
        self.fame = 1000

        self.expected_power = round(self.place_1.attrs.freedom * self.amount)

    def test_inner_circle(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.fame)])

    def test_outer_circle(self):
        impacts = list(logic.tt_power_impacts(inner_circle=False,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.FAME,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.fame)])

    def test_amount_below_zero(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=-self.amount,
                                              fame=-self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=-self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=-self.expected_power)])

    def test_fame_only_for_hero(self):
        actor_type = tt_api_impacts.OBJECT_TYPE.random(exclude=(tt_api_impacts.OBJECT_TYPE.HERO,))

        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=self.amount,
                                              fame=self.fame))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=self.expected_power)])

    def test_zero(self):
        impacts = list(logic.tt_power_impacts(inner_circle=True,
                                              actor_type=self.actor_type,
                                              actor_id=self.actor_id,
                                              place=self.place_1,
                                              amount=0,
                                              fame=0))

        self.assertCountEqual(impacts,
                              [game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.OUTER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=0),
                               game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                            actor_type=self.actor_type,
                                                            actor_id=self.actor_id,
                                                            target_type=tt_api_impacts.OBJECT_TYPE.PLACE,
                                                            target_id=self.place_1.id,
                                                            amount=0)])


def fake_tt_power_impacts(**kwargs):
    yield kwargs


class ImpactsFromHeroTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.place_1, self.place_2, self.place_3 = game_logic.create_test_map()

        self.account = self.accounts_factory.create_account()
        self.hero = heroes_logic.load_hero(account_id=self.account.id)

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: False)
    def test_can_not_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 0,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'inner_circle': False,
                                             'place': self.place_1}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: True)
    def test_can_change_power(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=1000,
                                                        inner_circle_places={self.place_2.id},
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'inner_circle': False,
                                             'place': self.place_1}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: True)
    def test_inner_circle(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.place_1)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=1000,
                                                        inner_circle_places=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'inner_circle': True,
                                             'place': self.place_1}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: True)
    def test_inner_circle__extended_inner_circle(self):
        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=1000,
                                                        inner_circle_places={self.place_1.id},
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': 1000,
                                             'fame': c.HERO_FAME_PER_HELP,
                                             'inner_circle': True,
                                             'place': self.place_1}])

    @mock.patch('the_tale.game.heroes.objects.Hero.can_change_place_power', lambda self, place: True)
    def test_power_below_zero(self):
        self.hero.preferences.set(heroes_relations.PREFERENCE_TYPE.PLACE, self.place_1)

        impact_arguments = list(logic.impacts_from_hero(hero=self.hero,
                                                        place=self.place_1,
                                                        power=-1000,
                                                        inner_circle_places=set(),
                                                        impacts_generator=fake_tt_power_impacts))
        self.assertEqual(impact_arguments, [{'actor_id': self.hero.id,
                                             'actor_type': tt_api_impacts.OBJECT_TYPE.HERO,
                                             'amount': -1000,
                                             'fame': 0,
                                             'inner_circle': True,
                                             'place': self.place_1}])


class GetStartPlaceForRaceTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = list(game_logic.create_test_map())
        self.races = {place.race for place in self.places}

        self.assertTrue(len(self.places), 3)

    def test_no_frontier(self):
        unexisted_race = game_relations.RACE.random(exclude=self.races)

        for target_place in self.places:
            for place in self.places:
                place.is_frontier = (place.id != target_place.id)

            found_place = logic.get_start_place_for_race(unexisted_race)

            self.assertEqual(found_place.id, target_place.id)

    def test_best_security(self):
        unexisted_race = game_relations.RACE.random(exclude=self.races)

        for place in self.places:
            place.is_frontier = False
            place.attrs.safety = random.uniform(0, 1)

        found_place = logic.get_start_place_for_race(unexisted_race)

        self.assertTrue(all(place.attrs.safety <= found_place.attrs.safety
                            for place in self.places))

    @mock.patch('the_tale.game.places.conf.settings.START_PLACE_SAFETY_PERCENTAGE', 1.0)
    def test_filter_by_race(self):
        race = game_relations.RACE.random()

        for place in self.places:
            place.is_frontier = False

        self.places[0].race = race
        self.places[0].attrs.safety = 0.1

        self.places[1].race = game_relations.RACE.random(exclude=[race])
        self.places[1].attrs.safety = 1.0

        self.places[2].race = race
        self.places[2].attrs.safety = 0.2

        found_place = logic.get_start_place_for_race(race)

        self.assertEqual(found_place.id, self.places[2].id)

    @mock.patch('the_tale.game.places.conf.settings.START_PLACE_SAFETY_PERCENTAGE', 0.2)
    def test_filter_by_race__after_safety_limitation(self):
        race = game_relations.RACE.random()

        for place in self.places:
            place.is_frontier = False

        self.places[0].race = race
        self.places[0].attrs.safety = 0.1

        self.places[1].race = game_relations.RACE.random(exclude=[race])
        self.places[1].attrs.safety = 1.0

        self.places[2].race = race
        self.places[2].attrs.safety = 0.2

        found_place = logic.get_start_place_for_race(race)

        self.assertEqual(found_place.id, self.places[1].id)


class ChoosePlaceCellByTerrainTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = list(game_logic.create_test_map())

        self.assertTrue(len(map_storage.cells.place_cells(self.places[0].id)) > 1)

    def test_no_terrains(self):
        expected_cells = set(map_storage.cells.place_cells(self.places[0].id))

        cells = set()

        while cells != expected_cells:
            cells.add(logic.choose_place_cell_by_terrain(self.places[0].id, terrains=()))

    def test_filter_by_terrains__has_terrains(self):
        x, y = logic.choose_place_cell_by_terrain(self.places[0].id, terrains=())

        terrain = map_storage.cells(x, y).terrain

        for i in range(100):
            test_x, test_y = logic.choose_place_cell_by_terrain(self.places[0].id, terrains=())
            self.assertEqual(map_storage.cells(test_x, test_y).terrain, terrain)

    def test_filter_by_terrains__no_terrains(self):
        expected_cells = set(map_storage.cells.place_cells(self.places[0].id))

        cells = set()

        existed_terrains = {map_storage.cells(*cell).terrain for cell in expected_cells}

        unexisted_terrain = map_relations.TERRAIN.random(exclude=existed_terrains)

        while cells != expected_cells:
            cells.add(logic.choose_place_cell_by_terrain(self.places[0].id, terrains=(unexisted_terrain,)))


class SyncPowerEconomicTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        game_tt_services.debug_clear_service()

    def test(self):
        impacts = []
        for power, place in zip((100, 300, 200), self.places):
            impacts.append(game_tt_services.PowerImpact.hero_2_place(type=game_tt_services.IMPACT_TYPE.INNER_CIRCLE,
                                                                     hero_id=1,
                                                                     place_id=place.id,
                                                                     amount=power))
        politic_power_logic.add_power_impacts(impacts)

        politic_power_storage.places.sync(force=True)

        logic.sync_power_economic(self.places, 5)

        self.assertEqual(self.places[0].attrs.power_economic, 2)
        self.assertEqual(self.places[1].attrs.power_economic, 4)
        self.assertEqual(self.places[2].attrs.power_economic, 3)


class SyncMoneyEconomicTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()
        self.places = game_logic.create_test_map()

        game_tt_services.debug_clear_service()

    def test(self):
        for money, place in zip((100, 300, 200), self.places):
            logic.register_money_transaction(hero_id=1, place_id=place.id, amount=money)

        logic.sync_money_economic(self.places, 5)

        self.assertEqual(self.places[0].attrs.money_economic, 2)
        self.assertEqual(self.places[1].attrs.money_economic, 4)
        self.assertEqual(self.places[2].attrs.money_economic, 3)


class UpdateEffectsTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        tt_services.effects.cmd_debug_clear_service()

        self.places = game_logic.create_test_map()

        game_tt_services.debug_clear_service()

    def create_effect(self, place_id, value, attribute, delta=None):
        effect = tt_api_effects.Effect(id=None,
                                       attribute=attribute,
                                       entity=place_id,
                                       value=value,
                                       name='test',
                                       delta=delta)
        return tt_services.effects.cmd_register(effect)

    def test_stability__reduce_effects(self):

        tt_services.effects.cmd_debug_clear_service()

        effect_1_id = self.create_effect(self.places[0].id, -0.5, places_relations.ATTRIBUTE.STABILITY, delta=0.1)
        effect_2_id = self.create_effect(self.places[0].id, 0.25, places_relations.ATTRIBUTE.STABILITY, delta=0.2)
        effect_3_id = self.create_effect(self.places[1].id, 0.5, places_relations.ATTRIBUTE.STABILITY, delta=0.6)

        places_storage.effects.refresh()

        logic.update_effects()

        self.assertAlmostEqual(storage.effects[effect_1_id].value, -0.4)
        self.assertAlmostEqual(storage.effects[effect_2_id].value, 0.05)
        self.assertNotIn(effect_3_id, storage.effects)

    def test_normal_attribute_reduce_effects(self):
        effect_1_id = self.create_effect(self.places[0].id, -500, places_relations.ATTRIBUTE.PRODUCTION, delta=100)
        effect_2_id = self.create_effect(self.places[0].id, 250, places_relations.ATTRIBUTE.PRODUCTION, delta=150)
        effect_3_id = self.create_effect(self.places[1].id, 400, places_relations.ATTRIBUTE.PRODUCTION, delta=1)

        places_storage.effects.refresh()

        logic.update_effects()

        self.assertEqual(storage.effects[effect_1_id].value, -400)
        self.assertEqual(storage.effects[effect_2_id].value, 100)
        self.assertEqual(storage.effects[effect_3_id].value, 399)

    def test_remove_attribute(self):
        effect_1_id = self.create_effect(self.places[0].id, 100, places_relations.ATTRIBUTE.PRODUCTION, delta=49)
        effect_2_id = self.create_effect(self.places[0].id, 100, places_relations.ATTRIBUTE.PRODUCTION, delta=99)
        effect_3_id = self.create_effect(self.places[1].id, 100, places_relations.ATTRIBUTE.PRODUCTION, delta=33)

        places_storage.effects.refresh()

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         {effect_1_id, effect_2_id, effect_3_id})

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         {effect_1_id, effect_3_id})

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         {effect_3_id})

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         set())

    def test_skip_effect_without_delta(self):
        effect_1_id = self.create_effect(self.places[0].id, 100, places_relations.ATTRIBUTE.PRODUCTION, delta=49)
        effect_2_id = self.create_effect(self.places[0].id, 100, places_relations.ATTRIBUTE.PRODUCTION, delta=None)
        effect_3_id = self.create_effect(self.places[1].id, 100, places_relations.ATTRIBUTE.PRODUCTION, delta=33)

        places_storage.effects.refresh()

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         {effect_1_id, effect_2_id, effect_3_id})

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         {effect_1_id, effect_2_id, effect_3_id})

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         {effect_2_id, effect_3_id})

        logic.update_effects()

        self.assertEqual(set(effect.id for effect in storage.effects.all()),
                         {effect_2_id})

        places_storage.effects.refresh()
        self.assertEqual(places_storage.effects[effect_2_id].value, 100)


class RegisterEffectTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        tt_services.effects.cmd_debug_clear_service()

        self.places = game_logic.create_test_map()

    def test(self):
        with self.check_almost_delta(lambda: self.places[0].attrs.culture, 0.33):
            with self.check_delta(lambda: len(storage.effects.all()), 1):
                with self.check_changed(lambda: storage.places._version):
                    with self.check_changed(lambda: storage.effects._version):
                        effect_id = logic.register_effect(place_id=self.places[0].id,
                                                          attribute=relations.ATTRIBUTE.CULTURE,
                                                          value=0.33,
                                                          name='test.effect',
                                                          delta=3,
                                                          info={'test': 'tset'},
                                                          refresh_effects=True,
                                                          refresh_places=True)

        effect = storage.effects[effect_id]

        self.assertEqual(effect.id, effect_id)
        self.assertEqual(effect.entity, self.places[0].id)
        self.assertTrue(effect.attribute.is_CULTURE)
        self.assertEqual(effect.value, 0.33)
        self.assertEqual(effect.name, 'test.effect')
        self.assertEqual(effect.delta, 3)
        self.assertEqual(effect.info, {'test': 'tset'})

    def test_without_refresh(self):
        with self.check_not_changed(lambda: self.places[0].attrs.culture):
            with self.check_not_changed(lambda: len(storage.effects.all())):
                with self.check_not_changed(lambda: storage.places._version):
                    with self.check_not_changed(lambda: storage.effects._version):
                        logic.register_effect(place_id=self.places[0].id,
                                              attribute=relations.ATTRIBUTE.CULTURE,
                                              value=0.33,
                                              name='test.effect',
                                              delta=3,
                                              info={'test': 'tset'})

    def test_rewritable_type(self):
        self.assertTrue(relations.ATTRIBUTE.CLAN_PROTECTOR.type.is_REWRITABLE)

        with self.check_delta(lambda: len(storage.effects.all()), 1):
            with self.check_changed(lambda: storage.places._version):
                with self.check_changed(lambda: storage.effects._version):
                    effect_1_id = logic.register_effect(place_id=self.places[0].id,
                                                        attribute=relations.ATTRIBUTE.CLAN_PROTECTOR,
                                                        value=33,
                                                        name='test.effect',
                                                        delta=3,
                                                        info={'test': 'tset'},
                                                        refresh_effects=True,
                                                        refresh_places=True)

                    effect_2_id = logic.register_effect(place_id=self.places[0].id,
                                                        attribute=relations.ATTRIBUTE.CLAN_PROTECTOR,
                                                        value=777,
                                                        name='test.effect.2',
                                                        delta=4,
                                                        info={'test': 'tset.2'},
                                                        refresh_effects=True,
                                                        refresh_places=True)

        self.assertEqual(self.places[0].attrs.clan_protector, 777)

        self.assertNotIn(effect_1_id, storage.effects)

        effect = storage.effects[effect_2_id]

        self.assertEqual(effect.id, effect_2_id)
        self.assertEqual(effect.entity, self.places[0].id)
        self.assertTrue(effect.attribute.is_CLAN_PROTECTOR)
        self.assertEqual(effect.value, 777)
        self.assertEqual(effect.name, 'test.effect.2')
        self.assertEqual(effect.delta, 4)
        self.assertEqual(effect.info, {'test': 'tset.2'})


class RemoveEffectTests(utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        tt_services.effects.cmd_debug_clear_service()

        self.places = game_logic.create_test_map()

        self.effect_id = logic.register_effect(place_id=self.places[0].id,
                                               attribute=relations.ATTRIBUTE.CULTURE,
                                               value=0.33,
                                               name='test.effect',
                                               delta=3,
                                               info={'test': 'tset'},
                                               refresh_effects=True,
                                               refresh_places=True)

    def test(self):
        with self.check_almost_delta(lambda: self.places[0].attrs.culture, -0.33):
            with self.check_delta(lambda: len(storage.effects.all()), -1):
                with self.check_changed(lambda: storage.places._version):
                    with self.check_changed(lambda: storage.effects._version):
                        logic.remove_effect(effect_id=self.effect_id,
                                            place_id=self.places[0].id,
                                            refresh_effects=True,
                                            refresh_places=True)

        self.assertNotIn(self.effect_id, storage.effects)

    def test_without_refresh(self):
        with self.check_not_changed(lambda: self.places[0].attrs.culture):
            with self.check_not_changed(lambda: len(storage.effects.all())):
                with self.check_not_changed(lambda: storage.places._version):
                    with self.check_not_changed(lambda: storage.effects._version):
                        logic.remove_effect(effect_id=self.effect_id,
                                            place_id=self.places[0].id)

        self.assertIn(self.effect_id, storage.effects)


class ProtectorCandidatesTests(clans_helpers.ClansTestsMixin,
                               emissaries_helpers.EmissariesTestsMixin,
                               utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        tt_services.effects.cmd_debug_clear_service()

        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.accounts = []
        self.clans = []
        self.emissaries = []

        for i in range(3):
            self.accounts.append(self.accounts_factory.create_account())
            self.clans.append(self.create_clan(owner=self.accounts[-1], uid=i))

            if i == 2:
                place_id = self.places[1].id
            else:
                place_id = self.places[0].id

            self.emissaries.append(self.create_emissary(clan=self.clans[-1],
                                                        initiator=self.accounts[-1],
                                                        place_id=place_id))

        for emissary in self.emissaries:
            politic_power_logic.add_power_impacts([game_tt_services.PowerImpact(type=game_tt_services.IMPACT_TYPE.EMISSARY_POWER,
                                                                                actor_type=tt_api_impacts.OBJECT_TYPE.HERO,
                                                                                actor_id=666,
                                                                                target_type=tt_api_impacts.OBJECT_TYPE.EMISSARY,
                                                                                target_id=emissary.id,
                                                                                amount=1000000)])

    def test_no_candidates(self):
        self.assertEqual(logic.protector_candidates(self.places[0].id), set())

    def test_has_candidates(self):
        emissaries_logic.create_event(initiator=self.accounts[0],
                                      emissary=self.emissaries[0],
                                      concrete_event=emissaries_events.Revolution(raw_ability_power=666),
                                      days=7)

        self.assertEqual(logic.protector_candidates(self.places[0].id), {self.clans[0].id})

        emissaries_logic.create_event(initiator=self.accounts[1],
                                      emissary=self.emissaries[1],
                                      concrete_event=emissaries_events.Revolution(raw_ability_power=666),
                                      days=7)

        self.assertEqual(logic.protector_candidates(self.places[0].id), {self.clans[0].id, self.clans[1].id})

        emissaries_logic.create_event(initiator=self.accounts[2],
                                      emissary=self.emissaries[2],
                                      concrete_event=emissaries_events.Revolution(raw_ability_power=666),
                                      days=7)

        self.assertEqual(logic.protector_candidates(self.places[0].id), {self.clans[0].id, self.clans[1].id})


class RemoveProtectoratTests(helpers.PlacesTestsMixin,
                             clans_helpers.ClansTestsMixin,
                             emissaries_helpers.EmissariesTestsMixin,
                             utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        tt_services.effects.cmd_debug_clear_service()

        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

    def test_no_protectorat(self):
        self.assertEqual(self.places[0].attrs.clan_protector, None)

        logic.remove_protectorat(self.places[0])

        self.assertEqual(self.places[0].attrs.clan_protector, None)

    def test_has_protectorat(self):

        self.set_protector(place_id=self.places[0].id,
                           clan_id=self.clan.id)

        self.assertEqual(self.places[0].attrs.clan_protector, self.clan.id)

        logic.remove_protectorat(self.places[0],
                                 refresh_effects=True,
                                 refresh_places=True)

        self.assertEqual(self.places[0].attrs.clan_protector, None)


class SyncProtectoratTests(helpers.PlacesTestsMixin,
                           clans_helpers.ClansTestsMixin,
                           emissaries_helpers.EmissariesTestsMixin,
                           utils_testcase.TestCase):

    def setUp(self):
        super().setUp()

        tt_services.effects.cmd_debug_clear_service()

        self.places = game_logic.create_test_map()

        self.prepair_forum_for_clans()

        self.account = self.accounts_factory.create_account()
        self.clan = self.create_clan(owner=self.account, uid=1)

    def test_no_protectorat(self):
        self.assertEqual(self.places[0].attrs.clan_protector, None)

        logic.sync_protectorat(self.places[0])

        self.assertEqual(self.places[0].attrs.clan_protector, None)

    def test_no_emissary(self):
        self.set_protector(place_id=self.places[0].id,
                           clan_id=self.clan.id)

        # create emissary from other clan
        account_2 = self.accounts_factory.create_account()
        clan_2 = self.create_clan(owner=account_2, uid=2)
        self.create_emissary(clan=clan_2,
                             initiator=account_2,
                             place_id=self.places[0].id)

        self.assertEqual(self.places[0].attrs.clan_protector, self.clan.id)

        logic.sync_protectorat(self.places[0])

        self.assertEqual(self.places[0].attrs.clan_protector, None)

    def test_has_emissary(self):
        self.set_protector(place_id=self.places[0].id,
                           clan_id=self.clan.id)

        self.assertEqual(self.places[0].attrs.clan_protector, self.clan.id)

        self.create_emissary(clan=self.clan,
                             initiator=self.account,
                             place_id=self.places[0].id)

        logic.sync_protectorat(self.places[0])

        self.assertEqual(self.places[0].attrs.clan_protector, self.clan.id)
