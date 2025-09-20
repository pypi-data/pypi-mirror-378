from ..services.db_engine_service import DBEngineService as DBEngineService
from ..utils.core_utils import CoreUtil as CoreUtil
from casbin import AsyncEnforcer

async def get_casbin_enforcer() -> AsyncEnforcer: ...
