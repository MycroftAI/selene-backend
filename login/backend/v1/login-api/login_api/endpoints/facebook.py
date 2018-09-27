from http import HTTPStatus

from flask import current_app, redirect
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
        tartarus = current_app.config['TARTARUS_BASE_URL']
        selene = current_app.config['SELENE_BASE_URL']
        auth_endpoint = f'{tartarus}/social/auth/facebook?clientUri={selene}/api/auth/social&path=/social/login'
        return redirect(auth_endpoint)
