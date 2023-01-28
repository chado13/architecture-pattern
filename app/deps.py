from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.db import DB


def db() -> DB:
    return DB(config.db_url)


async def session(db: DB = Depends(db)) -> AsyncGenerator[AsyncSession, None]:
    async with db.session() as session:
        yield session
