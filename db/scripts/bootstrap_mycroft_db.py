# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

from datetime import date
from glob import glob
from io import BytesIO
from os import environ, path, remove
from tempfile import TemporaryDirectory
from urllib import request
from zipfile import ZipFile

from markdown import markdown
from psycopg2 import connect
from psycopg2.extras import DateRange

MYCROFT_DB_DIR = environ.get("DB_DIR", "/opt/selene/selene-backend/db/mycroft")
MYCROFT_DB_NAME = environ.get("DB_NAME", "mycroft")
SCHEMAS = ("account", "skill", "device", "geography", "metric", "tagging", "wake_word")
DB_DESTROY_FILES = ("drop_mycroft_db.sql", "drop_template_db.sql", "drop_roles.sql")
DB_CREATE_FILES = (
    "create_roles.sql",
    "create_template_db.sql",
)
ACCOUNT_TABLE_ORDER = (
    "account",
    "agreement",
    "account_agreement",
    "membership",
    "account_membership",
)
SKILL_TABLE_ORDER = (
    "skill",
    "settings_display",
    "display",
    "oauth_credential",
    "oauth_token",
)
DEVICE_TABLE_ORDER = (
    "category",
    "geography",
    "text_to_speech",
    "account_preferences",
    "account_defaults",
    "device",
    "device_skill",
)
GEOGRAPHY_TABLE_ORDER = ("country", "timezone", "region", "city")
METRIC_TABLE_ORDER = ("api", "api_history", "job", "core", "account_activity")
TAGGING_TABLE_ORDER = ("file_location", "file", "wake_word_file")
WAKE_WORD_TABLE_ORDER = ("wake_word", "pocketsphinx_settings")

schema_directory = "{}_schema"


def get_sql_from_file(file_path: str) -> str:
    with open(path.join(MYCROFT_DB_DIR, file_path)) as sql_file:
        sql = sql_file.read()

    return sql


class PostgresDB(object):
    def __init__(self, db_name, user=None):
        db_host = environ.get("DB_HOST", "127.0.0.1")
        db_port = environ.get("DB_PORT", 5432)
        db_ssl_mode = environ.get("DB_SSLMODE")
        if db_name in ("postgres", "defaultdb", "mycroft_template"):
            db_user = environ.get("POSTGRES_USER", "postgres")
            db_password = environ.get("POSTGRES_PASSWORD")
        else:
            db_user = environ.get("DB_USER", "selene")
            db_password = environ["DB_PASSWORD"]

        if user is not None:
            db_user = user

        self.db = connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
            sslmode=db_ssl_mode,
        )
        self.db.autocommit = True

    def close_db(self):
        self.db.close()

    def execute_sql(self, sql: str, args=None):
        _cursor = self.db.cursor()
        _cursor.execute(sql, args)
        return _cursor


def destroy_existing(db):
    print("Destroying any objects we will be creating later.")
    for db_destroy_file in DB_DESTROY_FILES:
        db.execute_sql(get_sql_from_file(db_destroy_file))

def create_anew(db):
    print("Creating the mycroft database")
    for db_setup_file in DB_CREATE_FILES:
        db.execute_sql(get_sql_from_file(db_setup_file))


def _init_db():
    postgres_db = PostgresDB(db_name="postgres")
    destroy_existing(postgres_db)
    create_anew(postgres_db)
    postgres_db.close_db()


def _setup_template_db(db):
    print("Creating the extensions")
    db.execute_sql(get_sql_from_file(path.join("create_extensions.sql")))
    print("Creating user-defined data types")
    type_directory = path.join(MYCROFT_DB_DIR, "types")
    for type_file in glob(type_directory + "/*.sql"):
        db.execute_sql(get_sql_from_file(path.join(type_directory, type_file)))
    print("Create the schemas and grant access")
    for schema in SCHEMAS:
        db.execute_sql(get_sql_from_file(schema + "_schema/create_schema.sql"))


