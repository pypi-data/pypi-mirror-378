import abc
from ..auth.auth_router import AuthRouter as AuthRouter
from ..config.app_config import AppConfig as AppConfig
from ..controller.auth import Auth_Controller as Auth_Controller
from ..controller.default import Default_Controller as Default_Controller
from ..exception.register_handlers import register_exception_handlers as register_exception_handlers
from ..logger.logging_ import logging as logging
from ..utils.core_utils import CoreUtil as CoreUtil
from _typeshed import Incomplete
from abc import ABC, abstractmethod

class BaseApplication(ABC, metaclass=abc.ABCMeta):
    app: Incomplete
    def __init__(self) -> None: ...
    @abstractmethod
    def add_middleware(self) -> None: ...
    @abstractmethod
    def add_router(self) -> None: ...
    def include_router(self, controllers) -> None: ...
