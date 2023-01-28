import datetime
from dataclasses import dataclass


@dataclass(unsafe_hash=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class OutOfStock(Exception):
    pass


class Batches:
    def __init__(self, ref: str, sku: str, qty: int, eta: datetime.datetime | None):
        self.ref = ref
        self.sku = sku
        self._purchased_qty = qty
        self.eta = eta
        self._allocations = set()

    def __eq__(self, other: "Batches") -> bool:
        if not isinstance(other, Batches):
            return False
        return other.ref == self.ref

    def __hash__(self):
        return hash(self.ref)

    def __gt__(self, other) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    @property
    def allocated_qty(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_qty(self) -> int:
        return self._purchased_qty - self.allocated_qty

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_qty >= line.qty


def allocate(line: OrderLine, batches: list[Batches]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.ref
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
