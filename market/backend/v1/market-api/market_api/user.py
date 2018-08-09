from http import HTTPStatus
import json

from flask import request, current_app
from flask_restful import Resource
import requests

from util.jwt import decode_auth_token


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
        user_uuid = decode_auth_token(selene_token, current_app.config['SECRET_KEY'])
        tartarus_token = request.cookies.get('tartarusToken')
        service_request_headers = {'Authorization': 'Bearer ' + tartarus_token}
        service_url = current_app.config['TARTARUS_BASE_URL'] + '/user/' + user_uuid
        self.service_response = requests.get(service_url, headers=service_request_headers)

    def _build_frontend_response(self):
        if self.service_response.status_code == HTTPStatus.OK:
            service_response_data = json.loads(self.service_response.content)
            frontend_response_data = dict(
                name=service_response_data.get('name')
            )
        else:
            frontend_response_data = {}
        self.frontend_response = (frontend_response_data, self.service_response.status_code)
