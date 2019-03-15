from ..entity.city import City
from ...repository_base import RepositoryBase


class CityRepository(RepositoryBase):
    def __init__(self, db):
        super(CityRepository, self).__init__(db, __file__)

    def get_cities_by_region(self, region_id):
        db_request = self._build_db_request(
            sql_file_name='get_cities_by_region.sql',
            args=dict(region_id=region_id)
        )
        db_result = self.cursor.select_all(db_request)

        return [City(**row) for row in db_result]
