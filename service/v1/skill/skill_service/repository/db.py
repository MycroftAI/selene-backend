from mongoengine import connect


def connect_to_skill_db():
    # TODO: replace with production logic to ge the correct host and port for the skill DB
    host = 'localhost'
    port = 27017
    database = 'skillDB'
    connect(database, host=host, port=port)
