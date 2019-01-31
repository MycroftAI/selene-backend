"""Endpoint for single sign on through Google"""
from flask import redirect

from selene.api import SeleneEndpoint


class AuthorizeGoogleEndpoint(SeleneEndpoint):

    def get(self):
        """Call a Tartarus endpoint that will redirect to Google login."""
        tartarus_auth_endpoint = (
            '{tartarus_url}/social/auth/google'
            '?clientUri={login_url}&path=/social/login'.format(
                login_url=self.config['SSO_BASE_URL'],
                tartarus_url=self.config['TARTARUS_BASE_URL']
            )
        )
        return redirect(tartarus_auth_endpoint)
