# -*- coding: utf-8 -*-
"""
 orm.py  Generated on 2017-09-21 15:43

 Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>

"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.automap import automap_base

from log import LogManager
from settings import DATABASES

class OrmService(object):

    """Provide ORM service. """

    services = dict()

    def __init__(self):
        super(OrmService, self).__init__()

    @staticmethod
    def get_service(db_name):
        if db_name in OrmService.services:
            return OrmService.services[db_name]
        else:
            service = OrmProxy(DATABASES[db_name]['ENGINE'], DATABASES[db_name]['CONFIG'])
            OrmService.services[db_name] = service
            return service


class OrmProxy(object):

    """Wrapper ORM. """

    def __init__(self, engine, db_config):
        super(OrmProxy, self).__init__()
        self.logger = LogManager.get_logger("orm." + self.__class__.__name__)
        self.engine = engine
        self.db_config = db_config
        self.host = self.db_config["HOST"]
        self.port = self.db_config["PORT"]
        self.user = self.db_config["USER"]
        self.passwd = self.db_config["PASSWORD"]
        self.db = self.db_config["NAME"]
        self.connected = False
        self.orm_engine = None

        try:
            if self.engine == 'mysql':
                params = (self.user, self.passwd, self.host, self.port, self.db)
                connect = 'mysql+mysqldb://%s:%s@%s:%s/%s?charset=utf8' % params
                self.orm_engine = create_engine(connect, max_overflow=5,
                                                encoding='utf-8', echo=True)
                self.connected = True
                self.logger.info('init: %s', 'Database engine MySQLdb.')
            else:
                self.logger.error('init: err=%s', 'Database engine not find.')
                raise "Database engine not find."
        except SQLAlchemyError:
            self.logger.error('connect: err=%s', 'Connect orm failed.')
            self.logger.log_last_except()

    def make_session(self):
        Session = sessionmaker(bind=self.orm_engine)
        return Session()

    def commit_session(self, session):
        try:
            session.commit()
            return True
        except SQLAlchemyError:
            session.rollback()
            self.logger.error('commit_session: err=%s', 'Commit error, rollback.')
            self.logger.log_last_except()
            return False

    def load_model(self, table):
        try:
            metadata = MetaData()
            metadata.reflect(self.orm_engine, only=[table])
            Base = automap_base(metadata=metadata)
            Base.prepare()
            return Base.classes[table]
        except SQLAlchemyError:
            self.logger.error('load_model: err=%s', 'Load model failed.')
            self.logger.log_last_except()

