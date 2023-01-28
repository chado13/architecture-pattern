import sqlalchemy as sa
from sqlalchemy.orm import registry, relationship

import app.domain.model as model

mapper_registry = registry()

order_lines = sa.Table(
    "order_lines",
    mapper_registry.metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("sku", sa.String(255)),
    sa.Column("qty", sa.Integer, nullable=False),
    sa.Column("order_id", sa.String(255)),
)

batches = sa.Table(
    "batches",
    mapper_registry.metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("ref", sa.String(255)),
    sa.Column("sku", sa.String(255)),
    sa.Column("_purchased_qty", sa.Integer),
    sa.Column("eta", sa.DateTime),
)

allocations = sa.Table(
    "allocations",
    mapper_registry.metadata,
    sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
    sa.Column("batch_id", sa.ForeignKey("batches.id")),
    sa.Column("orderline_id", sa.ForeignKey("order_lines.id")),
)


def start_mappers() -> None:
    # sqlalchemy 2.0 version mapper deprecated
    lines_mapper = mapper_registry.map_imperatively(model.OrderLine, order_lines)
    mapper_registry.map_imperatively(
        model.Batches,
        batches,
        properties={
            "_allocations": relationship(
                lines_mapper,
                secondary=allocations,
                collection_class=set,
            )
        },
    )
