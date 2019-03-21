from http import HTTPStatus

from flask import Blueprint
from schematics.exceptions import DataError

from selene.util.auth import AuthenticationError
from selene.util.not_modified import NotModifiedError

selene_api = Blueprint('selene_api', __name__)


@selene_api.app_errorhandler(DataError)
def handle_data_error(error):
    return error.to_primitive(), HTTPStatus.BAD_REQUEST


@selene_api.app_errorhandler(AuthenticationError)
def handle_data_error(error):
    return dict(error=str(error)), HTTPStatus.UNAUTHORIZED


@selene_api.app_errorhandler(NotModifiedError)
def handle_not_modified(error):
    return '', HTTPStatus.NOT_MODIFIED
