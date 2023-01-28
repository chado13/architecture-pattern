import abc

from sqlalchemy.ext.asyncio import AsyncSession

import app.domain.model as model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def add(self, batch: model.Batches) -> None:
        ...

    @abc.abstractmethod
    async def get(self, ref: str) -> model.Batches:
        ...

    @abc.abstractmethod
    async def fetch(self) -> list[model.Batches]:
        ...


class SqlalchemyRepository(AbstractRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, batch: model.Batches) -> None:
        await self.session.add(batch)

    async def get(self, ref: str) -> model.Batches:
        return await self.session.query(model.Batches).filter_by(ref=ref).one()

    async def fetch(self) -> list[model.Batches]:
        return await self.session.query(model.Batches).all()
