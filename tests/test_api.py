import datetime
import uuid
from typing import Any, Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, Any, Any]:
    with TestClient(app) as c:
        yield c


async def test_api_returns_allocation(session: AsyncSession, client: TestClient) -> None:
    sku, othersku = random_sku(), random_sku("ohter")
    earlybatch = random_batchref(1)
    laterbatch = random_batchref(2)
    ohterbatch = random_batchref(3)
    await add_stock(
        session,
        [
            (earlybatch, sku, 100, datetime.datetime(2023, 1, 1)),
            (laterbatch, sku, 100, datetime.datetime(2023, 1, 2)),
            (ohterbatch, othersku, 100, None),
        ],
    )
    data = {"order_id": random_orderid(1), "sku": sku, "qty": 3}
    r = client.post("/allocate", json=data)

    assert r.status_code == 201
    assert r.json() == {"batch_id": earlybatch}


async def test_unhappy_path_returns_400_and_error_message() -> None:
    pass


async def add_stock(
    session: AsyncSession, batchs: list[tuple[str, str, int, datetime.datetime | None]]
) -> None:
    for ref, sku, qty, eta in batchs:
        await session.execute(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
            " VALUES (:ref, :sku, :qty, :eta)",
            dict(ref=ref, sku=sku, qty=qty, eta=eta),
        )


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name: Any = "") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name: Any = "") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: Any = "") -> str:
    return f"order-{name}-{random_suffix()}"