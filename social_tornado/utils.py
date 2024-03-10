import warnings
from functools import wraps

from social_core.backends.utils import get_backend
from social_core.utils import get_strategy, setting_name

DEFAULTS = {
    "STORAGE": "social_tornado.models.TornadoStorage",
    "STRATEGY": "social_tornado.strategy.TornadoStrategy",
}


def get_helper(request_handler, name):
    return request_handler.settings.get(  # fmt: skip
        setting_name(name), DEFAULTS.get(name, None))


def load_strategy(request_handler):
    strategy = get_helper(request_handler, "STRATEGY")
    storage = get_helper(request_handler, "STORAGE")
    return get_strategy(strategy, storage, request_handler)


def load_backend(request_handler, strategy, name, redirect_uri):
    backends = get_helper(request_handler, "AUTHENTICATION_BACKENDS")
    Backend = get_backend(backends, name)
    return Backend(strategy, redirect_uri)


def psa(redirect_uri=None):
    def decorator(func):
        @wraps(func)
        def wrapper(self, backend, *args, **kwargs):
            uri = redirect_uri
            if uri and not uri.startswith("/"):
                uri = self.reverse_url(uri, backend)
            self.strategy = load_strategy(self)
            self.backend = load_backend(self, self.strategy, backend, uri)
            return func(self, backend, *args, **kwargs)

        return wrapper

    return decorator


def strategy(*args, **kwargs):
    warnings.warn("@strategy decorator is deprecated, use @psa instead")
    return psa(*args, **kwargs)
