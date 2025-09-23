from ..config.app_config import AppConfig as AppConfig
from ..entity.auth_user import AuthLogin as AuthLogin, AuthPassword as AuthPassword, AuthUser as AuthUser, AuthUserResponse as AuthUserResponse
from ..exception.service_exception import AuthException as AuthException, LoginException as LoginException
from ..schemas.query_request import QueryRequest as QueryRequest
from ..services.data_service import DataService as DataService
from ..services.db_engine_service import DBEngineService as DBEngineService
from .premission_service import PermissionService as PermissionService
from _typeshed import Incomplete
from datetime import timedelta
from sqlmodel.ext.asyncio.session import AsyncSession as AsyncSession

class AuthService:
    TOKEN_SECRET_KEY: Incomplete
    TOKEN_ALGORITHM: str
    TOKEN_EXPIRE_MINUTES: Incomplete
    Password: Incomplete
    oauth2_scheme: Incomplete
    @classmethod
    def verify_password(cls, plain_password, hashed_password): ...
    @classmethod
    def hash_password(cls, password): ...
    @classmethod
    def token_encode(cls, data: dict, expires_delta: timedelta | None = None) -> str: ...
    @classmethod
    def token_decode(cls, token) -> dict: ...
    @classmethod
    def get_permission(cls): ...
    @classmethod
    async def get_current_user(cls, token=..., db: AsyncSession = ...) -> AuthUser: ...
    @classmethod
    async def logout(cls) -> None: ...
    @classmethod
    async def refresh(cls): ...
    @classmethod
    async def login(cls, *, db: AsyncSession, auth_login: AuthLogin): ...
    @classmethod
    async def modify_password(cls, db: AsyncSession, *, password_model: AuthPassword, auth_user: AuthUser): ...
