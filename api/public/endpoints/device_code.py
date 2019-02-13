import json
import hashlib
import random
import uuid

from selene.api import SeleneEndpoint
from selene.util.selene_cache import SeleneCache


class DeviceCodeEndpoint(SeleneEndpoint):
    """Endpoint to get a pairing code"""

    # We need to do that to avoid ambiguous characters, like 0 and O, that is even harder to distinguish
    # in the display of the mark 1
    ALLOWED_CHARACTERS = "ACEFHJKLMNPRTUVWXY3479"

    def __init__(self):
        super(DeviceCodeEndpoint, self).__init__()
        self.device_pairing_time = 86400
        self.cache: SeleneCache = self.config.get('SELENE_CACHE')
        self.sha512 = hashlib.sha512()

    def get(self):
        # The pairing process happens in two steps, the step where we get the pairing code and
        # the step to activate the device. The state parameter is used to make sure that the device that is
        # trying to be activate is the device which started the previous step
        state = self.request.args['state']
        return self._create(state)

    def _create(self, state):
        self.sha512.update(bytes(str(uuid.uuid4()), 'utf-8'))
        token = self.sha512.hexdigest()
        code = self._pairing_code()
        pairing = json.dumps({'code': code,
                              'state': state,
                              'token': token,
                              'expiration': self.device_pairing_time})
        # This is to deal with the case where we generate a pairing code that already exists in the
        # cache, meaning another device is trying to pairing using the same code. In this case, we should
        # call the method again to get another random pairing code
        if self.cache.set_if_not_exists_with_expiration(self._code_key(code),
                                                        value=pairing,
                                                        expiration=self.device_pairing_time):
            return code
        else:
            return self._create(state)

    @staticmethod
    def _code_key(code):
        return 'pairing.code:{}'.format(code)

    def _pairing_code(self):
        return ''.join(random.choice(self.ALLOWED_CHARACTERS) for _ in range(6))
