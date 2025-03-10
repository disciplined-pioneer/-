from core.database import async_db_session
from db.models.models import User

async def get_user_by_tg_id(tg_id: int) -> dict | None:
    async with async_db_session() as session:
        user_obj = await User.get(tg_id=tg_id)

        if user_obj:
            return {
                'subdivision': user_obj.subdivision,
                'full_name': user_obj.full_name
            }
        return None

async def main():
    user = await get_user_by_tg_id(802587774)
    print(user)

# Запуск асинхронной функции
import asyncio
asyncio.run(main())
