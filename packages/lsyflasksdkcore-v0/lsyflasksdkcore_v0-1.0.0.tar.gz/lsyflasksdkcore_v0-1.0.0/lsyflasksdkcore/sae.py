from abc import ABCMeta, abstractmethod
from typing import Optional

from flask_login import LoginManager


class AuthUserABC(metaclass=ABCMeta):
    @property
    @abstractmethod
    def is_active(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_authenticated(self) -> bool:
        return True

    @property
    @abstractmethod
    def is_superuser(self) -> bool:
        pass

    @property
    @abstractmethod
    def system_role_id(self) -> str:
        pass

    @property
    @abstractmethod
    def is_anonymous(self) -> bool:
        return False

    @abstractmethod
    def get_id(self):
        pass

    @abstractmethod
    def get_name(self):
        pass


class TokenManagerABC(metaclass=ABCMeta):

    def init_app(self, app):
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.request_loader(self.request_loader)

    @abstractmethod
    def request_loader(self, request) -> Optional[AuthUserABC]:
        pass
