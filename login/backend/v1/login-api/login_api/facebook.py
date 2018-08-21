# from http import HTTPStatus
# import json
# from time import time
#
# from flask import current_app, request as frontend_request
# from flask_restful import Resource
# import requests as service_request
#
# FACEBOOK_API_URL = 'https://graph.facebook.com/v3.1/me/?fields=name,email'
# THIRTY_DAYS = 2592000
#
#
# class AuthorizeFacebookView(Resource):
#     """
#     Check the authenticity Facebook token obtained by the frontend
#     """
#     def __init__(self):
#         self.frontend_response = None
#         self.response_status_code = HTTPStatus.OK
#         self.users_email = None
#         self.users_name = None
#
#     def get(self):
#         self._validate_token()
#         self._build_frontend_response()
#
#         return self.frontend_response
#
#     def _validate_token(self):
#         facebook_token = frontend_request.headers['token']
#         service_request_headers = {'Authorization': 'Bearer ' + facebook_token}
#         fb_service_response = service_request.get(
#             FACEBOOK_API_URL,
#             headers=service_request_headers
#         )
#         if fb_service_response.status_code == HTTPStatus.OK:
#             fb_service_response_content = json.loads(fb_service_response.content)
#             self.users_name = fb_service_response_content['name']
#             self.users_email = fb_service_response_content['email']
#         else:
#             self.response_status_code = fb_service_response.status_code
#
#     def _build_frontend_response(self):
#         if self.response_status_code == HTTPStatus.OK:
#             frontend_response_data = dict(
#                 expiration=time() + THIRTY_DAYS,
#                 seleneToken=encode_selene_token(self.users_uuid),
#                 tartarusToken=self.tartarus_token,
#             )
#         else:
#             frontend_response_data = {}
#         self.frontend_response = (frontend_response_data, self.response_status_code)
