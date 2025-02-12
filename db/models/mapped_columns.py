from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, DateTime, text
from sqlalchemy.orm import mapped_column

intpk = Annotated[
    int,
    mapped_column(primary_key=True)
]

unique_big_int = Annotated[
    int,
    mapped_column(
        BigInteger,
        unique=True
    )
]

created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('Europe/Moscow', NOW())")
    )
]

str_3 = Annotated[str, 3]
str_32 = Annotated[str, 32]
str_140 = Annotated[str, 140]
str_240 = Annotated[str, 240]
