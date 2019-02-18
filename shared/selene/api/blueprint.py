from http import HTTPStatus

from flask import Blueprint
from schematics.exceptions import DataError

selene_api = Blueprint('selene_api', __name__)


@selene_api.app_errorhandler(DataError)
def handle_data_error(error):
    return str(error.messages), HTTPStatus.BAD_REQUEST
