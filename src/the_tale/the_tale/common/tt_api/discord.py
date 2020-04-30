
import smart_imports

smart_imports.all()


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

        user = tt_protocol_discord_pb2.User(id=account_id,
                                    nickname=account.nick_verbose)

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
