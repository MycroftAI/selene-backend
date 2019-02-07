from os import path
from typing import List

from selene.device.entity.device import Device
from selene.util.db import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


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
    sql_results = fetch(db, query)
    return Device(**sql_results)


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


def get_subscription_type_by_device_id(db, device_id):
    """Return the type of subscription of device's owner
    :param db: psycopg2 connection to mycroft database
    :param device_id: device uuid
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_subscription_type_by_device_id.sql'),
        args=dict(device_id=device_id),
        singleton=True
    )
    sql_result = fetch(db, query)
    if sql_result:
        return {'@type': sql_result['rate_period']}
    else:
        return {'@type': 'free'}
