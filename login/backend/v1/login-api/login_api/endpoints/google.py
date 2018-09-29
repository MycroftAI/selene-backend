from flask import current_app, redirect
from selene_util.api import SeleneEndpoint


class AuthorizeGoogleEndpoint(SeleneEndpoint):

    def get(self):
        return self._validate_token()

    def _validate_token(self):
        tartarus = current_app.config['TARTARUS_BASE_URL']
        selene = current_app.config['SELENE_BASE_URL']
        auth_endpoint = f'{tartarus}/social/auth/google?clientUri={selene}/api/social&path=/social/login'
        return redirect(auth_endpoint)