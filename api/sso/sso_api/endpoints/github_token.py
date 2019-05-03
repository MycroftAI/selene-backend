from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.util.auth import get_github_authentication_token


class GithubTokenEndpoint(SeleneEndpoint):
    def get(self):
        token = get_github_authentication_token(
            self.request.args['code'],
            self.request.args['state']
        )

        return dict(token=token), HTTPStatus.OK
