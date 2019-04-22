from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import RegionRepository


class RegionEndpoint(SeleneEndpoint):
    def get(self):
        country_id = self.request.args['country']
        region_repository = RegionRepository(self.db)
        regions = region_repository.get_regions_by_country(country_id)

        return regions, HTTPStatus.OK
