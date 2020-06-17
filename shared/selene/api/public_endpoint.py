# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import hashlib
import json
import uuid

from flask import current_app, request, Response, after_this_request
from flask import g as global_context
from flask.views import MethodView

from selene.api.etag import ETagManager
from selene.data.account import AccountRepository
from selene.data.metric import AccountActivityRepository
from selene.util.auth import AuthenticationError
from selene.util.db import connect_to_db
from selene.util.exceptions import NotModifiedException
from ..util.cache import SeleneCache

ONE_DAY = 86400


def track_account_activity(db, device_id: str):
    """Use the device ID to find the account, update active timestamp and metrics."""
    account_repository = AccountRepository(db)
    account = account_repository.get_account_by_device_id(device_id)
    account_repository.update_last_activity_ts(account.id)
    account_activity_repository = AccountActivityRepository(db)
    account_activity_repository.increment_activity(account)


def check_oauth_token():
    global_context.url = request.url
    exclude_paths = [
        "/v1/device/code",
        "/v1/device/activate",
        "/api/account",
        "/v1/auth/token",
        "/v1/auth/callback",
        "/v1/user/stripe/webhook",
    ]
    exclude = any(request.path.startswith(path) for path in exclude_paths)
    if not exclude:
        headers = request.headers
        if "Authorization" not in headers:
            raise AuthenticationError("Oauth token not found")
        token_header = headers["Authorization"]
        device_authenticated = False
        if token_header.startswith("Bearer "):
            token = token_header[len("Bearer ") :]
            session = current_app.config["SELENE_CACHE"].get(
                "device.token.access:{access}".format(access=token)
            )
            if session:
                device_authenticated = True
        if not device_authenticated:
            raise AuthenticationError("device not authorized")


def generate_device_login(device_id: str, cache: SeleneCache) -> dict:
    """Generates a login session for a given device id"""
    sha512 = hashlib.sha512()
    sha512.update(bytes(str(uuid.uuid4()), "utf-8"))
    access = sha512.hexdigest()
    sha512.update(bytes(str(uuid.uuid4()), "utf-8"))
    refresh = sha512.hexdigest()
    login = dict(
        uuid=device_id, accessToken=access, refreshToken=refresh, expiration=ONE_DAY
    )
    login_json = json.dumps(login)
    # Storing device access token for one:
    cache.set_with_expiration(
        "device.token.access:{access}".format(access=access), login_json, ONE_DAY
    )
    # Storing device refresh token for ever:
    cache.set("device.token.refresh:{refresh}".format(refresh=refresh), login_json)

    # Storing the login session by uuid (that allows us to delete session using the uuid)
    cache.set("device.session:{uuid}".format(uuid=device_id), login_json)
    return login


def delete_device_login(device_id: str, cache: SeleneCache):
    session = cache.get("device.session:{uuid}".format(uuid=device_id))
    if session is not None:
        session = json.loads(session)
        access_token = session["accessToken"]
        cache.delete("device.token.access:{access}".format(access=access_token))
        refresh_token = session["refreshToken"]
        cache.delete("device.refresh.token:{refresh}".format(refresh=refresh_token))
        cache.delete("device.session:{uuid}".format(uuid=device_id))


class PublicEndpoint(MethodView):
    """Abstract class for all endpoints used by Mycroft devices"""

    def __init__(self):
        global_context.url = request.url
        self.config: dict = current_app.config
        self.request = request
        self.cache: SeleneCache = self.config["SELENE_CACHE"]
        global_context.cache = self.cache
        self.etag_manager: ETagManager = ETagManager(self.cache, self.config)
        self.device_id = None

    @property
    def db(self):
        if "db" not in global_context:
            global_context.db = connect_to_db(
                current_app.config["DB_CONNECTION_CONFIG"]
            )

        return global_context.db

    def _authenticate(self, device_id: str = None):
        headers = self.request.headers
        if "Authorization" not in headers:
            raise AuthenticationError("Oauth token not found")
        token_header = self.request.headers["Authorization"]
        device_authenticated = False
        if token_header.startswith("Bearer "):
            token = token_header[len("Bearer ") :]
            session = self.cache.get(
                "device.token.access:{access}".format(access=token)
            )
            if session is not None:
                session = json.loads(session)
                device_uuid = session["uuid"]
                global_context.device_id = device_uuid
                self.device_id = device_uuid
                if device_id is not None:
                    device_authenticated = device_id == device_uuid
                else:
                    device_authenticated = True
        if not device_authenticated:
            raise AuthenticationError("device not authorized")

    def _add_etag(self, key):
        """Add a etag header to the response. We try to get the etag from the cache using the given key.
        If the cache has the etag, we use it, otherwise we generate a etag, store it and add it to the response"""
        etag = self.etag_manager.get(key)

        @after_this_request
        def set_etag_header(response: Response):
            response.headers["ETag"] = etag
            return response

    def _validate_etag(self, key):
        etag_from_request = self.request.headers.get("If-None-Match")
        if etag_from_request is not None:
            etag_from_cache = self.cache.get(key)
            not_modified = (
                etag_from_cache is not None
                and etag_from_request == etag_from_cache.decode("utf-8")
            )
            if not_modified:
                raise NotModifiedException()
