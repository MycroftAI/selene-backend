from http import HTTPStatus

from selene.api import SeleneEndpoint


class PairingCodeEndpoint(SeleneEndpoint):
    def __init__(self):
        super(PairingCodeEndpoint, self).__init__()
        self.cache = self.config['SELENE_CACHE']

    def get(self, pairing_code):
        self._authenticate()
        pairing_code_is_valid = self._get_pairing_data(pairing_code)

        return dict(isValid=pairing_code_is_valid), HTTPStatus.OK

    def _get_pairing_data(self, pairing_code: str) -> bool:
        """Checking if there's one pairing session for the pairing code."""
        pairing_code_is_valid = False
        cache_key = 'pairing.code:' + pairing_code
        pairing_cache = self.cache.get(cache_key)
        if pairing_cache is not None:
            pairing_code_is_valid = True

        return pairing_code_is_valid
