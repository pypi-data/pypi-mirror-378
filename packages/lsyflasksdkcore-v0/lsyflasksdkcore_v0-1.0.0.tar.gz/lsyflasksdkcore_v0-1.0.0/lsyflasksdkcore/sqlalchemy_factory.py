from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

from lsyflasksdkcore import Model


class SQLAlchemyFactory(object):
    def __init__(self):
        self._db = SQLAlchemy()
        self._model = Model()

    def init_app(self, app):
        self._db.init_app(app)
        self._model.init_app(app)

    def get_db(self) -> SQLAlchemy:
        return self._db

    def get_model(self) -> Model:
        return self._model

    @staticmethod
    def create_db_model():
        custom_metadata = MetaData()
        custom_model = declarative_base(metadata=custom_metadata)
        return custom_model

# 单例实例
sqlalchemy_factory = SQLAlchemyFactory()
