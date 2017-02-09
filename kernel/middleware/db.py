import MySQLdb

OP_CREATE_TABLE = 1
OP_DROP_TABLE = 2
OP_INSERT = 3
OP_DELETE = 4
OP_UPDATE = 5
OP_FIND = 6
OP_COUNT = 7


class DatabaseProxy(object):

    def __init__(self, engine, db_config):
        super(DatabaseProxy, self).__init__()
        self.engine = engine
        if self.engine == 'mysql':
            self.db_client = MysqlDatabase(db_config)
            self.db_client.connect()
        else:
            raise "Database engine not find."

    def __exit__(self):
        self.db_client = None

    def create_table(self, table, columns):
        params = {
            "table": table,
            "definition": ", ".join(columns)
        }
        return self.db_client.execute(OP_CREATE_TABLE, params)

    def drop_table(self, table):
        params = {
            "table": table
        }
        return self.db_client.execute(OP_DROP_TABLE, params)

    def insert(self, table, values):
        self.db_client.format_string(values)
        params = {
            "table": table,
            "values": ", ".join(values)
        }
        return self.db_client.execute(OP_INSERT, params)

    def delete(self, table, condition=None):
        params = {
            "table": table,
            "condition": condition and " ".join(condition) or condition,
        }
        return self.db_client.execute(OP_DELETE, params)

    def update(self, table, expressions, condition=None):
        params = {
            "table": table,
            "expressions": " ".join(expressions),
            "condition": condition and " ".join(condition) or condition,
        }
        return self.db_client.execute(OP_UPDATE, params)

    def find(self, table, columns, condition):
        params = {
            "columns": ", ".join(columns),
            "table": table,
            "condition": " ".join(condition),
        }
        return self.db_client.execute(OP_FIND, params)

    def count(self, table, column="*"):
        params = {
            "column": " ".join(column),
            "table": table,
        }
        return self.db_client.execute(OP_COUNT, params)


class MysqlDatabase(object):
    data_types = {
        'AutoField': 'integer AUTO_INCREMENT',
        'BigAutoField': 'bigint AUTO_INCREMENT',
        'BinaryField': 'longblob',
        'BooleanField': 'bool',
        'CharField': 'varchar(%(max_length)s)',
        'CommaSeparatedIntegerField': 'varchar(%(max_length)s)',
        'DateField': 'date',
        'DateTimeField': 'datetime',
        'DecimalField': 'numeric(%(max_digits)s, %(decimal_places)s)',
        'DurationField': 'bigint',
        'FileField': 'varchar(%(max_length)s)',
        'FilePathField': 'varchar(%(max_length)s)',
        'FloatField': 'double precision',
        'IntegerField': 'integer',
        'BigIntegerField': 'bigint',
        'IPAddressField': 'char(15)',
        'GenericIPAddressField': 'char(39)',
        'NullBooleanField': 'bool',
        'OneToOneField': 'integer',
        'PositiveIntegerField': 'integer UNSIGNED',
        'PositiveSmallIntegerField': 'smallint UNSIGNED',
        'SlugField': 'varchar(%(max_length)s)',
        'SmallIntegerField': 'smallint',
        'TextField': 'longtext',
        'TimeField': 'time',
        'UUIDField': 'char(32)',
    }

    operators = {
        'exact': '= %s',
        'iexact': 'LIKE %s',
        'contains': 'LIKE BINARY %s',
        'icontains': 'LIKE %s',
        'regex': 'REGEXP BINARY %s',
        'iregex': 'REGEXP %s',
        'gt': '> %s',
        'gte': '>= %s',
        'lt': '< %s',
        'lte': '<= %s',
        'startswith': 'LIKE BINARY %s',
        'endswith': 'LIKE BINARY %s',
        'istartswith': 'LIKE %s',
        'iendswith': 'LIKE %s',
    }

    def __init__(self, db_config):
        super(MysqlDatabase, self).__init__()
        self.db_config = db_config
        self.host = self.db_config["HOST"]
        self.port = self.db_config["PORT"]
        self.user = self.db_config["USER"]
        self.passwd = self.db_config["PASSWORD"]
        self.db = self.db_config["NAME"]
        self.connected = False
        self.connection = None
        self.cursor = None

    def __exit__(self):
        self.cursor = None
        if self.connection:
            self.connection.close()

    def connect(self):
        try:
            self.connection = MySQLdb.connect(host=self.host,
                                              port=self.port,
                                              user=self.user,
                                              passwd=self.passwd,
                                              db=self.db,
                                              charset='utf8',
                                              use_unicode=True)
            self.cursor = self.create_cursor()
            self.connected = True
        except MySQLdb.Error as e:
            raise e

    def create_cursor(self):
        cursor = self.connection.cursor()
        return MysqlCursorWrapper(cursor)

    def is_usable(self):
        try:
            self.connection.ping()
        except MySQLdb.Error:
            return False
        else:
            return True

    def execute(self, op, params, args=None):
        sql = None
        if op == OP_CREATE_TABLE:
            sql = MysqlSchema.sql_create_table % params

        elif op == OP_DROP_TABLE:
            sql = MysqlSchema.sql_delete_table % params

        elif op == OP_INSERT:
            sql = MysqlSchema.sql_insert % params

        elif op == OP_DELETE:
            if params['condition']:
                sql = MysqlSchema.sql_delete_where % params
            else:
                sql = MysqlSchema.sql_delete % params

        elif op == OP_UPDATE:
            if params['condition']:
                sql = MysqlSchema.sql_update_where% params
            else:
                sql = MysqlSchema.sql_update % params

        elif op == OP_FIND:
            sql = MysqlSchema.sql_select % params

        elif op == OP_COUNT:
            sql = MysqlSchema.sql_count % params

        else:
            raise "Unknown database operation."

        print sql
        self.cursor.execute(sql, args)
        return self.cursor.fetchall()

    @classmethod
    def format_string(cls, values):
        for i in range(0, len(values)):
            value = values[i]
            values[i] = type(value) == str and "'%s'" % value or str(value)


