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

import os

from flask import Flask

from selene.api import SeleneResponse, selene_api
from selene.api.base_config import get_base_config
from selene.api.public_endpoint import check_oauth_token
from selene.util.cache import SeleneCache
from selene.util.log import configure_logger
from .endpoints.device import DeviceEndpoint
from .endpoints.device_activate import DeviceActivateEndpoint
from .endpoints.device_code import DeviceCodeEndpoint
from .endpoints.device_email import DeviceEmailEndpoint
from .endpoints.device_location import DeviceLocationEndpoint
from .endpoints.device_metrics import DeviceMetricsEndpoint
from .endpoints.device_oauth import OauthServiceEndpoint
from .endpoints.device_refresh_token import DeviceRefreshTokenEndpoint
from .endpoints.device_setting import DeviceSettingEndpoint
from .endpoints.device_skill import SkillSettingsMetaEndpoint
from .endpoints.device_skill_manifest import DeviceSkillManifestEndpoint
from .endpoints.device_skill_settings import DeviceSkillSettingsEndpoint
from .endpoints.device_skill_settings import DeviceSkillSettingsEndpointV2
from .endpoints.device_subscription import DeviceSubscriptionEndpoint
from .endpoints.geolocation import GeolocationEndpoint
from .endpoints.google_stt import GoogleSTTEndpoint
from .endpoints.oauth_callback import OauthCallbackEndpoint
from .endpoints.open_weather_map import OpenWeatherMapEndpoint
from .endpoints.premium_voice import PremiumVoiceEndpoint
from .endpoints.stripe_webhook import StripeWebHookEndpoint
from .endpoints.wolfram_alpha import WolframAlphaEndpoint
from .endpoints.wolfram_alpha_spoken import WolframAlphaSpokenEndpoint

_log = configure_logger('public_api')

public = Flask(__name__)
public.config.from_object(get_base_config())
public.config['GOOGLE_STT_KEY'] = os.environ['GOOGLE_STT_KEY']
public.config['SELENE_CACHE'] = SeleneCache()
public.response_class = SeleneResponse
public.register_blueprint(selene_api)
public.add_url_rule(
    '/v1/device/<string:device_id>/skill/<string:skill_gid>',
    view_func=DeviceSkillSettingsEndpoint.as_view('device_skill_delete_api'),
    methods=['DELETE']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/skill',
    view_func=DeviceSkillSettingsEndpoint.as_view('device_skill_api'),
    methods=['GET', 'PUT']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/skill/settings',
    view_func=DeviceSkillSettingsEndpointV2.as_view('skill_settings_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/settingsMeta',
    view_func=SkillSettingsMetaEndpoint.as_view('device_user_skill_api'),
    methods=['PUT']
)
public.add_url_rule(
    '/v1/device/<string:device_id>',
    view_func=DeviceEndpoint.as_view('device_api'),
    methods=['GET', 'PATCH']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/setting',
    view_func=DeviceSettingEndpoint.as_view('device_settings_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/subscription',
    view_func=DeviceSubscriptionEndpoint.as_view('device_subscription_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/geolocation',
    view_func=GeolocationEndpoint.as_view('location_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/wa',
    view_func=WolframAlphaEndpoint.as_view('wolfram_alpha_api'),
    methods=['GET']
)  # TODO: change this path in the API v2
public.add_url_rule(
    '/v1/owm/<path:path>',
    view_func=OpenWeatherMapEndpoint.as_view('open_weather_map_api'),
    methods=['GET']
)     # TODO: change this path in the API v2
public.add_url_rule(
    '/v1/stt',
    view_func=GoogleSTTEndpoint.as_view('google_stt_api'),
    methods=['POST']
)  # TODO: change this path in the API v2
public.add_url_rule(
    '/v1/device/code',
    view_func=DeviceCodeEndpoint.as_view('device_code_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/device/activate',
    view_func=DeviceActivateEndpoint.as_view('device_activate_api'),
    methods=['POST']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/message',
    view_func=DeviceEmailEndpoint.as_view('device_email_api'),
    methods=['PUT']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/metric/<path:metric>',
    view_func=DeviceMetricsEndpoint.as_view('device_metric_api'),
    methods=['POST']
)
public.add_url_rule(
    '/v1/auth/token',
    view_func=DeviceRefreshTokenEndpoint.as_view('refresh_token_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/wolframAlphaSpoken',
    view_func=WolframAlphaSpokenEndpoint.as_view('wolfram_alpha_spoken_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/location',
    view_func=DeviceLocationEndpoint.as_view('device_location_api'),
    methods=['GET']
)
public.add_url_rule(
    '/v1/device/<string:device_id>/skillJson',
    view_func=DeviceSkillManifestEndpoint.as_view('skill_manifest_api'),
    methods=['GET', 'PUT']
)

public.add_url_rule(
    '/v1/auth/callback',
    view_func=OauthCallbackEndpoint.as_view('oauth_callback_api'),
    methods=['GET']
)

public.add_url_rule(
    '/v1/device/<string:device_id>/voice',
    view_func=PremiumVoiceEndpoint.as_view('premium_voice_api'),
    methods=['GET']
)

public.add_url_rule(
    '/v1/device/<string:device_id>/<string:oauth_path>/<string:credentials>',
    view_func=OauthServiceEndpoint.as_view('oauth_api'),
    methods=['GET']
)

public.add_url_rule(
    '/v1/user/stripe/webhook',
    view_func=StripeWebHookEndpoint.as_view('stripe_webhook_api'),
    methods=['POST']
)


# This is a workaround to allow the API return 401 when we call a non existent
# path. Use case: GET /device/{uuid} with empty uuid. Core today uses the 401
# to validate if it needs to perform a pairing process. We should fix that in a
# future version because we have to return 404 when we call a non existent path
public.before_request(check_oauth_token)
