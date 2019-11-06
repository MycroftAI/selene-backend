"""Call this endpoint to retrieve the timezone for a given location"""
from dataclasses import asdict
from http import HTTPStatus
from logging import getLogger

from selene.api import PublicEndpoint
from selene.data.geography import CityRepository

ONE_HUNDRED_MILES = 100

_log = getLogger()


class GeolocationEndpoint(PublicEndpoint):
    def __init__(self):
        super().__init__()
        self.device_id = None
        self.request_geolocation = None
        self.cities = None
        self._city_repo = None

    @property
    def city_repo(self):
        """Lazy load the CityRepository."""
        if self._city_repo is None:
            self._city_repo = CityRepository(self.db)

        return self._city_repo

    def get(self):
        """Handle a HTTP GET request."""
        self.request_geolocation = self.request.args['location'].lower()
        response_geolocation = self._get_geolocation()

        return dict(data=response_geolocation), HTTPStatus.OK

    def _get_geolocation(self):
        """Try our best to find a geolocation matching the request."""
        self._get_cities()
        if self.cities:
            selected_geolocation = self._select_geolocation_from_cities()
        else:
            selected_geolocation = self.city_repo.get_biggest_city_in_region(
                self.request_geolocation
            )

        if selected_geolocation is None:
            selected_geolocation = self.city_repo.get_biggest_city_in_country(
                self.request_geolocation
            )

        if selected_geolocation is not None:
            selected_geolocation.latitude = float(
                selected_geolocation.latitude
            )
            selected_geolocation.longitude = float(
                selected_geolocation.longitude
            )

        return selected_geolocation

    def _get_cities(self):
        """Retrieve a list of cities matching the requested location.

        City names can be a single word (e.g. Seattle) or multiple words
        (e.g. Kansas City).  Query the database for all permutations of words
        in the location passed in the request. For example, a request for
        "Kansas City Missouri" will pass "Kansas" and "Kansas City" and
        "Kansas City Missouri"

        This logic assumes that it will not find a match when a city and
        region/country are included in the request. For example, a request for
        "Kansas City Missouri" should only find a match for "Kansas City".
        """
        possible_city_names = []
        geolocation_words = self.request_geolocation.split()
        for index, word in enumerate(geolocation_words):
            possible_city_name = ' '.join(geolocation_words[:index + 1])
            possible_city_names.append(possible_city_name)

        self.cities = self.city_repo.get_geographic_location_by_city(
            possible_city_names
        )

    def _select_geolocation_from_cities(self):
        """Select one of the cities returned by the database.

        If a single match is found, select it.  If multiple matches are found,
        return the city with the biggest population.  If multiple matches are
        found and a region or country is included in the requested location,
        attempt to match based on the extra criteria.
        """
        selected_geolocation = None
        if len(self.cities) == 1:
            selected_geolocation = self.cities[0]
        elif len(self.cities) > 1:
            biggest_city = self.cities[0]
            if biggest_city.city.lower() == self.request_geolocation:
                selected_geolocation = biggest_city
            else:
                city_in_region = self._get_city_for_requested_region()
                city_in_country = self._get_city_for_requested_country()
                selected_geolocation = city_in_region or city_in_country

        return selected_geolocation

    def _get_city_for_requested_region(self):
        """If a region is in the request, get the city in that region.

        Example:
            A request for "Kansas City Missouri" should return the city of
            Kansas City in the state of Missouri
        """
        city_in_requested_region = None
        for city in self.cities:
            location_without_city = self.request_geolocation[len(city.city):]
            if city.region.lower() in location_without_city.strip():
                city_in_requested_region = city
                break

        return city_in_requested_region

    def _get_city_for_requested_country(self):
        """If a country is in the request, get the city in that country.

        Examples:
            A request for "Sydney Australia" should return the city of Syndey
            in the country of Australia.
        """
        selected_city = None
        for city in self.cities:
            location_without_city = self.request_geolocation[len(city.city):]
            if city.country.lower() in location_without_city.strip():
                selected_city = city
                break

        return selected_city
