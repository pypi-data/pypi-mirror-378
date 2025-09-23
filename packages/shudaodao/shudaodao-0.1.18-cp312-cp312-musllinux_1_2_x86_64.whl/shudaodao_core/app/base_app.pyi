import abc
from ..auth.auth_router import AuthRouter as AuthRouter
from ..config.app_config import AppConfig as AppConfig
from ..logger.logging_ import logging as logging
from ..services.premission_service import PermissionService as PermissionService
from ..tools.class_scaner import ClassScanner as ClassScanner
from ..utils.core_utils import CoreUtil as CoreUtil
from _typeshed import Incomplete
from abc import ABC, abstractmethod

class BaseApplication(ABC, metaclass=abc.ABCMeta):
    app: Incomplete
    def __init__(self) -> None: ...
    @abstractmethod
    def application_onload(self): ...
    @abstractmethod
    def application_unload(self): ...
