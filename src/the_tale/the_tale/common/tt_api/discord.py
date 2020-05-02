
import smart_imports

smart_imports.all()


class DISCORD_ROLE(rels_django.DjangoEnum):
    records = (('DEVELOPER', 0, 'Разработчик'),
               ('MODERATOR', 1, 'Модератор'),
               ('PILLAR_OF_WORLD', 2, 'Столп Мира'),
               ('MIGHTY_KEEPER', 3, 'Могучий Хранитель'),
               ('KEEPER', 4, 'Хранитель'),
               ('SPIRIT_OF_PANDORA', 5, 'Дух Пандоры'))


@dataclasses.dataclass(frozen=True)
class BindCode:
    __slots__ = ('code', 'created_at', 'expire_at')

    code: uuid.UUID
    created_at: datetime.datetime
    expire_at: datetime.datetime


class Client(client.Client):
    __slots__ = ()

    def protobuf_to_bind_code(self, pb_bind_code):
        return BindCode(code=uuid.UUID(pb_bind_code.code),
                        created_at=datetime.datetime.fromtimestamp(pb_bind_code.created_at),
                        expire_at=datetime.datetime.fromtimestamp(pb_bind_code.expire_at))

    def cmd_get_bind_code(self, account_id, expire_timeout):

        account = accounts_prototypes.AccountPrototype.get_by_id(account_id)

        ##########
        # nickname
        ##########
        nickname = account.nick_verbose

        if account.clan_id is not None:
            membership = clans_logic.get_membership(account_id)
            nickname = f'[{clans_storage.infos[account.clan_id].abbr}] {membership.role.symbol} {nickname}'

        #######
        # roles
        #######

        roles = set()

        if account_id in accounts_conf.settings.DEVELOPERS_IDS:
            roles.add(DISCORD_ROLE.DEVELOPER)

        if account_id in accounts_conf.settings.MODERATORS_IDS:
            roles.add(DISCORD_ROLE.MODERATOR)

        if account.might >= 10000:
            roles.add(DISCORD_ROLE.PILLAR_OF_WORLD)

        elif account.might >= 1000:
            roles.add(DISCORD_ROLE.MIGHTY_KEEPER)

        elif account.might >= 100:
            roles.add(DISCORD_ROLE.KEEPER)

        else:
            roles.add(DISCORD_ROLE.SPIRIT_OF_PANDORA)

        ######################
        # communicate with bot
        ######################
        user = tt_protocol_discord_pb2.User(id=account_id,
                                            nickname=nickname,
                                            roles=[role.name.lower() for role in roles])

        request = tt_protocol_discord_pb2.GetBindCodeRequest(user=user,
                                                             expire_timeout=expire_timeout)

        answer = operations.sync_request(url=self.url('get-bind-code'),
                                         data=request,
                                         AnswerType=tt_protocol_discord_pb2.GetBindCodeResponse)

        return self.protobuf_to_bind_code(answer.code)

    def cmd_debug_clear_service(self):
        if not django_settings.TESTS_RUNNING:
            return

        operations.sync_request(url=self.url('debug-clear-service'),
                                data=tt_protocol_discord_pb2.DebugClearServiceRequest(),
                                AnswerType=tt_protocol_discord_pb2.DebugClearServiceResponse)
