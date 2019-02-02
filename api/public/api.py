from flask import Flask
from flask_restful import Api
from selene.util.encoder import output_json

from endpoints.device import DeviceEndpoint
from endpoints.device_setting import DeviceSettingEndpoint
from endpoints.device_skill import DeviceSkillEndpoint

public = Flask(__name__)




public_api = Api(public)
public_api.representations['application/json'] = output_json

public_api.representations.update()

public_api.add_resource(DeviceSkillEndpoint, '/device/<string:device_id>/skill')
public_api.add_resource(DeviceEndpoint, '/device/<string:device_id>')
public_api.add_resource(DeviceSettingEndpoint, '/device/<string:device_id>/setting')
