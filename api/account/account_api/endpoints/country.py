from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import CountryRepository
from selene.util.db import get_db_connection


class CountryEndpoint(SeleneEndpoint):
    def get(self):
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            country_repository = CountryRepository(db)
            countries = country_repository.get_countries()

        return countries, HTTPStatus.OK
