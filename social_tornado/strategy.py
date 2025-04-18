import json

from social_core.strategy import BaseStrategy, BaseTemplateStrategy
from social_core.utils import build_absolute_uri
from tornado.template import Loader, Template


class TornadoTemplateStrategy(BaseTemplateStrategy):
    def render_template(self, tpl, context):
        path, tpl = tpl.rsplit("/", 1)
        return Loader(path).load(tpl).generate(**context)

    def render_string(self, html, context):
        return Template(html).generate(**context)


class TornadoStrategy(BaseStrategy):
    DEFAULT_TEMPLATE_STRATEGY = TornadoTemplateStrategy

    def __init__(self, storage, request_handler, tpl=None):
        self.request_handler = request_handler
        self.request = self.request_handler.request
        super().__init__(storage, tpl)

    def get_setting(self, name):
        return self.request_handler.settings[name]

    def request_data(self, merge=True):
        # Multiple valued arguments not supported yet
        return {
            key: val[0].decode()  # fmt: skip
            for key, val in self.request.arguments.items()
        }

    def request_host(self):
        return self.request.host

    def redirect(self, url):
        return self.request_handler.redirect(url)

    def html(self, content):
        self.request_handler.write(content)

    def session_get(self, name, default=None):
        value = self.request_handler.get_secure_cookie(name)
        if value:
            return json.loads(value.decode())
        return default

    def session_set(self, name, value):
        self.request_handler.set_secure_cookie(  # fmt: skip
            name, json.dumps(value).encode()
        )

    def session_pop(self, name):
        value = self.session_get(name)
        self.request_handler.clear_cookie(name)
        return value

    def session_setdefault(self, name, value):
        pass

    def build_absolute_uri(self, path=None):
        return build_absolute_uri(
            f"{self.request.protocol}://{self.request.host}", path
        )

    def partial_to_session(self, next, backend, request=None, *args, **kwargs):
        return json.dumps(
            super().partial_to_session(  # fmt: skip
                next, backend, request=request, *args, **kwargs
            )
        )

    def partial_from_session(self, session):
        if session:
            return super().partial_to_session(json.loads(session))
