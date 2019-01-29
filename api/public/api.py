from flask import Flask, make_response, json
from flask_restful import Api

from encoder import DataClassJsonEncoder
from endpoints.device import DeviceEndpoint
from endpoints.device_setting import DeviceSettingEndpoint
from endpoints.device_skill import DeviceSkillEndpoint

public = Flask(__name__)


def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=DataClassJsonEncoder), code)
    resp.headers.extend(headers or {})
    return resp


public_api = Api(public)
public_api.representations['application/json'] = output_json

public_api.representations.update()

public_api.add_resource(DeviceSkillEndpoint, '/device/<string:device_id>/skill')
public_api.add_resource(DeviceEndpoint, '/device/<string:device_id>')
public_api.add_resource(DeviceSettingEndpoint, '/device/<string:device_id>/setting')
