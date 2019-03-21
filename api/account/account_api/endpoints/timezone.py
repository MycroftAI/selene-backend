from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import TimezoneRepository
from selene.util.db import get_db_connection


class TimezoneEndpoint(SeleneEndpoint):
    def get(self):
        country_id = self.request.args['country_id']
        with get_db_connection(self.config['DB_CONNECTION_POOL']) as db:
            timezone_repository = TimezoneRepository(db)
            timezones = timezone_repository.get_timezones_by_country(country_id)

        for timezone in timezones:
            timezone.dst_offset = float(timezone.dst_offset)
            timezone.gmt_offset = float(timezone.gmt_offset)

        return timezones, HTTPStatus.OK
