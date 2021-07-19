# Mycroft Server - Backend
# Copyright (C) 2019 Mycroft AI Inc
# SPDX-License-Identifier: 	AGPL-3.0-or-later
#
# This file is part of the Mycroft Server.
#
# The Mycroft Server is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

"""Entry point for the API that supports the Mycroft Marketplace."""
from flask import Flask

from selene.api import get_base_config, selene_api, SeleneResponse
from selene.api.endpoints import AccountEndpoint, AgreementsEndpoint
from selene.util.cache import SeleneCache
from selene.util.log import configure_logger
from .endpoints import (
    PreferencesEndpoint,
    CityEndpoint,
    CountryEndpoint,
    AccountDefaultsEndpoint,
    DeviceEndpoint,
    DeviceCountEndpoint,
    GeographyEndpoint,
    MembershipEndpoint,
    RegionEndpoint,
    PairingCodeEndpoint,
    SkillsEndpoint,
    SkillOauthEndpoint,
    SkillSettingsEndpoint,
    SoftwareUpdateEndpoint,
    SshKeyValidatorEndpoint,
    TimezoneEndpoint,
    VoiceEndpoint,
    WakeWordEndpoint,
)

_log = configure_logger("account_api")


# Define the Flask application
acct = Flask(__name__)
acct.config.from_object(get_base_config())
acct.response_class = SeleneResponse
acct.register_blueprint(selene_api)
acct.config["SELENE_CACHE"] = SeleneCache()

account_endpoint = AccountEndpoint.as_view("account_endpoint")
acct.add_url_rule(
    "/api/account", view_func=account_endpoint, methods=["GET", "PATCH", "DELETE"]
)

agreements_endpoint = AgreementsEndpoint.as_view("agreements_endpoint")
acct.add_url_rule(
    "/api/agreement/<string:agreement_type>",
    view_func=agreements_endpoint,
    methods=["GET"],
)

city_endpoint = CityEndpoint.as_view("city_endpoint")
acct.add_url_rule("/api/cities", view_func=city_endpoint, methods=["GET"])

country_endpoint = CountryEndpoint.as_view("country_endpoint")
acct.add_url_rule("/api/countries", view_func=country_endpoint, methods=["GET"])

defaults_endpoint = AccountDefaultsEndpoint.as_view("defaults_endpoint")
acct.add_url_rule(
    "/api/defaults", view_func=defaults_endpoint, methods=["GET", "PATCH", "POST"]
)

device_endpoint = DeviceEndpoint.as_view("device_endpoint")
acct.add_url_rule(
    "/api/devices",
    defaults={"device_id": None},
    view_func=device_endpoint,
    methods=["GET"],
)
acct.add_url_rule("/api/devices", view_func=device_endpoint, methods=["POST"])
acct.add_url_rule(
    "/api/devices/<string:device_id>",
    view_func=device_endpoint,
    methods=["DELETE", "GET", "PATCH"],
)

device_count_endpoint = DeviceCountEndpoint.as_view("device_count_endpoint")
acct.add_url_rule("/api/device-count", view_func=device_count_endpoint, methods=["GET"])

geography_endpoint = GeographyEndpoint.as_view("geography_endpoint")
acct.add_url_rule("/api/geographies", view_func=geography_endpoint, methods=["GET"])

membership_endpoint = MembershipEndpoint.as_view("membership_endpoint")
acct.add_url_rule("/api/memberships", view_func=membership_endpoint, methods=["GET"])

ssh_key_validation_endpoint = PairingCodeEndpoint.as_view("pairing_code_endpoint")
acct.add_url_rule(
    "/api/pairing-code/<string:pairing_code>",
    view_func=ssh_key_validation_endpoint,
    methods=["GET"],
)

preferences_endpoint = PreferencesEndpoint.as_view("preferences_endpoint")
acct.add_url_rule(
    "/api/preferences", view_func=preferences_endpoint, methods=["GET", "PATCH", "POST"]
)

region_endpoint = RegionEndpoint.as_view("region_endpoint")
acct.add_url_rule("/api/regions", view_func=region_endpoint, methods=["GET"])

setting_endpoint = SkillSettingsEndpoint.as_view("setting_endpoint")
acct.add_url_rule(
    "/api/skills/<string:skill_family_name>/settings",
    view_func=setting_endpoint,
    methods=["GET", "PUT"],
)

skill_endpoint = SkillsEndpoint.as_view("skill_endpoint")
acct.add_url_rule("/api/skills", view_func=skill_endpoint, methods=["GET"])

skill_oauth_endpoint = SkillOauthEndpoint.as_view("skill_oauth_endpoint")
acct.add_url_rule(
    "/api/skills/oauth/<int:oauth_id>", view_func=skill_oauth_endpoint, methods=["GET"]
)

software_update_endpoint = SoftwareUpdateEndpoint.as_view("software_update_endpoint")
acct.add_url_rule(
    "/api/software-update", view_func=software_update_endpoint, methods=["PATCH"]
)

ssh_key_validation_endpoint = SshKeyValidatorEndpoint.as_view(
    "ssh_key_validation_endpoint"
)
acct.add_url_rule(
    "/api/ssh-key/<string:ssh_key>",
    view_func=ssh_key_validation_endpoint,
    methods=["GET"],
)

timezone_endpoint = TimezoneEndpoint.as_view("timezone_endpoint")
acct.add_url_rule("/api/timezones", view_func=timezone_endpoint, methods=["GET"])

voice_endpoint = VoiceEndpoint.as_view("voice_endpoint")
acct.add_url_rule("/api/voices", view_func=voice_endpoint, methods=["GET"])

wake_word_endpoint = WakeWordEndpoint.as_view("wake_word_endpoint")
acct.add_url_rule("/api/wake-words", view_func=wake_word_endpoint, methods=["GET"])
