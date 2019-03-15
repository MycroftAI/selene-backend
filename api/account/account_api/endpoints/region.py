from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import RegionRepository
from selene.util.db import get_db_connection


class RegionEndpoint(SeleneEndpoint):
    def get(self):
        query_string = self.request.query_string.decode()
        country_id = query_string.split('=')[1]

        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            region_repository = RegionRepository(db)
            regions = region_repository.get_regions_by_country(country_id)

        return regions, HTTPStatus.OK
