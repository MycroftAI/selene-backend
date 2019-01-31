from os import path

from selene.util.db.cursor import DatabaseQuery, fetch

SQL_DIR = path.join(path.dirname(__file__), 'sql')


def get_account_id_from_credentials(db, email: str, password: str) -> str:
    """
    Validate that the provided email/password combination exists on our database

    :param db: database connection object
    :param email: the user provided email address
    :param password: the user provided password
    :return: the uuid of the account
    """
    query = DatabaseQuery(
        file_path=path.join(SQL_DIR, 'get_account_id_from_credentials.sql'),
        args=dict(email_address=email, password=password),
        singleton=True
    )
    sql_results = fetch(db, query)

    return sql_results['id']
