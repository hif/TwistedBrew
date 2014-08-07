import psycopg2
from masters.defaults import *
import utils.logging as log

COLUMN_SMALL = 'varchar(64)'
COLUMN_LARGE = 'varchar(4096)'

BREW_TABLE = 'Brews'
BREW_COLUMNS = '(name, brewer, style, category, description, profile, ingredients, weblink)'
BREW_CREATE_TABLE = 'CREATE TABLE {0} ' \
                    '(name {1}, brewer {1}, style {1}, category {1}, description {2}, profile {2}, ' \
                    'ingredients {2}, weblink {1});'.format(BREW_TABLE, COLUMN_SMALL, COLUMN_LARGE)

WORKER_TABLE = 'Workers'
WORKER_COLUMNS = '(name, type)'
WORKER_CREATE_TABLE = 'CREATE TABLE {0} (name {1}, type {1});'.format(WORKER_TABLE, COLUMN_SMALL)


class DataManager():
    def __init__(self, connectionstring=DefaultDBConnectionString):
        self.connectionstring = connectionstring

    def inittables(self):
        log.debug('Initializing tables')
        try:
            connection = psycopg2.connect(self.connectionstring)
            cursor = connection.cursor()
            self.droptable(BREW_TABLE, connection, cursor)
            self.droptable(WORKER_TABLE, connection, cursor)
            connection.commit()
            try:
                cursor.execute(BREW_CREATE_TABLE)
                connection.commit()
            except Exception, e:
                log.error('Unable to create table {0} ({1})'.format(BREW_TABLE, e))
            try:
                cursor.execute(WORKER_CREATE_TABLE)
                connection.commit()
            except Exception, e:
                log.error('Unable to create table {0} ({1})'.format(WORKER_TABLE, e))
            connection.close()
        except Exception, e:
            log.error(u'Unable to connect to database using {0} ({1})'.format(self.connectionstring, e.message))

    @staticmethod
    def droptable(table, connection, cursor):
        try:
            query = 'DROP TABLE {0}'.format(table)
            cursor.execute(query)
            connection.commit()
        except Exception, e:
            log.debug('Unable to drop table {0} ({1})'.format(table, e.message))

    def insertbrew(self, brew, connection=None):
        try:
            log.debug(u'Inserting brew {0}'.format(brew.name))
            closeconnection = False
            if connection is None:
                closeconnection = True
                connection = psycopg2.connect(self.connectionstring)
            cursor = connection.cursor()
            query = 'INSERT INTO {0} {1}  VALUES (%s, %s, %s, %s, %s, %s, %s, %s);'.format(BREW_TABLE, BREW_COLUMNS)
            data = (brew.name, brew.brewer, brew.style, brew.category, brew.description, brew.profile,
                    brew.ingredients, brew.weblink)
            cursor.execute(query, data)
            connection.commit()
            if closeconnection:
                connection.close()
        except Exception, e:
            log.error(e.message)

    def insertworker(self, worker, connection=None):
        try:
            log.debug(u'Inserting worker {0}'.format(worker.name))
            closeconnection = False
            if connection is None:
                closeconnection = True
                connection = psycopg2.connect(self.connectionstring)
            cursor = connection.cursor()
            query = 'INSERT INTO {0} {1} VALUES (%s, %s);'.format(WORKER_TABLE, WORKER_COLUMNS)
            data = (worker.name, worker.type)
            cursor.execute(query, data)
            connection.commit()
            if closeconnection:
                connection.close()
        except Exception, e:
            log.error(e.message)

    def insertbrews(self, brews):
        try:
            log.debug(u'Inserting brews')
            connection = psycopg2.connect(self.connectionstring)
            for brew in brews:
                self.insertbrew(brew, connection)
            connection.close()
        except Exception, e:
            log.error(e.message)

    def insertworkers(self, workers):
        try:
            log.debug(u'Inserting workers')
            connection = psycopg2.connect(self.connectionstring)
            for worker in workers:
                self.insertworker(worker, connection)
            connection.close()
        except Exception, e:
            log.error(e.message)

    def insertupdate(self, data):
        try:
            log.debug(u'Inserting worker update: {0}'.format(data))
            connection = psycopg2.connect(self.connectionstring)
            connection.close()
        except Exception, e:
            log.error(e.message)

    def clearworkers(self):
        try:
            log.debug(u'Clearing workers from database')
            connection = psycopg2.connect(self.connectionstring)
            cursor = connection.cursor()
            query = 'DELETE FROM {0};'.format(WORKER_TABLE)
            cursor.execute(query)
            connection.commit()
            connection.close()
        except Exception, e:
            log.error(e.message)

