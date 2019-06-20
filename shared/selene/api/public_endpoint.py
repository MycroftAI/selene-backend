import hashlib
import json
import uuid

from flask import (
    current_app,
    request,
    Response,
    after_this_request
)
from flask import g as global_context
from flask.views import MethodView

from selene.api.etag import ETagManager
from selene.util.auth import AuthenticationError
from selene.util.db import connect_to_db
from selene.util.exceptions import NotModifiedException
from ..util.cache import SeleneCache

ONE_DAY = 86400


def check_oauth_token():
    global_context.url = request.url
    exclude_paths = ['/v1/device/code', '/v1/device/activate', '/api/account', '/v1/auth/token', '/v1/auth/callback']
    exclude = any(request.path.startswith(path) for path in exclude_paths)
    if not exclude:
        headers = request.headers
        if 'Authorization' not in headers:
            raise AuthenticationError('Oauth token not found')
        token_header = headers['Authorization']
        device_authenticated = False
        if token_header.startswith('Bearer '):
            token = token_header[len('Bearer '):]
            session = current_app.config['SELENE_CACHE'].get('device.token.access:{access}'.format(access=token))
            if session:
                device_authenticated = True
        if not device_authenticated:
            raise AuthenticationError('device not authorized')


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

    # Storing the login session by uuid (that allows us to delete session using the uuid)
    cache.set('device.session:{uuid}'.format(uuid=device_id), login_json)
    return login


def delete_device_login(device_id: str, cache: SeleneCache):
    session = cache.get('device.session:{uuid}'.format(uuid=device_id))
    if session is not None:
        session = json.loads(session)
        access_token = session['accessToken']
        cache.delete('device.token.access:{access}'.format(access=access_token))
        refresh_token = session['refreshToken']
        cache.delete('device.refresh.token:{refresh}'.format(refresh=refresh_token))
        cache.delete('device.session:{uuid}'.format(uuid=device_id))


class PublicEndpoint(MethodView):
    """Abstract class for all endpoints used by Mycroft devices"""

    def __init__(self):
        self.config: dict = current_app.config
        self.request = request
        global_context.url = request.url
        self.cache: SeleneCache = self.config['SELENE_CACHE']
        global_context.cache = self.cache
        self.etag_manager: ETagManager = ETagManager(self.cache, self.config)

    @property
    def db(self):
        if 'db' not in global_context:
            global_context.db = connect_to_db(
                current_app.config['DB_CONNECTION_CONFIG']
            )

        return global_context.db

    def _authenticate(self, device_id: str = None):
        headers = self.request.headers
        if 'Authorization' not in headers:
            raise AuthenticationError('Oauth token not found')
        token_header = self.request.headers['Authorization']
        device_authenticated = False
        if token_header.startswith('Bearer '):
            token = token_header[len('Bearer '):]
            session = self.cache.get('device.token.access:{access}'.format(access=token))
            if session is not None:
                session = json.loads(session)
                device_uuid = session['uuid']
                global_context.device_id = device_uuid
                if device_id is not None:
                    device_authenticated = (device_id == device_uuid)
                else:
                    device_authenticated = True
        if not device_authenticated:
            raise AuthenticationError('device not authorized')

    def _add_etag(self, key):
        """Add a etag header to the response. We try to get the etag from the cache using the given key.
        If the cache has the etag, we use it, otherwise we generate a etag, store it and add it to the response"""
        etag = self.etag_manager.get(key)

        @after_this_request
        def set_etag_header(response: Response):
            response.headers['ETag'] = etag
            return response

    def _validate_etag(self, key):
        etag_from_request = self.request.headers.get('If-None-Match')
        if etag_from_request is not None:
            etag_from_cache = self.cache.get(key)
            not_modified = (
                    etag_from_cache is not None and
                    etag_from_request == etag_from_cache.decode('utf-8')
            )
            if not_modified:
                raise NotModifiedException()
