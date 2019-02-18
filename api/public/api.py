from flask import Flask

from selene.api import SeleneResponse, selene_api
from selene.api.base_config import get_base_config

from .public_api.endpoints.device import DeviceEndpoint
from .public_api.endpoints.device_setting import DeviceSettingEndpoint
from .public_api.endpoints.device_skill import DeviceSkillEndpoint
from .public_api.endpoints.device_skills import DeviceSkillsEndpoint
from .public_api.endpoints.device_subscription import DeviceSubscriptionEndpoint
from .public_api.endpoints.open_weather_map import OpenWeatherMapEndpoint
from .public_api.endpoints.wolfram_alpha import WolframAlphaEndpoint
from .public_api.endpoints.google_stt import GoogleSTTEndpoint

public = Flask(__name__)
public.config.from_object(get_base_config())
public.response_class = SeleneResponse
public.register_blueprint(selene_api)


public.add_url_rule(
    '/device/<string:device_id>/skill',
    view_func=DeviceSkillsEndpoint.as_view('device_skill_api'),
    methods=['GET']
)
public.add_url_rule(
    '/device/<string:device_id>/userSkill',
    view_func=DeviceSkillEndpoint.as_view('device_user_skill_api'),
    methods=['GET']
)

public.add_url_rule(
    '/device/<string:device_id>',
    view_func=DeviceEndpoint.as_view('device_api'),
    methods=['GET']
)

public.add_url_rule(
    '/device/<string:device_id>/setting',
    view_func=DeviceSettingEndpoint.as_view('device_settings_api'),
    methods=['GET']
)

public.add_url_rule(
    '/device/<string:device_id>/subscription',
    view_func=DeviceSubscriptionEndpoint.as_view('device_subscription_api'),
    methods=['GET']
)
public.add_url_rule(
    '/wa',
    view_func=WolframAlphaEndpoint.as_view('wolfram_alpha_api'),
    methods=['GET']
)  # TODO: change this path in the API v2
public.add_url_rule(
    '/owm/<path:path>',
    view_func=OpenWeatherMapEndpoint.as_view('open_weather_map_api'),
    methods=['GET']
)     # TODO: change this path in the API v2
public.add_url_rule(
    '/stt',
    view_func=GoogleSTTEndpoint.as_view('google_stt_api'),
    methods=['POST']
)  # TODO: change this path in the API v2
