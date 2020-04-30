import sqlite3


DATABASE = 'earthquake.db'
CREATE_TABLE = '''
    CREATE TABLE IF NOT EXISTS earthquakes (
        created_at timestamp PRIMARY KEY default (strftime('%s','now')),
        fecha_inicio date,
        fecha_fin date,
        magnitud_min real not null,
        magnitud_max real,
        salida text not null
    );
'''


class Database(object):

    def __init__(self):
        try:
            self.connection = sqlite3.connect(DATABASE)
            self.cursor = self.connection.cursor()
            self.cursor.execute(CREATE_TABLE)
            self.connection.commit()
            self.connection.close()
        except sqlite3.DatabaseError as error:
            raise error

    def __call__(self):
        try:
            self.connection = sqlite3.connect(DATABASE)
            self.cursor = self.connection.cursor()
            return self.connection, self.cursor
        except sqlite3.DatabaseError as error:
            raise error
