from glob import glob
from os import path

from psycopg2 import connect

MYCROFT_DB_DIR = path.join(path.abspath('..'), 'mycroft')
SCHEMAS = ('account', 'skill', 'device', 'geography')
DB_DESTROY_FILES = (
    'drop_mycroft_db.sql',
    'drop_template_db.sql',
    # 'drop_roles.sql'
)
DB_CREATE_FILES = (
    # 'create_roles.sql',
    'create_template_db.sql',
)
ACCOUNT_TABLE_ORDER = (
    'account',
    'agreement',
    'account_agreement',
    'membership',
    'account_membership',
)
SKILL_TABLE_ORDER = (
    'skill',
    'settings_display',
    'display',
    'oauth_credential',
    'oauth_token'
)
DEVICE_TABLE_ORDER = (
    'category',
    'geography',
    'text_to_speech',
    'wake_word',
    'wake_word_settings',
    'account_preferences',
    'account_defaults',
    'device',
    'device_skill',
)
GEOGRAPHY_TABLE_ORDER = (
    'country',
    'timezone',
    'region',
    'city'
)

schema_directory = '{}_schema'


def get_sql_from_file(file_path: str) -> str:
    with open(path.join(MYCROFT_DB_DIR, file_path)) as sql_file:
        sql = sql_file.read()

    return sql


class PostgresDB(object):
    def __init__(self, dbname, user, password=None):
        # self.db = connect(dbname=dbname, user=user, host='127.0.0.1')
        self.db = connect(
            dbname=dbname,
            user=user,
            password=password,
            host='selene-test-db-do-user-1412453-0.db.ondigitalocean.com',
            port=25060,
            sslmode='require'
        )
        self.db.autocommit = True

    def close_db(self):
        self.db.close()

    def execute_sql(self, sql: str):
        cursor = self.db.cursor()
        cursor.execute(sql)


# postgres_db = PostgresDB(dbname='postgres', user='chrisveilleux')
postgres_db = PostgresDB(
    dbname='defaultdb',
    user='doadmin',
    password='l06tn0qi2bjhgcki'
)

print('Destroying any objects we will be creating later.')
for db_destroy_file in DB_DESTROY_FILES:
    postgres_db.execute_sql(
        get_sql_from_file(db_destroy_file)
    )

print('Creating the extensions, mycroft database, and selene roles')
for db_setup_file in DB_CREATE_FILES:
    postgres_db.execute_sql(
        get_sql_from_file(db_setup_file)
    )

postgres_db.close_db()

# template_db = PostgresDB(dbname='mycroft_template', user='mycroft')
template_db = PostgresDB(
    dbname='mycroft_template',
    user='selene',
    password='ubhemhx1dikmqc5f'
)

template_db.execute_sql(
    get_sql_from_file(path.join('create_extensions.sql'))
)

print('Creating user-defined data types')
type_directory = path.join(MYCROFT_DB_DIR, 'types')
for type_file in glob(type_directory + '/*.sql'):
    template_db.execute_sql(
        get_sql_from_file(path.join(type_directory, type_file))
    )

print('Create the schemas and grant access')
for schema in SCHEMAS:
    template_db.execute_sql(
        get_sql_from_file(schema + '_schema/create_schema.sql')
    )

print('Creating the account schema tables')
# These are created first as other schemas have tables with
# foreign keys to these tables.
for table in ACCOUNT_TABLE_ORDER:
    create_table_file = path.join(
        'account_schema',
        'tables',
        table + '.sql'
    )
    template_db.execute_sql(
        get_sql_from_file(create_table_file)
    )

print('Creating the skill schema tables')
# Create the skill schema tables second as other schemas have tables with
# foreign keys to these tables.
for table in SKILL_TABLE_ORDER:
    create_table_file = path.join(
        'skill_schema',
        'tables',
        table + '.sql'
    )
    template_db.execute_sql(
        get_sql_from_file(create_table_file)
    )

print('Creating the geography schema tables')
for table in GEOGRAPHY_TABLE_ORDER:
    create_table_file = path.join(
        'geography_schema',
        'tables',
        table + '.sql'
    )
    template_db.execute_sql(
        get_sql_from_file(create_table_file)
    )

print('Creating the device schema tables')
for table in DEVICE_TABLE_ORDER:
    create_table_file = path.join(
        'device_schema',
        'tables',
        table + '.sql'
    )
    template_db.execute_sql(
        get_sql_from_file(create_table_file)
    )

print('Granting access to schemas and tables')
for schema in SCHEMAS:
    template_db.execute_sql(
        get_sql_from_file(schema + '_schema/grants.sql')
    )

template_db.close_db()

print('Copying template to new database.')
# postgres_db = PostgresDB(dbname='postgres', user='mycroft')
postgres_db = PostgresDB(
    dbname='defaultdb',
    user='doadmin',
    password='l06tn0qi2bjhgcki'
)
postgres_db.execute_sql(get_sql_from_file('create_mycroft_db.sql'))
postgres_db.close_db()

# mycroft_db = PostgresDB(dbname='mycroft', user='mycroft')
mycroft_db = PostgresDB(
    dbname='mycroft_template',
    user='selene',
    password='ubhemhx1dikmqc5f'
)
insert_files = [
    dict(schema_dir='account_schema', file_name='membership.sql'),
    dict(schema_dir='device_schema', file_name='text_to_speech.sql'),

]
for insert_file in insert_files:
    insert_file_path = path.join(
        insert_file['schema_dir'],
        'data',
        insert_file['file_name']
    )
    try:
        mycroft_db.execute_sql(
            get_sql_from_file(insert_file_path)
        )
    except FileNotFoundError:
        pass
