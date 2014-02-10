# coding: utf-8

from rels import Column
from rels.django import DjangoEnum

from questgen.relations import OPTION_MARKERS as QUEST_OPTION_MARKERS

from the_tale.game.balance import constants as c

from the_tale.game.artifacts.models import ARTIFACT_TYPE


class RISK_LEVEL(DjangoEnum):
    health_percent_to_rest = Column()
    experience_modifier = Column()
    power_modifier = Column()
    reward_modifier = Column()

    records = ( ('VERY_HIGH', 0, u'очень высокий', 0.70, 1.30, 1.30, 1.30),
                 ('HIGH',      1, u'высокий', 0.85, 1.15, 1.15, 1.15),
                 ('NORMAL',    2, u'обычный', 1.00, 1.00, 1.00, 1.00),
                 ('LOW',       3, u'низкий', 1.15, 0.85, 0.85, 0.85),
                 ('VERY_LOW',  4, u'очень низкий', 1.30, 0.70, 0.70, 0.70) )


class PREFERENCE_TYPE(DjangoEnum):
    level_required = Column()
    base_name = Column()
    prepair_method = Column(unique=False)
    nullable = Column(unique=False)

    records = ( ('MOB', 0, u'любимая добыча', 43, 'mob', '_prepair_mob', True),
                 ('PLACE', 1, u'родной город', 4, 'place', '_prepair_place', True),
                 ('FRIEND', 2, u'соратник', 13, 'friend', '_prepair_person', True),
                 ('ENEMY', 3, u'противник', 26, 'enemy', '_prepair_person', True),
                 ('ENERGY_REGENERATION_TYPE', 4, u'религиозность', 1, 'energy_regeneration_type', '_prepair_value', False),
                 ('EQUIPMENT_SLOT', 5, u'экипировка', 34, 'equipment_slot', '_prepair_equipment_slot', True),
                 ('RISK_LEVEL', 6, u'уровень риска', 8, 'risk_level', '_prepair_risk_level', False),
                 ('FAVORITE_ITEM', 7, u'любимая вещь', 19, 'favorite_item', '_prepair_equipment_slot', True)
        )


class MONEY_SOURCE(DjangoEnum):

    records = ( ('EARNED_FROM_LOOT', 0, u'заработано продажей добычи'),
                 ('EARNED_FROM_ARTIFACTS', 1, u'заработано продажей артефактов'),
                 ('EARNED_FROM_QUESTS', 2, u'заработано выполнением квестов'),
                 ('EARNED_FROM_HELP', 3, u'получено от хранителя'),

                 ('SPEND_FOR_HEAL', 1000, u'потрачено на лечение'),
                 ('SPEND_FOR_ARTIFACTS', 1001, u'потрачено на покупку артефактов'),
                 ('SPEND_FOR_SHARPENING', 1002, u'потрачено на заточку артефактов'),
                 ('SPEND_FOR_USELESS', 1003, u'потрачено без пользы'),
                 ('SPEND_FOR_IMPACT', 1004, u'потрачено на изменение влияния'),
                 ('SPEND_FOR_EXPERIENCE', 1005, u'потрачено на обучение') )



class ITEMS_OF_EXPENDITURE(DjangoEnum):
    ui_id = Column()
    priority = Column(unique=False, primary=False)
    price_fraction = Column(unique=False, primary=False) # цена в доле от стандартной цены
    money_source = Column()
    description = Column()

    records = ( ('INSTANT_HEAL',        0, u'лечение',           'heal',       12, 0.3, MONEY_SOURCE.SPEND_FOR_HEAL,
                  u'Собирает деньги, чтобы поправить здоровье, когда понадобится.'),
                 ('BUYING_ARTIFACT',     1, u'покупка артефакта', 'artifact',   5,  1.5, MONEY_SOURCE.SPEND_FOR_ARTIFACTS,
                  u'Планирует приобретение новой экипировки.'),
                 ('SHARPENING_ARTIFACT', 2, u'заточка артефакта', 'sharpening', 4,  2.0, MONEY_SOURCE.SPEND_FOR_SHARPENING,
                  u'Собирает на улучшение экипировки.'),
                 ('USELESS',             3, u'бесполезные траты', 'useless',    2,  0.4, MONEY_SOURCE.SPEND_FOR_USELESS,
                  u'Копит золото для не очень полезных но безусловно необходимых трат.'),
                 ('IMPACT',              4, u'изменение влияния', 'impact',     4,  2.5, MONEY_SOURCE.SPEND_FOR_IMPACT,
                  u'Планирует накопить деньжат, чтобы повлиять на «запомнившегося» горожанина.'),
                 ('EXPERIENCE',          5, u'обучение',          'experience', 1,  5.0, MONEY_SOURCE.SPEND_FOR_EXPERIENCE,
                  u'Копит деньги в надежде немного повысить свою грамотность..'))


    @classmethod
    def get_quest_upgrade_equipment_fraction(cls):
        return cls.BUYING_ARTIFACT.price_fraction * 0.75




