from app.adapter.repository import AbstractRepository
from app.domain import model


class FakeRepository(AbstractRepository):
    def __init__(self, batches: model.Batches):
        self._batches = set(batches)

    async def add(self, batch: model.Batches) -> None:
        self._batches.add(batch)

    async def get(self, ref: str) -> model.Batches:
        return next(b for b in self._batches if b.ref == ref)

    async def fetch(self) -> list[model.Batches]:
        return list(self._batches)


class FakeSession:
    commited = False

    def commit(self) -> None:
        self.commited = True


def test_returns_allocation() -> None:
    # given
    line = model.OrderLine("o1", "complicated-amp", 10)
    batch = model.Batches("b1", "complicated-amp", 100, eta=None)
    repo = FakeRepository([batch])

    # when
    res = service.allocate(line, repo, FakeSession())

    # then
    assert res == "b1"


def test_commits() -> None:
    line = model.OrderLine("o1", "complicated-amp", 10)
    batch = model.Batches("b1", "complicated-amp", 100, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    service.allocate(line, repo, FakeSession())

    assert session.commited is True
