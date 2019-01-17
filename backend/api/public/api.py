from flask import Flask, make_response, json
from flask_restful import Api

from encoder import DataClassJsonEncoder
from endpoints.device import DeviceEndpoint

public = Flask(__name__)


def output_json(data, code, headers=None):
    resp = make_response(json.dumps(data, cls=DataClassJsonEncoder), code)
    resp.headers.extend(headers or {})
    return resp


public_api = Api(public)
public_api.representations['application/json'] = output_json

public_api.representations.update()

public_api.add_resource(DeviceEndpoint, '/device/<string:device_id>')
