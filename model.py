from dataclasses import dataclass
import datetime
from typing import NewType

OrderId = NewType("OrderId", str)
Sku = NewType("Sku", str)
Qty = NewType("Qty", int)

@dataclass(frozen=True)
class OrderLine:
    order_id: OrderId
    sku: Sku
    qty: Qty

class OutOfStock(Exception):
    pass

class Batch:
    def __init__(self, id: OrderId, sku: Sku, qty: Qty, eta: datetime.datetime | None):
        self.id = id
        self.sku = sku
        self._purchased_qty=qty
        self.eta = eta
        self._allocations = set()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.id == self.id
    
    def __hash__(self):
        return hash(self.id)

    def __gt__(self, other):
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    @property
    def allocated_qty(self):
        return sum(line.qty for line in self._allocations)

    @property
    def available_qty(self):
        return self._purchased_qty - self.allocated_qty

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_qty >= line.qty

def allocate(line: OrderLine, batchs: list[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batchs) if b.can_allocate(line))
        batch.allocate(line)
        return batch.id
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")
