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

    def get_geography_id(self, geography: Geography):
        geography_id = None
        acct_geographies = self.get_account_geographies()
        for acct_geography in acct_geographies:
            match = (
                acct_geography.city == geography.city and
                acct_geography.country == geography.country and
                acct_geography.region == geography.region and
                acct_geography.time_zone == geography.time_zone
            )
            if match:
                geography_id = acct_geography.id
                break

        return geography_id

    def add(self, geography: Geography):
        db_request = self._build_db_request(
            sql_file_name='add_geography.sql',
            args=dict(
                account_id=self.account_id,
                city=geography.city,
                country=geography.country,
                region=geography.region,
                timezone=geography.time_zone
            )
        )
        db_result = self.cursor.insert_returning(db_request)

        return db_result['id']

    def get_location_by_device_id(self, device_id):
        db_request = self._build_db_request(
            sql_file_name='get_location_by_device_id.sql',
            args=dict(device_id=device_id)
        )
        return self.cursor.select_one(db_request)
