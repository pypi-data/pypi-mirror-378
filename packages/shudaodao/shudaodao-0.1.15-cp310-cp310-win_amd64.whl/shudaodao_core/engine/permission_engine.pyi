from ..config.app_config import AppConfig as AppConfig
from ..entity.auth_rule import AuthRule as AuthRule
from ..logger.logging_ import logging as logging
from ..services.db_engine_service import DBEngineService as DBEngineService
from ..utils.core_utils import CoreUtil as CoreUtil

class PermissionEngine:
    def __new__(cls): ...
    def get_async_enforcer(self): ...
    @staticmethod
    def check_table() -> None: ...
