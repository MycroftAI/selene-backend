from ..entity.country import Country
from ...repository_base import RepositoryBase


class CountryRepository(RepositoryBase):
    def __init__(self, db):
        super(CountryRepository, self).__init__(db, __file__)

    def get_countries(self):
        db_request = self._build_db_request(sql_file_name='get_countries.sql')
        db_result = self.cursor.select_all(db_request)

        return [Country(**row) for row in db_result]
