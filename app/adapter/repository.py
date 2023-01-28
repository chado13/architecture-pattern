import abc

import model

class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batches):
        ...

    @abc.abstractmethod
    def get(self, ref: str) -> model.Batches:
        ...


class SqlalchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, batch: model.Batches):
        self.session.add(batch)

    def get(self, ref:str) -> model.Batches:
        return self.session.query(model.Batches).filter_by(ref=ref).one()
    
    def fetch(self):
        return self.session.query(model.Batches).all()

