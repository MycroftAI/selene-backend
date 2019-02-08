from glob import glob
from os import path

from psycopg2 import connect

MYCROFT_DB_DIR = '/Users/chrisveilleux/Mycroft/github/devops/db/mycroft'
SCHEMAS = ('account', 'skill', 'device')
DB_DESTROY_FILES = ('drop_db.sql', 'drop_roles.sql')
DB_CREATE_FILES = ('create_db.sql', 'create_roles.sql')
ACCOUNT_TABLE_ORDER = (
    'account',
    'refresh_token',
    'agreement',
    'account_agreement',
    'subscription',
    'account_subscription',
)
SKILL_TABLE_ORDER = (
    'skill',
    'branch',
    'activation',
    'category',
    'credit',
    'platform',
    'setting_version',
    'setting_section',
    'setting',
    'tag',
    'oauth_credential',
    'oauth_token'
)
DEVICE_TABLE_ORDER = (
    'category',
    'location',
    'text_to_speech',
    'wake_word',
    'wake_word_settings',
    'account_preferences',
    'device',
    'device_skill',
    'skill_setting'
)

schema_directory = '{}_schema'


def get_sql_from_file(file_path: str) -> str:
    with open(path.join(MYCROFT_DB_DIR, file_path)) as sql_file:
        sql = sql_file.read()

    return sql


class PostgresDB(object):
    def __init__(self, dbname, user):
        self.db = connect(dbname=dbname, user=user)
        self.db.autocommit = True

    def close_db(self):
        self.db.close()

    def execute_sql(self, sql: str):
        cursor = self.db.cursor()
        cursor.execute(sql)


postgres_db = PostgresDB(dbname='postgres', user='chrisveilleux')

# Destroy any objects we will be creating later.
for db_destroy_file in DB_DESTROY_FILES:
    postgres_db.execute_sql(
        get_sql_from_file(db_destroy_file)
    )

# Create the extensions, mycroft database, and selene roles
for db_setup_file in DB_CREATE_FILES:
    postgres_db.execute_sql(
        get_sql_from_file(db_setup_file)
    )

postgres_db.close_db()

mycroft_db = PostgresDB(dbname='mycroft', user='chrisveilleux')

mycroft_db.execute_sql(
    get_sql_from_file(path.join('create_extensions.sql'))
)

# Create user-defined data types
type_directory = path.join(MYCROFT_DB_DIR, 'types')
for type_file in glob(type_directory + '/*.sql'):
    mycroft_db.execute_sql(
        get_sql_from_file(path.join(type_directory, type_file))
    )

# Create the schemas and grant access
for schema in SCHEMAS:
    mycroft_db.execute_sql(
        get_sql_from_file(schema + '_schema/create_schema.sql')
    )

# Create the account schema tables first as other schemas have tables with
# foreign keys to these tables.
for table in ACCOUNT_TABLE_ORDER:
    create_table_file = path.join(
        'account_schema',
        'tables',
        table + '.sql'
    )
    mycroft_db.execute_sql(
        get_sql_from_file(create_table_file)
    )
    insert_rows_file = path.join(
        'account_schema',
        'data',
        table + '.sql'
    )
    try:
        mycroft_db.execute_sql(
            get_sql_from_file(insert_rows_file)
        )
    except FileNotFoundError:
        pass

# Create the account schema tables first as other schemas have tables with
# foreign keys to these tables.
for table in SKILL_TABLE_ORDER:
    create_table_file = path.join(
        'skill_schema',
        'tables',
        table + '.sql'
    )
    mycroft_db.execute_sql(
        get_sql_from_file(create_table_file)
    )
    insert_rows_file = path.join(
        'skill_schema',
        'data',
        table + '.sql'
    )
    try:
        mycroft_db.execute_sql(
            get_sql_from_file(insert_rows_file)
        )
    except FileNotFoundError:
        pass

# Create the account schema tables first as other schemas have tables with
# foreign keys to these tables.
for table in DEVICE_TABLE_ORDER:
    create_table_file = path.join(
        'device_schema',
        'tables',
        table + '.sql'
    )
    mycroft_db.execute_sql(
        get_sql_from_file(create_table_file)
    )
    insert_rows_file = path.join(
        'device_schema',
        'data',
        table + '.sql'
    )
    try:
        mycroft_db.execute_sql(
            get_sql_from_file(insert_rows_file)
        )
    except FileNotFoundError:
        pass

# Grant access to schemas and tables
for schema in SCHEMAS:
    mycroft_db.execute_sql(
        get_sql_from_file(schema + '_schema/grants.sql')
    )
