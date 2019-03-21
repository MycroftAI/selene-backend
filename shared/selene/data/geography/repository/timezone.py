from ..entity.timezone import Timezone
from ...repository_base import RepositoryBase


class TimezoneRepository(RepositoryBase):
    def __init__(self, db):
        super(TimezoneRepository, self).__init__(db, __file__)

    def get_timezones_by_country(self, country_id):
        db_request = self._build_db_request(
            sql_file_name='get_timezones_by_country.sql',
            args=dict(country_id=country_id)
        )
        db_result = self.cursor.select_all(db_request)

        return [Timezone(**row) for row in db_result]
