"""Tools for executing sql within a transaction."""
from functools import wraps


def use_transaction(func):
    """Execute all sql statements within the wrapped function in a transaction

    This is a decorator that assumes the function it is wrapping is a method
    of a class with a "db" attribute that is a psycopg connection object.

    :param func: function being decorated
    :return: decorated function
    """
    @wraps(func)
    def execute_in_transaction(*args, **kwargs):
        instance = args[0]
        return_value = None
        if hasattr(instance, "db"):
            prev_autocommit = instance.db.autocommit
            instance.db.autocommit = False
            with instance.db:
                try:
                    return_value = func(*args, **kwargs)
                except:
                    instance.db.rollback()
                    raise
                else:
                    instance.db.commit()
            instance.db.autocommit = prev_autocommit

        return return_value

    return execute_in_transaction
