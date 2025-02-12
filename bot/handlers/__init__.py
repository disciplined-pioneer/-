from .auth import router as auth
from .commands import router as commands
from .daily_type import router as daily_type
from .expenses import router as expenses
from .qr import router as qr
from .stationery import router as stationery

routers = [
    auth,
    commands,
    daily_type,
    expenses,
    qr,
    stationery
]
