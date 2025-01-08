from social_core.actions import do_auth, do_complete, do_disconnect
from tornado.web import RequestHandler

# from social_core.backends.utils import load_strategy, get_backend
from social_tornado.utils import load_backend, load_strategy

from .utils import psa


class BaseHandler(RequestHandler):
    def initialize(self):
        self.strategy = load_strategy(self)

    def user_id(self):
        return self.get_secure_cookie("user_id")

    def get_current_user(self):
        user_id = self.user_id()

        if user_id:
            return self.backend.strategy.get_user(int(user_id))

    def login_user(self, user):
        self.set_secure_cookie("user_id", str(user.id))


class AuthHandler(BaseHandler):
    def get(self, backend):
        self._auth(backend)

    def post(self, backend):
        self._auth(backend)

    @psa("complete")
    def _auth(self, backend):
        do_auth(self.backend)


class CompleteHandler(BaseHandler):
    def get(self, backend):
        self._complete(backend)

    def post(self, backend):
        self._complete(backend)

    @psa("complete")
    def _complete(self, backend):
        do_complete(
            self.backend,
            login=lambda backend, user, social_user: self.login_user(user),
            user=self.get_current_user(),
        )


class DisconnectHandler(BaseHandler):
    def post(self, user=None, backend=None, association_id=None):
        self.backend = load_backend(self, self.strategy, backend, "/")
        do_disconnect(  # fmt: skip
            self.backend,  # fmt: skip
            self.get_current_user(),  # fmt: skip
            association_id,  # fmt: skip
            redirect_name="next",
        )
