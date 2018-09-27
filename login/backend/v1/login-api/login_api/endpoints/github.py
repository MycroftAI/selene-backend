from flask import current_app, redirect
from flask_restful import Resource


class AuthorizeGithubView(Resource):

    def get(self):
        return self._validate_token()

    def _validate_token(self):
        tartarus = current_app.config['TARTARUS_BASE_URL']
        selene = current_app.config['SELENE_BASE_URL']
        auth_endpoint = f'{tartarus}/social/auth/github?clientUri={selene}/api/auth/social&path=/social/login'
        return redirect(auth_endpoint)