from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import CountryRepository


class CountryEndpoint(SeleneEndpoint):
    def get(self):
        country_repository = CountryRepository(self.db)
        countries = country_repository.get_countries()

        return countries, HTTPStatus.OK
