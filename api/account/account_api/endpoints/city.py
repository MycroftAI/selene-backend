from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import CityRepository


class CityEndpoint(SeleneEndpoint):
    def get(self):
        region_id = self.request.args['region']
        city_repository = CityRepository(self.db)
        cities = city_repository.get_cities_by_region(region_id=region_id)

        for city in cities:
            city.longitude = float(city.longitude)
            city.latitude = float(city.latitude)

        return cities, HTTPStatus.OK
