"""Tornado SQLAlchemy ORM models for Social Auth"""

from social_core.utils import module_member, setting_name
from social_sqlalchemy.storage import (
    BaseSQLAlchemyStorage,
    SQLAlchemyAssociationMixin,
    SQLAlchemyCodeMixin,
    SQLAlchemyNonceMixin,
    SQLAlchemyPartialMixin,
    SQLAlchemyUserMixin,
)
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, backref, mapped_column, relationship


class TornadoStorage(BaseSQLAlchemyStorage):
    user = None
    nonce = None
    association = None
    code = None
    partial = None


def init_social(Base, session, settings):
    UID_LENGTH = settings.get(setting_name("UID_LENGTH"), 255)
    User = module_member(settings[setting_name("USER_MODEL")])
    app_session = session

    class _AppSession:
        @classmethod
        def _session(cls):
            return app_session

    class UserSocialAuth(_AppSession, Base, SQLAlchemyUserMixin):
        """Social Auth association model"""

        uid: Mapped[str] = mapped_column(String(UID_LENGTH))
        user_id: Mapped[int] = mapped_column(
            ForeignKey(User.id), nullable=False, index=True
        )
        user: Mapped["User"] = relationship(  # fmt: skip
            User, backref=backref("social_auth", lazy="dynamic")
        )

        @classmethod
        def username_max_length(cls):
            return User.__table__.columns.get("username").type.length

        @classmethod
        def user_model(cls):
            return User

    class Nonce(_AppSession, Base, SQLAlchemyNonceMixin):
        """One use numbers"""

    class Association(_AppSession, Base, SQLAlchemyAssociationMixin):
        """OpenId account association"""

    class Code(_AppSession, Base, SQLAlchemyCodeMixin):
        """Mail validation single one time use code"""

    class Partial(_AppSession, Base, SQLAlchemyPartialMixin):
        """Partial pipeline storage"""

    # Set the references in the storage class
    TornadoStorage.user = UserSocialAuth
    TornadoStorage.nonce = Nonce
    TornadoStorage.association = Association
    TornadoStorage.code = Code
    TornadoStorage.partial = Partial