def _build_schema_tables(db, schema, tables):
    print(f"Creating the {schema} schema tables")
    for table in tables:
        create_table_file = path.join(schema + "_schema", "tables", table + ".sql")
        db.execute_sql(get_sql_from_file(create_table_file))


def _grant_access(db):
    print("Granting access to schemas and tables")
    for schema in SCHEMAS:
        db.execute_sql(get_sql_from_file(schema + "_schema/grants.sql"))


def _build_template_db():
    template_db = PostgresDB(db_name="mycroft_template")
    _setup_template_db(template_db)
    _build_schema_tables(template_db, "account", ACCOUNT_TABLE_ORDER)
    _build_schema_tables(template_db, "skill", SKILL_TABLE_ORDER)
    _build_schema_tables(template_db, "geography", GEOGRAPHY_TABLE_ORDER)
    _build_schema_tables(template_db, "wake_word", WAKE_WORD_TABLE_ORDER)
    _build_schema_tables(template_db, "device", DEVICE_TABLE_ORDER)
    _build_schema_tables(template_db, "tagging", TAGGING_TABLE_ORDER)
    _build_schema_tables(template_db, "metric", METRIC_TABLE_ORDER)
    _grant_access(template_db)
    template_db.close_db()


def _create_mycroft_db_from_template():
    print("Copying template to new database.")
    db = PostgresDB(db_name="postgres")
    db.execute_sql(get_sql_from_file("create_mycroft_db.sql"))
    db.close_db()


def _apply_insert_file(db, schema_dir, file_name):
    insert_file_path = path.join(schema_dir, "data", file_name)
    try:
        db.execute_sql(get_sql_from_file(insert_file_path))
    except FileNotFoundError:
        pass


def _populate_agreement_table(db):
    print("Populating account.agreement table")
    db.db.autocommit = False
    insert_sql = "insert into account.agreement VALUES (default, %s, '1', %s, %s)"
    privacy_policy_path = path.join(
        environ.get("MYCROFT_DOC_DIR", "/opt/mycroft/devops/agreements"),
        "privacy_policy.md",
    )
    terms_of_use_path = path.join(
        environ.get("MYCROFT_DOC_DIR", "/opt/mycroft/devops/agreements"),
        "terms_of_use.md",
    )
    docs = {"Privacy Policy": privacy_policy_path, "Terms of Use": terms_of_use_path}
    agreement_date_range = DateRange(lower=date(2000, 1, 1), bounds="[]")
    for agreement_type, doc_path in docs.items():
        try:
            lobj = db.db.lobject(0, "b")
            with open(doc_path) as doc:
                doc_html = markdown(doc.read(), output_format="html5")
                lobj.write(doc_html)
            db.execute_sql(
                insert_sql, args=(agreement_type, agreement_date_range, lobj.oid)
            )
            db.execute_sql(f"grant select on large object {lobj.oid} to selene")
        except FileNotFoundError:
            print(
                f"WARNING: File {doc_path} was not found. "
                f"The {agreement_type} agreement was not added."
            )
            db.db.rollback()
        except:
            db.db.rollback()
            raise
        else:
            db.db.commit()

    db.db.autocommit = True
    db.execute_sql(insert_sql, args=("Open Dataset", agreement_date_range, None))


def _populate_country_table(db):
    print("Populating geography.country table")
    country_insert = """
    INSERT INTO
        geography.country (iso_code, name)
    VALUES
        ('{iso_code}', '{country_name}')
    """
    country_url = "http://download.geonames.org/export/dump/countryInfo.txt"
    with request.urlopen(country_url) as country_file:
        for rec in country_file.readlines():
            if rec.startswith(b"#"):
                continue
            country_fields = rec.decode().split("\t")
            insert_args = dict(
                iso_code=country_fields[0], country_name=country_fields[4]
            )
            db.execute_sql(country_insert.format(**insert_args))


