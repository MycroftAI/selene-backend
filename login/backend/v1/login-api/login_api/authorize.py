from datetime import datetime
from http import HTTPStatus
import json
from time import time

from flask import current_app, request as frontend_request
from flask_restful import Resource
import jwt
import requests as service_request

TARTARUS_LOGIN_URL = 'https://api-test.mycroft.ai/v1/auth/login'
THIRTY_DAYS = 2592000


def encode_selene_token(user_uuid):
    """
    Generates the Auth Token
    :return: string
    """
    payload = dict(iat=datetime.utcnow(), iss="Selene", sub=user_uuid)
    selene_token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

    return selene_token.decode()


class AuthorizeView(Resource):
    """
    User Login Resource
    """
    def __init__(self):
        self.service_response = None
        self.frontend_response = None

    def get(self):
        self._authorize()
        self._build_frontend_response()

        return self.frontend_response

    def _authorize(self):
        basic_credentials = frontend_request.headers['authorization']
        service_request_headers = {'Authorization': basic_credentials}
        self.service_response = service_request.get(
            TARTARUS_LOGIN_URL,
            headers=service_request_headers
        )

    def _build_frontend_response(self):
        if self.service_response.status_code == HTTPStatus.OK:
            service_response_data = json.loads(self.service_response.content)
            frontend_response_data = dict(
                seleneToken=encode_selene_token(service_response_data.get('uuid')),
                expiration=time() + THIRTY_DAYS,
                tartarusToken=service_response_data.get('accessToken')
            )
        else:
            frontend_response_data = {}
        self.frontend_response = (frontend_response_data, self.service_response.status_code)



#
#     def post(self):
#         # get the post data
#         post_data = frontend_request.get_json()
#         try:
#             # fetch the user data
#             user = User.query.filter_by(
#                 email=post_data.get('email')
#             ).first()
#             if user and bcrypt.check_password_hash(
#                 user.password, post_data.get('password')
#             ):
#                 auth_token = user.encode_auth_token(user.id)
#                 if auth_token:
#                     responseObject = {
#                         'status': 'success',
#                         'message': 'Successfully logged in.',
#                         'auth_token': auth_token.decode()
#                     }
#                     return make_response(jsonify(responseObject)), 200
#             else:
#                 responseObject = {
#                     'status': 'fail',
#                     'message': 'User does not exist.'
#                 }
#                 return make_response(jsonify(responseObject)), 404
#         except Exception as e:
#             print(e)
#             responseObject = {
#                 'status': 'fail',
#                 'message': 'Try again'
#             }
#             return make_response(jsonify(responseObject)), 500
#
#
# def decode_auth_token(auth_token):
#     """
#     Decodes the auth token
#     :param auth_token:
#     :return: integer|string
#     """
#     try:
#         payload = jwt.decode(auth_token, login.config['SECRET_KEY'])
#         return payload['sub']
#     except jwt.ExpiredSignatureError:
#         return 'Signature expired. Please log in again.'
#     except jwt.InvalidTokenError:
#         return 'Invalid token. Please log in again.'
