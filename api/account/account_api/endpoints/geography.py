from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.device import GeographyRepository
from selene.util.db import get_db_connection


class GeographyEndpoint(SeleneEndpoint):
    def get(self):
        self._authenticate()
        response_data = self._build_response_data()

        return response_data, HTTPStatus.OK

    def _build_response_data(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            geography_repostiory = GeographyRepository(db, self.account.id)
            geographies = geography_repostiory.get_account_geographies()

        response_data = []
        for geography in geographies:
            response_data.append(
                dict(id=geography.id, name=geography.country, user_defined=True)
            )

        return response_data
