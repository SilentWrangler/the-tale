import os

from tt_web import utils
from tt_web.tests import helpers as web_helpers

from .. import service
from .. import operations


class BaseTests(web_helpers.BaseTests):

    def create_application(self):
        return service.create_application(get_config())

    async def clean_environment(self, app=None):
        await operations.clean_database()


def get_config():
    config_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'config.json')
    return utils.load_config(config_path)


async def create_accounts(game_ids):
    accounts_infos = []

    for game_id in (666, 777, 888):
        account_info = await operations.create_account(game_id=game_id)
        accounts_infos.append(account_info)

    return accounts_infos
