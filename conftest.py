import pytest
import sqlalchemy as sa
from orm import mapper_registry, start_mappers
from sqlalchemy.orm import sessionmaker, clear_mappers

@pytest.fixture
def engine():
    engine = sa.create_engine("sqlite:///:memory:")
    mapper_registry.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine):
    start_mappers()
    yield sessionmaker(bind=engine)()
    clear_mappers()