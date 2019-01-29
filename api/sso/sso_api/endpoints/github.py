"""Endpoint for single sign on through Github"""
from flask import redirect

from selene.util.api import SeleneEndpoint


class AuthorizeGithubEndpoint(SeleneEndpoint):

    def get(self):
        """Call a Tartarus endpoint that will redirect to Github login."""
        tartarus_auth_endpoint = (
            '{tartarus_url}/social/auth/github'
            '?clientUri={login_url}&path=/social/login'.format(
                tartarus_url=self.config['TARTARUS_BASE_URL'],
                login_url=self.config['SSO_BASE_URL']
            )
        )
        return redirect(tartarus_auth_endpoint)
