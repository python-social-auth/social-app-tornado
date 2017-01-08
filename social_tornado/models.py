"""Tornado SQLAlchemy ORM models for Social Auth"""
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from social_core.utils import setting_name, module_member
from social_sqlalchemy.storage import SQLAlchemyUserMixin, \
                                      SQLAlchemyAssociationMixin, \
                                      SQLAlchemyNonceMixin, \
                                      SQLAlchemyCodeMixin, \
                                      SQLAlchemyPartialMixin, \
                                      BaseSQLAlchemyStorage


class TornadoStorage(BaseSQLAlchemyStorage):
    user = None
    nonce = None
    association = None
    code = None
    partial = None


def init_social(Base, session, settings):
    UID_LENGTH = settings.get(setting_name('UID_LENGTH'), 255)
    User = module_member(settings[setting_name('USER_MODEL')])
    app_session = session

    class _AppSession(object):
        @classmethod
        def _session(cls):
            return app_session

    class UserSocialAuth(_AppSession, Base, SQLAlchemyUserMixin):
        """Social Auth association model"""
        uid = Column(String(UID_LENGTH))
        user_id = Column(User.id.type, ForeignKey(User.id),
                         nullable=False, index=True)
        user = relationship(User, backref=backref('social_auth',
                                                  lazy='dynamic'))

        @classmethod
        def username_max_length(cls):
            return User.__table__.columns.get('username').type.length

        @classmethod
        def user_model(cls):
            return User

    class Nonce(_AppSession, Base, SQLAlchemyNonceMixin):
        """One use numbers"""
        pass

    class Association(_AppSession, Base, SQLAlchemyAssociationMixin):
        """OpenId account association"""
        pass

    class Code(_AppSession, Base, SQLAlchemyCodeMixin):
        """Mail validation single one time use code"""
        pass

    class Partial(_AppSession, Base, SQLAlchemyPartialMixin):
        """Partial pipeline storage"""
        pass

    # Set the references in the storage class
    TornadoStorage.user = UserSocialAuth
    TornadoStorage.nonce = Nonce
    TornadoStorage.association = Association
    TornadoStorage.code = Code
    TornadoStorage.partial = Partial
