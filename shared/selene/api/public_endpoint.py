import json

from flask import current_app, request
from flask.views import MethodView

from selene.util.auth import AuthenticationError
from ..util.cache import SeleneCache


class PublicEndpoint(MethodView):
    """Abstract class for all endpoints used by Mycroft devices"""

    def __init__(self):
        self.config: dict = current_app.config
        self.request = request
        self.cache: SeleneCache = self.config['SELENE_CACHE']

    def _authenticate(self, device_id: str = None):
        headers = self.request.headers
        if 'Authorization' not in headers:
            raise AuthenticationError('Oauth token not found')
        token_header = self.request.headers['Authorization']
        device_authenticated = True
        if token_header.startswith('Bearer '):
            token = token_header[len('Bearer '):]
            session = self.cache.get('device.token.access:{access}'.format(access=token))
            if session is not None:
                if device_id is not None:
                    session = json.loads(session)
                    uuid = session['uuid']
                    device_authenticated = (device_id == uuid)
                else:
                    device_authenticated = True
        if not device_authenticated:
            raise AuthenticationError('device not authorized')
