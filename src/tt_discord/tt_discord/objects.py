
import uuid
import datetime
import dataclasses


@dataclasses.dataclass(frozen=True)
class BindCode:
    __slots__ = ('code', 'created_at', 'expire_at')

    code: uuid.UUID
    created_at: datetime.datetime
    expire_at: datetime.datetime
