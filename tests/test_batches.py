import datetime
from model import Batches, OrderLine
import pytest

def create_batch_and_orderline(sku, qty, order_qty):
    return (
        Batches("batch-001", sku, qty, datetime.datetime.today()),
        OrderLine("batch-001", sku, order_qty)
    )
    
def test_allocating_to_a_batch_reduces_the_available_quantity():
    #given
    batch, orderline = create_batch_and_orderline("small-table", 20, 2)
    
    #when
    batch.allocate(orderline)

    #then
    assert batch.available_qty == 18

def test_can_allocate_if_available_greater_than_required():
    #given
    batch, orderline = create_batch_and_orderline("small-table", 20, 2)

    #when, then
    assert batch.can_allocate(orderline)


def test_can_allocate_false_when_available_smaller_than_required():
    #given
    batch, orderline = create_batch_and_orderline("small-table", 2, 4)

    #when, then
    assert batch.can_allocate(orderline) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = create_batch_and_orderline("elegant-lamp", 2, 2)
    assert batch.can_allocate(line)


def test_can_allocate_false_when_sku_do_not_match():
    #given
    batch = Batches("batch-001", "small-table", 20, datetime.datetime.today())
    orderline = OrderLine("batch-002", "large-table", 10)

    #when, then
    assert batch.can_allocate(orderline) is False


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batches("batch-001", "uncomfortable-chair", 100, eta=None)
    different_sku_line = OrderLine("order-123", "expensive-toaster", 10)
    assert batch.can_allocate(different_sku_line) is False


def test_allocation_is_idempotent():
    #given
    batch, line = create_batch_and_orderline("small-table", 20, 2)

    #when
    batch.allocate(line)
    batch.allocate(line)

    #then
    assert batch.available_qty == 18


def test_deallocate():
    batch, line = create_batch_and_orderline("expensive-footstool", 20, 2)
    batch.allocate(line)
    batch.deallocate(line)
    assert batch.available_qty == 20


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = create_batch_and_orderline("decorative-trinket", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_qty == 20