class MysqlCursorWrapper(object):
    """
    A thin wrapper around MySQLdb's normal cursor class so that we can catch
    particular exception instances and reraise them with the right types.

    Implemented as a wrapper, rather than a subclass, so that we aren't stuck
    to the particular underlying representation returned by Connection.cursor().
    """
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, args=None):
        try:
            # args is None means no string interpolation
            return self.cursor.execute(query, args)
        except MySQLdb.OperationalError as e:
            # Map some error codes to IntegrityError, since they seem to be
            raise e

    def executemany(self, query, args):
        try:
            # args is None means no string interpolation
            return self.cursor.executemany(query, args)
        except MySQLdb.OperationalError as e:
            # Map some error codes to IntegrityError, since they seem to be
            raise e

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __iter__(self):
        return iter(self.cursor)

    def __enter__(self):
        return self

    def __exit__(self):
        self.close()


class BaseSchema(object):
    sql_create_table = "CREATE TABLE %(table)s (%(definition)s)"
    sql_rename_table = "ALTER TABLE %(old_table)s RENAME TO %(new_table)s"
    sql_retablespace_table = "ALTER TABLE %(table)s SET TABLESPACE %(new_tablespace)s"
    sql_delete_table = "DROP TABLE %(table)s CASCADE"

    sql_create_column = "ALTER TABLE %(table)s ADD COLUMN %(column)s %(definition)s"
    sql_alter_column = "ALTER TABLE %(table)s %(changes)s"
    sql_alter_column_type = "ALTER COLUMN %(column)s TYPE %(type)s"
    sql_alter_column_null = "ALTER COLUMN %(column)s DROP NOT NULL"
    sql_alter_column_not_null = "ALTER COLUMN %(column)s SET NOT NULL"
    sql_alter_column_default = "ALTER COLUMN %(column)s SET DEFAULT %(default)s"
    sql_alter_column_no_default = "ALTER COLUMN %(column)s DROP DEFAULT"
    sql_delete_column = "ALTER TABLE %(table)s DROP COLUMN %(column)s CASCADE"
    sql_rename_column = "ALTER TABLE %(table)s RENAME COLUMN %(old_column)s TO %(new_column)s"
    sql_update_with_default = "UPDATE %(table)s SET %(column)s = %(default)s WHERE %(column)s IS NULL"

    sql_create_check = "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s CHECK (%(check)s)"
    sql_delete_check = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_create_unique = "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s UNIQUE (%(columns)s)"
    sql_delete_unique = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_create_fk = (
        "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s FOREIGN KEY (%(column)s) "
        "REFERENCES %(to_table)s (%(to_column)s) DEFERRABLE INITIALLY DEFERRED"
    )
    sql_create_inline_fk = None
    sql_delete_fk = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_create_index = "CREATE INDEX %(name)s ON %(table)s (%(columns)s)%(extra)s"
    sql_delete_index = "DROP INDEX %(name)s"

    sql_create_pk = "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s PRIMARY KEY (%(columns)s)"
    sql_delete_pk = "ALTER TABLE %(table)s DROP CONSTRAINT %(name)s"

    sql_insert = "INSERT INTO %(table)s VALUE (%(values)s)"
    sql_delete = "DELETE FROM %(table)s"
    sql_delete_where = "DELETE FROM %(table)s WHERE %(condition)s"
    sql_delete_where_select = "DELETE FROM %(table)s WHERE %(columns) IN %(select)s"
    sql_update = "UPDATE %(table)s SET %(expressions)s"
    sql_update_where = "UPDATE %(table)s SET %(expressions)s WHERE %(condition)s"
    sql_update_where_select = "UPDATE %(table)s SET %(expressions)s WHERE %(columns) IN %(select)s"
    sql_select = "SELECT %(columns)s FROM %(table)s WHERE %(condition)s"
    sql_count = "SELECT COUNT(%(column)s) FROM %(table)s"


class MysqlSchema(BaseSchema):
    sql_rename_table = "RENAME TABLE %(old_table)s TO %(new_table)s"

    sql_alter_column_null = "MODIFY %(column)s %(type)s NULL"
    sql_alter_column_not_null = "MODIFY %(column)s %(type)s NOT NULL"
    sql_alter_column_type = "MODIFY %(column)s %(type)s"
    sql_rename_column = "ALTER TABLE %(table)s CHANGE %(old_column)s %(new_column)s %(type)s"

    sql_delete_unique = "ALTER TABLE %(table)s DROP INDEX %(name)s"

    sql_create_fk = (
        "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s FOREIGN KEY "
        "(%(column)s) REFERENCES %(to_table)s (%(to_column)s)"
    )
    sql_delete_fk = "ALTER TABLE %(table)s DROP FOREIGN KEY %(name)s"

    sql_delete_index = "DROP INDEX %(name)s ON %(table)s"

    sql_create_pk = "ALTER TABLE %(table)s ADD CONSTRAINT %(name)s PRIMARY KEY (%(columns)s)"
    sql_delete_pk = "ALTER TABLE %(table)s DROP PRIMARY KEY"
