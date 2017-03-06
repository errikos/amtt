"""
db (database) Loader module

TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

Under (heavy) development
"""

import logging

from . import Loader
from errors import LoaderError

# Database table mappings
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Component(Base):
    __tablename__ = 'COMPONENTS'

    type = Column(String, primary_key=True)
    name = Column(String, primary_key=True)
    parent = Column(String, primary_key=True)
    quantity = Column(Integer)
    comment = Column(String)


class Logic(Base):
    __tablename__ = 'LOGIC'

    gate = Column(String, primary_key=True)
    logic = Column(String, primary_key=True)
    comment = Column(String)


_logger = logging.getLogger('loader.db')


def handler(args):
    pass


class DbLoader(Loader):
    """

    """

    def __init__(self, db_url):
        self._db_url = db_url
        self._init_mapping()

    def _init_mapping(self):
        pass

    def load(self, translator):
        pass
