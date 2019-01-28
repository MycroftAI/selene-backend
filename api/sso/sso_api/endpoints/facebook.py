"""Endpoint for single sign on through Facebook"""
from flask import redirect

from selene_util.api import SeleneEndpoint


class AuthorizeFacebookEndpoint(SeleneEndpoint):
    def get(self):
        """Call a Tartarus endpoint that will redirect to Facebook login."""
        tartarus_auth_endpoint = (
            '{tartarus_url}/social/auth/facebook'
            '?clientUri={login_url}&path=/social/login'.format(
                tartarus_url=self.config['TARTARUS_BASE_URL'],
                login_url=self.config['SSO_BASE_URL']
            )
        )
        return redirect(tartarus_auth_endpoint)
