from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import GeographyRepository


class GeographyEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        geography_repository = GeographyRepository(self.db, self.account.id)
        geographies = geography_repository.get_account_geographies()

        response_data = []
        for geography in geographies:
            response_data.append(
                dict(id=geography.id, name=geography.country, user_defined=True)
            )

        return response_data
