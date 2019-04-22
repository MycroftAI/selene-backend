from http import HTTPStatus

from selene.api import SeleneEndpoint
from selene.data.geography import TimezoneRepository


class TimezoneEndpoint(SeleneEndpoint):
    def get(self):
        country_id = self.request.args['country']
        timezone_repository = TimezoneRepository(self.db)
        timezones = timezone_repository.get_timezones_by_country(country_id)

        for timezone in timezones:
            timezone.dst_offset = float(timezone.dst_offset)
            timezone.gmt_offset = float(timezone.gmt_offset)

        return timezones, HTTPStatus.OK
