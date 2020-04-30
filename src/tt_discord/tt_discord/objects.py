
import uuid
import datetime
import dataclasses


@dataclasses.dataclass(frozen=True)
class BindCode:
    code: uuid.UUID
    created_at: datetime.datetime
    expire_at: datetime.datetime
