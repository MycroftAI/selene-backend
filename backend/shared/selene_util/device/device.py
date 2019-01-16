from dataclasses import dataclass
from datetime import datetime
from os import path
from typing import List

from selene_util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


@dataclass
class Device(object):
    """Representation of a Device"""
    id: str
    account_id: str
    name: str
    platform: str
    enclosure_version: str
    core_version: str
    wake_word_id: str
    text_to_speech_id: str
    category_id: str = None
    location_id: str = None
    placement: str = None
    last_contact_ts: datetime = None


def get_device_by_id(db, device_id: str) -> Device:
    """Fetch a device using a given device id

    :param db: psycopg2 connection to mycroft database
    :param device_id: uuid
    :return: Device entity
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_device_by_id.sql'),
        args=dict(device_id=device_id),
        singleton=True
    )
    sql_result = fetch(db, query)
    return Device(**sql_result)


def get_devices_by_account_id(db, account_id: str) -> List[Device]:
    """Fetch all devices associated to a user from a given account id

    :param db: psycopg2 connection to mycroft database
    :param account_id: uuid
    :return: List of User's devices
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_devices_by_account_id.sql'),
        args=dict(account_id=account_id),
        singleton=False
    )
    sql_results = fetch(db, query)
    return [Device(**result) for result in sql_results]
