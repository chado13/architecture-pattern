from sqlalchemy.orm import relationship, registry
import sqlalchemy as sa
import model

metadata = sa.MetaData()
mapper_registry = registry()

order_lines = sa.Table(
    "order_lines", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("sku", sa.String(255)),
    sa.Column("qty", sa.Integer, nullable=False),
    sa.Column("order_id", sa.String(255))
)

batches = sa.Table(
    "batches", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("ref", sa.String(255)),
    sa.Column("sku", sa.String(255)),
    sa.Column("_purchased_qty", sa.Integer),
    sa.Column("eta", sa.DateTime)
)

allocations = sa.Table(
    "allocations", metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("batch_id", sa.ForeignKey("batches.id")),
    sa.Column("orderline_id", sa.ForeignKey("order_lines.id"))
)
def start_mappers():
    # sqlalchemy 2.0 version mapper deprecated
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, order_lines)
    mapper_registry.map_imperatively(
        model.Batches,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper, secondary=allocations, collection_class=set,
            )
        },
    )