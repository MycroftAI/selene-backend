"""Database access utility functions"""
from os import environ
from mongoengine import connect


def connect_to_skill_db():
    """Establish a connection to the Mongo skills database."""
    host = environ['SKILL_DB_HOST']
    port = int(environ['SKILL_DB_PORT'])
    database = 'skillDB'
    connect(database, host=host, port=port)
