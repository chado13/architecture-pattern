from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapter.repository import AbstractRepository
from app.domain import model
from app.domain.model import OrderLine


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batches]) -> bool:
    return sku in {b.sku for b in batches}


async def allocate(line: OrderLine, repo: AbstractRepository, session: AsyncSession) -> str:
    batches = await repo.fetch()
    if not is_valid_sku(line.sku, batches):
        raise InvalidSku(f"Invalid sku {line.sku}")
    batchref = model.allocate(line, batches)
    session.commit()
    return batchref