def _populate_region_table(db):
    print("Populating geography.region table")
    region_insert = """
    INSERT INTO
        geography.region (country_id, region_code, name)
    VALUES
        (
            (SELECT id FROM geography.country WHERE iso_code = %(iso_code)s),
            %(region_code)s,
            %(region_name)s
        )
    """
    region_url = "http://download.geonames.org/export/dump/admin1CodesASCII.txt"
    with request.urlopen(region_url) as region_file:
        for region in region_file.readlines():
            region_fields = region.decode().split("\t")
            country_iso_code = region_fields[0][:2]
            insert_args = dict(
                iso_code=country_iso_code,
                region_code=region_fields[0],
                region_name=region_fields[1],
            )
            db.execute_sql(region_insert, insert_args)


def _populate_timezone_table(db):
    print("Populating geography.timezone table")
    timezone_insert = """
    INSERT INTO
        geography.timezone (country_id, name, gmt_offset, dst_offset)
    VALUES
        (
            (SELECT id FROM geography.country WHERE iso_code = %(iso_code)s),
            %(timezone_name)s,
            %(gmt_offset)s,
            %(dst_offset)s
        )
    """
    timezone_url = "http://download.geonames.org/export/dump/timeZones.txt"
    with request.urlopen(timezone_url) as timezone_file:
        timezone_file.readline()
        for timezone in timezone_file.readlines():
            timezone_fields = timezone.decode().split("\t")
            insert_args = dict(
                iso_code=timezone_fields[0],
                timezone_name=timezone_fields[1],
                gmt_offset=timezone_fields[2],
                dst_offset=timezone_fields[3],
            )
            db.execute_sql(timezone_insert, insert_args)


def _populate_city_table(db):
    print("Populating geography.city table")
    region_query = "SELECT id, region_code FROM geography.region"
    query_result = db.execute_sql(region_query)
    region_lookup = dict()
    for row in query_result.fetchall():
        region_lookup[row[1]] = row[0]

    timezone_query = "SELECT id, name FROM geography.timezone"
    query_result = db.execute_sql(timezone_query)
    timezone_lookup = dict()
    for row in query_result.fetchall():
        timezone_lookup[row[1]] = row[0]
    cities_download = request.urlopen(
        "http://download.geonames.org/export/dump/cities500.zip"
    )

    temp_dir = TemporaryDirectory()
    dump_file_path = path.join(temp_dir.name, "city.dump")

    with ZipFile(BytesIO(cities_download.read())) as cities_zip:
        with cities_zip.open("cities500.txt") as cities:
            with open(dump_file_path, "w") as dump_file:
                for city in cities.readlines():
                    city_fields = city.decode().split("\t")
                    city_region = city_fields[8] + "." + city_fields[10]
                    region_id = region_lookup.get(city_region)
                    timezone_id = timezone_lookup[city_fields[17]]
                    if region_id is not None:
                        dump_file.write(
                            "\t".join(
                                [
                                    region_id,
                                    timezone_id,
                                    city_fields[1],
                                    city_fields[4],
                                    city_fields[5],
                                    city_fields[14],
                                ]
                            )
                            + "\n"
                        )
    with open(dump_file_path) as dump_file:
        cursor = db.db.cursor()
        cursor.copy_from(
            dump_file,
            "geography.city",
            columns=(
                "region_id",
                "timezone_id",
                "name",
                "latitude",
                "longitude",
                "population",
            ),
        )
    remove(dump_file_path)
    temp_dir.cleanup()


def _populate_db():
    mycroft_db = PostgresDB(db_name=MYCROFT_DB_NAME)
    _apply_insert_file(
        mycroft_db, schema_dir="account_schema", file_name="membership.sql"
    )
    _apply_insert_file(
        mycroft_db, schema_dir="device_schema", file_name="text_to_speech.sql"
    )
    _populate_agreement_table(mycroft_db)
    _populate_country_table(mycroft_db)
    _populate_region_table(mycroft_db)
    _populate_timezone_table(mycroft_db)
    _populate_city_table(mycroft_db)
    mycroft_db.close_db()


if __name__ == "__main__":
    _init_db()
    _build_template_db()
    _create_mycroft_db_from_template()
    _populate_db()
