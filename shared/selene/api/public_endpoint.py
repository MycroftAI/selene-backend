from flask import current_app, request
from flask.views import MethodView

from ..util.cache import SeleneCache


class PublicEndpoint(MethodView):
    """Abstract class for all endpoints used by Mycroft devices"""

    def __init__(self):
        self.config: dict = current_app.config
        self.request = request
        self.cache: SeleneCache = self.config['SELENE_CACHE']
