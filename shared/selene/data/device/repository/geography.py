from ..entity.geography import Geography
from ...repository_base import RepositoryBase


class GeographyRepository(RepositoryBase):
    def __init__(self, db, account_id):
        super(GeographyRepository, self).__init__(db, __file__)
        self.account_id = account_id

    def get_account_geographies(self):
        db_request = self._build_db_request(
            sql_file_name='get_account_geographies.sql',
            args=dict(account_id=self.account_id)
        )
        db_response = self.cursor.select_all(db_request)

        return [Geography(**row) for row in db_response]

    def add(self, geography):
        db_request_args = dict(account_id=self.account_id)
        db_request_args.update(geography)
        db_request = self._build_db_request(
            sql_file_name='add_geography.sql',
            args=db_request_args
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result['id']
