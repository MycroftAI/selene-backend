from http import HTTPStatus

from flask import Blueprint
from schematics.exceptions import DataError

from selene.util.auth import AuthenticationError

selene_api = Blueprint('selene_api', __name__)


@selene_api.app_errorhandler(DataError)
def handle_data_error(error):
    return str(error.messages), HTTPStatus.BAD_REQUEST


@selene_api.app_errorhandler(AuthenticationError)
def handle_data_error(error):
    return dict(error=str(error)), HTTPStatus.UNAUTHORIZED
