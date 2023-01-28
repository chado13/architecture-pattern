import app.domain.model as model
from app.adapter.repository import SqlalchemyRepository


def test_repository_can_save_a_batch(session):
    # given
    batch = model.Batches("batch1", "rusty-soapdish", 100, eta=None)
    repo = SqlalchemyRepository(session)

    # when
    repo.add(batch)
    session.commit()

    # then
    rows = list(session.execute("SELECT ref, sku, _purchased_qty, eta FROM batches"))
    assert rows == [("batch1", "rusty-soapdish", 100, None)]


def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch1_id)

    repo = SqlalchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batches("batch1", "generic-sofa", 100, eta=None)

    assert retrieved.sku == expected.sku
    assert retrieved._purchased_qty == expected._purchased_qty
    assert retrieved._allocations == {
        model.OrderLine("order1", "generic-sofa", 12),
    }


def insert_order_line(session):
    session.execute(
        "insert into order_lines (order_id, sku, qty)" 'values ("order1", "generic-sofa", 12)'
    )
    [[orderline_id]] = session.execute(
        "select id from order_lines where order_id=:order_id and sku=:sku",
        dict(order_id="order1", sku="generic-sofa"),
    )
    return orderline_id


def insert_batch(session, batch_id):
    session.execute(
        "insert into batches (ref, sku, _purchased_qty, eta) "
        'values (:batch_id, "generic-sofa", 100, null)',
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        'select id from batches where ref=:batch_id and sku="generic-sofa"', dict(batch_id=batch_id)
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        "insert into allocations (orderline_id, batch_id) " "values (:orderline_id, :batch_id)",
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )
