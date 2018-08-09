from http import HTTPStatus
import json

from flask import request, current_app
from flask_restful import Resource
import jwt
import requests

TARTARUS_USER_URL = 'https://api-test.mycroft.ai/v1/user/{user_uuid}'
UNDEFINED = 'Undefined'


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, current_app.config['SECRET_KEY'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'


class UserView(Resource):
    """
    User Login Resource
    """
    def __init__(self):
        self.service_response = None
        self.frontend_response = None

    def get(self):
        self._get_user_from_service()
        self._build_frontend_response()

        return self.frontend_response

    def _get_user_from_service(self):
        selene_token = request.cookies.get('seleneToken')
        user_uuid = decode_auth_token(selene_token)
        tartarus_token = request.cookies.get('tartarusToken')
        service_request_headers = {'Authorization': 'Bearer ' + tartarus_token}
        self.service_response = requests.get(
            TARTARUS_USER_URL.format(user_uuid=user_uuid),
            headers=service_request_headers
        )

    def _build_frontend_response(self):
        if self.service_response.status_code == HTTPStatus.OK:
            service_response_data = json.loads(self.service_response.content)
            frontend_response_data = dict(
                name=service_response_data.get('name')
            )
        else:
            frontend_response_data = {}
        self.frontend_response = (frontend_response_data, self.service_response.status_code)