class EQUIPMENT_SLOT(DjangoEnum):
    artifact_type = Column(related_name='equipment_slot')

    records = ( ('HAND_PRIMARY', 0, u'основная рука', ARTIFACT_TYPE.MAIN_HAND),
                 ('HAND_SECONDARY', 1, u'вспомогательная рука', ARTIFACT_TYPE.OFF_HAND),
                 ('HELMET', 2, u'шлем', ARTIFACT_TYPE.HELMET),
                 ('SHOULDERS', 3, u'наплечники', ARTIFACT_TYPE.SHOULDERS),
                 ('PLATE', 4, u'доспех', ARTIFACT_TYPE.PLATE),
                 ('GLOVES', 5, u'перчатки', ARTIFACT_TYPE.GLOVES),
                 ('CLOAK', 6, u'плащ', ARTIFACT_TYPE.CLOAK),
                 ('PANTS', 7, u'штаны', ARTIFACT_TYPE.PANTS),
                 ('BOOTS', 8, u'сапоги', ARTIFACT_TYPE.BOOTS),
                 ('AMULET', 9, u'амулет', ARTIFACT_TYPE.AMULET),
                 ('RING', 10, u'кольцо', ARTIFACT_TYPE.RING) )


class MODIFIERS(DjangoEnum):
    records = ( ('INITIATIVE', 0, u'инициатива'),
                ('HEALTH', 1, u'здоровье'),
                ('DAMAGE', 2, u'урон'),
                ('SPEED', 3, u'скорость'),
                ('MIGHT_CRIT_CHANCE', 4, u'шанс критического срабатвания способности Хранителя'),
                ('EXPERIENCE', 5, u'опыт'),
                ('MAX_BAG_SIZE', 6, u'максимальный размер рюкзака'),
                ('POWER', 7, u'влияние героя'),
                ('QUEST_MONEY_REWARD', 8, u'денежная награда за выполнение задения'),
                ('BUY_PRICE', 9, u'цена покупки'),
                ('SELL_PRICE', 10, u'цена продажи'),
                ('ITEMS_OF_EXPENDITURE_PRIORITIES', 11, u'приортет трат'),
                ('GET_ARTIFACT_FOR_QUEST', 12, u'получить артефакты за задания'),
                ('BUY_BETTER_ARTIFACT', 13, u'купить лучший артефакт'),
                ('KILL_BEFORE_BATTLE', 14, u'убить монстра перед боем'),
                ('PICKED_UP_IN_ROAD', 15, u'ехать на попутных телегах'),
                ('POWER_TO_FRIEND', 16, u'бонус к влиянию на друга'),
                ('POWER_TO_ENEMY', 17, u'бонус к влиянию на врага'),
                ('QUEST_MARKERS', 18, u'маркеры задания'),
                ('QUEST_MARKERS_REWARD_BONUS', 19, u'бонус наград за правильный выбор'),
                ('FIRST_STRIKE', 20, u'первый удар'),
                ('LOOT_PROBABILITY', 21, u'вероятность получить лут после боя'),
                ('EXP_FOR_KILL', 22, u'опыт за убийство моснтра'),
                ('PEACEFULL_BATTLE', 23, u'мирный бой'),
                ('FRIEND_QUEST_PRIORITY', 24, u'приоритет задания на помощь другу'),
                ('ENEMY_QUEST_PRIORITY', 25, u'приоритет задания на вредительство врагу'),
                ('HONOR_EVENTS', 26, u'события для черт'))



class HABIT_INTERVAL(DjangoEnum):
    female_text = Column()
    neuter_text = Column()
    left_border = Column()
    right_border = Column()


class HABIT_HONOR_INTERVAL(HABIT_INTERVAL):

    records = ( ('LEFT_3', 0, u'бесчестный', u'бесчестная', u'бесчестное', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, u'подлый', u'подлая', u'подлое', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, u'порочный', u'порочная', u'порочное', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, u'у себя на уме', u'у себя на уме', u'у себя на уме', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, u'порядочный', u'порядочная', u'порядочное', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, u'благородный', u'благородная', u'благородное', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, u'хозяин своего слова', u'хозяйка своего слова', u'хозяин своего слова', c.HABITS_RIGHT_BORDERS[5], c.HABITS_RIGHT_BORDERS[6]) )


