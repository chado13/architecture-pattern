from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapter.repository import SqlalchemyRepository
from app.deps import session
from app.domain import model
from app.schema import OrderLine
from app.services import services as service

app = FastAPI()


def is_valid_sku(sku: str, batches: list[model.Batches]) -> bool:
    return sku in {b.sku for b in batches}


@app.post("/allocate", status_code=status.HTTP_201_CREATED)
async def allocate(
    orderline: OrderLine, session: AsyncSession = Depends(session)
) -> dict[str, str]:
    repo = SqlalchemyRepository(session)
    batches = await repo.fetch()
    line = model.OrderLine(order_id=orderline.order_id, sku=orderline.sku, qty=orderline.qty)

    if not is_valid_sku(line.sku, batches):
        raise HTTPException(status_code=400, detail=f"Invalid sku {line.sku}")

    try:
        batchref = await service.allocate(line, repo, session)
    except model.OutOfStock as e:
        raise HTTPException(status_code=400, detail=f"{e}")
    return {"batchref": batchref}
