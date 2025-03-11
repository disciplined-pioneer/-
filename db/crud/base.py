import logging
from typing import Any, Type

from pydantic import BaseModel

from core.database import async_db_session, engine
from db.models.models import Base


async def init_postgres() -> bool:
    """
        Create all tables in the core
    :return: True or False
    """
    async with async_db_session() as s:
        try:
            # await s.run_sync(
            #     lambda s_value: Base.metadata.drop_all(
            #         bind=s_value.bind
            #     )
            # )

            await s.run_sync(
                lambda s_value: Base.metadata.create_all(
                    bind=s_value.bind
                )
            )

            return True

        except Exception as e:
            logging.exception(e)
            return False


async def close_connections() -> bool:
    """
        Close pool of db connections
    :return: True or False
    """
    async with async_db_session() as s:
        try:
            await engine.dispose()

            return True

        except Exception as e:
            logging.exception(e)
            return False


async def to_pydantic(pydantic_class: Type[BaseModel], data: Any, to_json: bool = False) -> list[BaseModel] | list[dict]:
    """
        Making pydantic class or json from SQLAlchemy table data
    :param pydantic_class: subclass of Pydantic BaseModel
    :param data: result of select() SQLAlchemy request
    :param to_json: make from tabel data json or not
    :return: pydantic model or dict
    """
    if not issubclass(pydantic_class, BaseModel):
        raise ValueError("pydantic_class must be a subclass of BaseModel")

    try:
        if not to_json:
            result = [
                pydantic_class.model_validate(row, from_attributes=True)
                for row in data
            ]

        else:
            result = [
                pydantic_class.model_validate(row, from_attributes=True).model_dump_json()
                for row in data
            ]

        return result

    except Exception as e:
        logging.exception(e)
        raise e


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models.models import User
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from settings import settings

engine = create_async_engine(settings.postgres.URL, echo=True)
async_session_maker = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

async def get_user_data(user_id: int):
    async with async_session_maker() as session:
        try:
            result = await session.execute(select(User).where(User.tg_id == user_id))
            user = result.scalars().first()
            await session.commit()  # Принудительный коммит
            return user
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None