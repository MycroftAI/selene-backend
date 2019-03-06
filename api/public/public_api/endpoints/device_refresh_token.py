import hashlib
import json
import uuid
from http import HTTPStatus

from selene.api import PublicEndpoint


class DeviceRefreshTokenEndpoint(PublicEndpoint):

    ONE_DAY = 86400

    def __init__(self):
        super(DeviceRefreshTokenEndpoint, self).__init__()
        self.sha512 = hashlib.sha512()

    def get(self):
        refresh = self.request.headers['Authorization']
        if refresh.startswith('Bearer '):
            refresh = refresh[len('Bearer '):]
            session = self._refresh_session_token(refresh)
            if session:
                response = session, HTTPStatus.OK
            else:
                response = '', HTTPStatus.UNAUTHORIZED
        else:
            response = '', HTTPStatus.UNAUTHORIZED
        return response

    def _refresh_session_token(self, refresh: str):
        refresh_key = 'device.token.refresh:{}'.format(refresh)
        session = self.cache.get(refresh_key)
        if session:
            old_login = json.loads(session)
            device_id = old_login['uuid']
            self.cache.delete(refresh_key)
            self.sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
            access = self.sha512.hexdigest()
            self.sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
            refresh = self.sha512.hexdigest()
            login = dict(
                uuid=device_id,
                accessToken=access,
                refreshToken=refresh,
                expiration=self.ONE_DAY
            )
            new_login = json.dumps(login)
            # Storing device access token for one:
            self.cache.set_with_expiration(
                'device.token.access:{access}'.format(access=access),
                new_login,
                self.ONE_DAY
            )
            # Storing device refresh token for ever:
            self.cache.set('device.token.refresh:{refresh}'.format(refresh=refresh), new_login)
            return new_login