class HABIT_AGGRESSIVENESS_INTERVAL(HABIT_INTERVAL):
    records = ( ('LEFT_3', 0, u'скорый на расправу', u'скорая на расправу', u'скорое на расправу', -c.HABITS_BORDER, c.HABITS_RIGHT_BORDERS[0]),
                ('LEFT_2', 1, u'вспыльчивый', u'вспыльчивая', u'вспыльчивое', c.HABITS_RIGHT_BORDERS[0], c.HABITS_RIGHT_BORDERS[1]),
                ('LEFT_1', 2, u'задира', u'задира', u'задира', c.HABITS_RIGHT_BORDERS[1], c.HABITS_RIGHT_BORDERS[2]),
                ('NEUTRAL', 3, u'сдержанный', u'сдержанная', u'сдержаное', c.HABITS_RIGHT_BORDERS[2], c.HABITS_RIGHT_BORDERS[3]),
                ('RIGHT_1', 4, u'доброхот', u'доброхот', u'доброхот', c.HABITS_RIGHT_BORDERS[3], c.HABITS_RIGHT_BORDERS[4]),
                ('RIGHT_2', 5, u'миролюбивый', u'миролюбивая', u'миролюбивое', c.HABITS_RIGHT_BORDERS[4], c.HABITS_RIGHT_BORDERS[5]),
                ('RIGHT_3', 6, u'гуманист', u'гуманист', u'гуманист', c.HABITS_RIGHT_BORDERS[5], c.HABITS_RIGHT_BORDERS[6]) )


class HABIT_CHANGE_SOURCE(DjangoEnum):
    quest_marker = Column(unique=False, single_type=False)
    quest_default = Column(unique=False, single_type=False)
    correlation_requirements = Column(unique=False, single_type=False)
    honor = Column(unique=False)
    aggressiveness = Column(unique=False)

    records = ( ('QUEST_HONORABLE', 0, u'выбор чести в задании игроком', QUEST_OPTION_MARKERS.HONORABLE, False, None,           c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
                ('QUEST_DISHONORABLE', 1, u'выбор бесчестия в задании игроком', QUEST_OPTION_MARKERS.DISHONORABLE, False, None,  -c.HABITS_QUEST_ACTIVE_DELTA, 0.0),
                ('QUEST_AGGRESSIVE', 2, u'выборе агрессивности в задании игроком', QUEST_OPTION_MARKERS.AGGRESSIVE, False, None, 0.0, -c.HABITS_QUEST_ACTIVE_DELTA),
                ('QUEST_UNAGGRESSIVE', 3, u'выбор миролюбия в задании игроком', QUEST_OPTION_MARKERS.UNAGGRESSIVE, False, None,  0.0, c.HABITS_QUEST_ACTIVE_DELTA),

                ('QUEST_HONORABLE_DEFAULT', 4, u'выбор чести в задании героем', QUEST_OPTION_MARKERS.HONORABLE, True, False,            c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
                ('QUEST_DISHONORABLE_DEFAULT', 5, u'выбор бесчестия в задании героем', QUEST_OPTION_MARKERS.DISHONORABLE, True, False,  -c.HABITS_QUEST_PASSIVE_DELTA, 0.0),
                ('QUEST_AGGRESSIVE_DEFAULT', 6, u'выборе агрессивности в задании героем', QUEST_OPTION_MARKERS.AGGRESSIVE, True, False, 0.0, -c.HABITS_QUEST_PASSIVE_DELTA),
                ('QUEST_UNAGGRESSIVE_DEFAULT', 7, u'выбор миролюбия в задании героем', QUEST_OPTION_MARKERS.UNAGGRESSIVE, True, False,  0.0, c.HABITS_QUEST_PASSIVE_DELTA),

                ('HELP_AGGRESSIVE', 8, u'помощь в бою', None, None, None,      0.0, -1.0),
                ('HELP_UNAGGRESSIVE', 9, u'помощь вне боя', None, None, None,  0.0, 1.0),
                ('ARENA_SEND', 10, u'отправка на арену', None, None, None,     0.0, -1.0),
                ('ARENA_LEAVE', 11, u'покидание арены', None, None, None,      0.0, 1.0),
                ('PERIODIC', 12, u'периодическое изменение', None, None, None, -1.0, -1.0) )


class HABIT_TYPE(DjangoEnum):
    intervals = Column()

    records = ( ('HONOR', 0, u'честь', HABIT_HONOR_INTERVAL),
                ('AGGRESSIVENESS', 1, u'агрессивность', HABIT_AGGRESSIVENESS_INTERVAL) )
