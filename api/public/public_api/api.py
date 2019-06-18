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
from .endpoints.device_skill import DeviceSkillEndpoint
from .endpoints.device_skill_manifest import DeviceSkillManifestEndpoint
from .endpoints.device_skills import DeviceSkillsEndpoint
from .endpoints.device_subscription import DeviceSubscriptionEndpoint
from .endpoints.google_stt import GoogleSTTEndpoint
from .endpoints.oauth_callback import OauthCallbackEndpoint
from .endpoints.open_weather_map import OpenWeatherMapEndpoint
from .endpoints.premium_voice import PremiumVoiceEndpoint
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
    '/v1/device/<string:device_id>/skill/<string:skill_id>',
    view_func=DeviceSkillsEndpoint.as_view('device_skill_delete_api'),
    methods=['DELETE']
)

public.add_url_rule(
    '/v1/device/<string:device_id>/skill',
    view_func=DeviceSkillsEndpoint.as_view('device_skill_api'),
    methods=['GET', 'PUT']
)

public.add_url_rule(
    '/v1/device/<string:device_id>/userSkill',
    view_func=DeviceSkillEndpoint.as_view('device_user_skill_api'),
    methods=['GET']
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

"""
This is a workaround to allow the API return 401 when we call a non existent path. Use case:
GET /device/{uuid} with empty uuid. Core today uses the 401 to validate if it needs to perform a pairing process
Whe should fix that in a future version because we have to return 404 when we call a non existent path
"""
public.before_request(check_oauth_token)
