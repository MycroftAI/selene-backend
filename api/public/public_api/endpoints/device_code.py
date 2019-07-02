import hashlib
import json
import random
import uuid
from http import HTTPStatus

from selene.api import PublicEndpoint
from selene.util.cache import DEVICE_PAIRING_CODE_KEY

ONE_DAY = 86400


class DeviceCodeEndpoint(PublicEndpoint):
    """Endpoint to get a pairing code"""

    # We need to do that to avoid ambiguous characters, like 0 and O, that
    # is even harder to distinguish in the display of the mark 1
    allowed_characters = "ACEFHJKLMNPRTUVWXY3479"

    def __init__(self):
        super(DeviceCodeEndpoint, self).__init__()

    def get(self):
        """Return a pairing code to the requesting device.

        The pairing process happens in two steps.  First step generates
        pairing code.  Second step uses the pairing code to activate the device.
        The state parameter is used to make sure that the device that is
        """
        response_data = self._build_response()
        return response_data, HTTPStatus.OK

    def _build_response(self):
        """
        Build the response data to return to the device.

        The pairing code generated may already exist for another device. So,
        continue to generate pairing codes until one that does not already
        exist is created.
        """
        response_data = dict(
            state=self.request.args['state'],
            token=self._generate_token(),
            expiration=ONE_DAY
        )
        pairing_code_added = False
        while not pairing_code_added:
            pairing_code = self._generate_pairing_code()
            response_data.update(code=pairing_code)
            pairing_code_added = self.cache.set_if_not_exists_with_expiration(
                DEVICE_PAIRING_CODE_KEY.format(pairing_code=pairing_code),
                value=json.dumps(response_data),
                expiration=ONE_DAY
            )

        return response_data

    @staticmethod
    def _generate_token():
        sha512 = hashlib.sha512()
        sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
        return sha512.hexdigest()

    def _generate_pairing_code(self):
        return ''.join(random.choice(self.allowed_characters) for _ in range(6))
