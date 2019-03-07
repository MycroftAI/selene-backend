import hashlib
import json
import uuid

from flask import current_app, request
from flask.views import MethodView

from selene.util.auth import AuthenticationError
from ..util.cache import SeleneCache

ONE_DAY = 86400


def generate_device_login(device_id: str, cache: SeleneCache) -> dict:
    """Generates a login session for a given device id"""
    sha512 = hashlib.sha512()
    sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
    access = sha512.hexdigest()
    sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
    refresh = sha512.hexdigest()
    login = dict(
        uuid=device_id,
        accessToken=access,
        refreshToken=refresh,
        expiration=ONE_DAY
    )
    login_json = json.dumps(login)
    # Storing device access token for one:
    cache.set_with_expiration(
        'device.token.access:{access}'.format(access=access),
        login_json,
        ONE_DAY
    )
    # Storing device refresh token for ever:
    cache.set('device.token.refresh:{refresh}'.format(refresh=refresh), login_json)
    return login


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
