from http import HTTPStatus

import requests as service_request
from flask import current_app, Response
from flask_restful import Resource

THIRTY_DAYS = 2592000


class AuthorizeFacebookView(Resource):
    """
    Check the authenticity Facebook token obtained by the frontend
    """
    def __init__(self):
        self.frontend_response = None
        self.response_status_code = HTTPStatus.OK
        self.users_email = None
        self.users_name = None

    def get(self):
        return self._validate_token()


    def _validate_token(self):
        service_request_parameters = {'clientUri': current_app.config['SELENE_BASE_URL']}
        fb_service_response = service_request.get(
            current_app.config['TARTARUS_BASE_URL'] + '/social/auth/facebook',
            params=service_request_parameters
        )
        return Response(fb_service_response, mimetype='text/html')
