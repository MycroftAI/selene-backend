from datetime import datetime
from http import HTTPStatus
import json
from time import time

from flask import current_app, request as frontend_request
from flask_restful import Resource
import jwt
import requests as service_request

THIRTY_DAYS = 2592000


def encode_selene_token(user_uuid):
    """
    Generates the Auth Token
    :return: string
    """
    token_expiration = time() + THIRTY_DAYS
    payload = dict(iat=datetime.utcnow(), exp=token_expiration, sub=user_uuid)
    selene_token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    # before returning the token, convert it from bytes to string so that
    # it can be included in a JSON response object
    return selene_token.decode()


class AuthorizeAntisocialView(Resource):
    """
    User Login Resource
    """
    def __init__(self):
        self.frontend_response = None
        self.response_status_code = HTTPStatus.OK
        self.tartarus_token = None
        self.users_uuid = None

    def get(self):
        self._authorize()
        self._build_frontend_response()

        return self.frontend_response

    def _authorize(self):
        basic_credentials = frontend_request.headers['authorization']
        service_request_headers = {'Authorization': basic_credentials}
        auth_service_response = service_request.get(
            current_app.config['TARTARUS_BASE_URL'] + '/auth/login',
            headers=service_request_headers
        )
        if auth_service_response.status_code == HTTPStatus.OK:
            auth_service_response_content = json.loads(
                auth_service_response.content
            )
            self.users_uuid = auth_service_response_content['uuid']
            self.tartarus_token = auth_service_response_content['accessToken']
        else:
            self.response_status_code = auth_service_response.status_code

    def _build_frontend_response(self):
        if self.response_status_code == HTTPStatus.OK:
            frontend_response_data = dict(
                expiration=time() + THIRTY_DAYS,
                seleneToken=encode_selene_token(self.users_uuid),
                tartarusToken=self.tartarus_token,
            )
        else:
            frontend_response_data = {}
        self.frontend_response = (
            frontend_response_data,
            self.response_status_code
        )
