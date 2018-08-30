"""Database access utility functions"""
from os import environ
from mongoengine import connect


def connect_to_skill_db():
    """Establish a connection to the Mongo skills database."""
    host = environ['SELENE_SKILL_SERVICE_HOST']
    port = int(environ['SELENE_SKILL_SERVICE_PORT_SKILL_DB'])
    database = 'skillDB'
    connect(database, host=host, port=port)
