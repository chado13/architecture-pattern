import datetime
from model import Batch, OrderLine, allocate, OutOfStock
import pytest

def create_batch_and_orderline(sku, qty, order_qty):
    return (
        Batch("batch-001", sku, qty, datetime.datetime.today()),
        OrderLine("batch-001", sku, order_qty)
    )
    
def test_allocate_ok():
    #given
    batch, orderline = create_batch_and_orderline("small-table", 20, 2)
    
    #when
    batch.allocate(orderline)

    #then
    assert batch.available_qty == 18

def test_can_allocate_true():
    #given
    batch, orderline = create_batch_and_orderline("small-table", 20, 2)

    #when, then
    assert batch.can_allocate(orderline)


def test_can_allocate_false_when_available_smaller_than_required():
    #given
    batch, orderline = create_batch_and_orderline("small-table", 2, 4)

    #when, then
    assert batch.can_allocate(orderline) is False

def test_can_allocate_false_when_sku_do_not_match():
    #given
    batch = Batch("batch-001", "small-table", 20, datetime.datetime.today())
    orderline = OrderLine("batch-002", "large-table", 10)

    #when, then
    assert batch.can_allocate(orderline) is False

def test_allocation_is_idempotent():
    #given
    batch, line = create_batch_and_orderline("small-table", 20, 2)

    #when
    batch.allocate(line)
    batch.allocate(line)

    #then
    assert batch.available_qty == 18


def test_prefers_current_stock_batchs_to_shipment():
    in_stock_batch = Batch("in-stock-batch", "retro-clock", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "retro-clock", 100, eta=datetime.datetime.today() + datetime.timedelta(days=1))
    line = OrderLine("oref", "retro-clock", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_qty == 90
    assert shipment_batch.available_qty == 100

def test_prefers_earlier_batchs():
    earlist = Batch("speedy-batch", "minimalist-spoon", 100, eta=datetime.datetime.today())
    medium = Batch("normal-batch", "minimalist-spoon", 100, eta=datetime.datetime.today() + datetime.timedelta(days=1))
    latest = Batch("slow-batch", "minimalist-spoon", 100, eta=datetime.datetime.today()+datetime.timedelta(days=2))
    line = OrderLine("order1", "minimalist-spoon", 10)

    allocate(line, [medium, earlist, latest])

    assert earlist.available_qty == 90
    assert medium.available_qty == 100
    assert latest.available_qty == 100

def test_returns_allocated_batchs_id():
    in_stock_batch = Batch("in-stock-batch-id", "highbrow-poster", 100, eta=None)
    shipment_batch = Batch("shipment-batch-id", "highbrow-poster", 100, eta=datetime.datetime.today() + datetime.timedelta(days=1))
    line = OrderLine("oref", "highbrow-poster", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.id


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "small-fork", 10, eta=datetime.datetime.today())
    allocate(OrderLine("order1", "small-fork", 10), [batch])

    with pytest.raises(OutOfStock, match="small-fork"):
        allocate(OrderLine("order2", "small-fork", 1), [batch])