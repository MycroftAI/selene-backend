from ..entity.region import Region
from ...repository_base import RepositoryBase


class RegionRepository(RepositoryBase):
    def __init__(self, db):
        super(RegionRepository, self).__init__(db, __file__)

    def get_regions_by_country(self, country_id):
        db_request = self._build_db_request(
            sql_file_name='get_regions_by_country.sql',
            args=dict(country_id=country_id)
        )
        db_result = self.cursor.select_all(db_request)

        return [Region(**row) for row in db_result]
