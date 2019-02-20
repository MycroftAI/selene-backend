import os

from flask import Flask

from selene.api import SeleneResponse, selene_api
from selene.api.base_config import get_base_config
from selene.util.cache import SeleneCache

from .endpoints.device import DeviceEndpoint
from .endpoints.device_setting import DeviceSettingEndpoint
from .endpoints.device_skill import DeviceSkillEndpoint
from .endpoints.device_skills import DeviceSkillsEndpoint
from .endpoints.device_subscription import DeviceSubscriptionEndpoint
from .endpoints.open_weather_map import OpenWeatherMapEndpoint
from .endpoints.wolfram_alpha import WolframAlphaEndpoint
from .endpoints.google_stt import GoogleSTTEndpoint
from .endpoints.device_code import DeviceCodeEndpoint
from .endpoints.device_activate import DeviceActivateEndpoint
from .endpoints.account_device import AccountDeviceEndpoint

public = Flask(__name__)
public.config.from_object(get_base_config())
public.config['GOOGLE_STT_KEY'] = os.environ['GOOGLE_STT_KEY']
public.config['SELENE_CACHE'] = SeleneCache()

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
public.add_url_rule(
    '/device/code',
    view_func=DeviceCodeEndpoint.as_view('device_code_api'),
    methods=['GET']
)
public.add_url_rule(
    '/device/activate',
    view_func=DeviceActivateEndpoint.as_view('device_activate_api'),
    methods=['POST']
)
public.add_url_rule(
    '/api/account/<string:account_id>/device',
    view_func=AccountDeviceEndpoint.as_view('account_device_api'),
    methods=['POST']
)
