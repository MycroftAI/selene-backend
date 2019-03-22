from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import CityRepository
from selene.util.db import get_db_connection


class CityEndpoint(SeleneEndpoint):
    def get(self):
        region_id = self.request.args['region']
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            city_repository = CityRepository(db)
            cities = city_repository.get_cities_by_region(region_id=region_id)

        for city in cities:
            city.longitude = float(city.longitude)
            city.latitude = float(city.latitude)

        return cities, HTTPStatus.OK
