import typing as t
from contextlib import suppress
from contextvars import ContextVar
from datetime import timedelta
from time import time

from acb.config import Config
from acb.debug import debug
from acb.depends import depends
from firebase_admin import auth as firebase_auth
from firebase_admin import initialize_app
from google.auth.transport import requests as google_requests
from pydantic import EmailStr, SecretStr
from sqlmodel import SQLModel, select  # type: ignore
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from ._base import AuthBase, AuthBaseSettings

firebase_request_adapter: google_requests.Request = google_requests.Request()
firebase_app: t.Any = None


class AuthSettings(AuthBaseSettings):
    api_key: SecretStr = SecretStr("")
    app_id: str = ""
    messaging_sender_id: str = ""


class CurrentUser:
    user_data: t.Any = {}

    def has_role(self, role: str) -> str:
        return self.user_data.custom_claims.get(role)

    def set_role(self, role: str) -> str | bool | None:
        return firebase_auth.set_custom_user_claims(self.user_data["uid"], {role: True})

    @property
    def identity(self) -> str | None:
        return self.user_data.get("uid")

    @property
    def display_name(self) -> str | None:
        return self.user_data.get("name")

    @property
    def email(self) -> EmailStr | None:
        return self.user_data.get("email")

    @property
    def gmail(self) -> str | None:
        return self.user_data.get("gmail")

    @depends.inject
    def is_authenticated(
        self, request: Request | None, config: Config = depends()
    ) -> bool | str:
        if request:
            with suppress(
                firebase_auth.ExpiredIdTokenError,
                firebase_auth.RevokedIdTokenError,
                firebase_auth.InvalidIdTokenError,
                firebase_auth.ExpiredSessionCookieError,
            ):
                session_cookie = request.session.get(config.auth.token_id)
                if session_cookie:
                    self.user_data = firebase_auth.verify_session_cookie(
                        session_cookie, check_revoked=True
                    )
        return self.identity or False


class Auth(AuthBase):
    secret_key: SecretStr
    _current_user: ContextVar[t.Any] = ContextVar("current_user", default=CurrentUser())

    def __init__(
        self,
        secret_key: SecretStr = SecretStr("secret"),
        user_model: t.Optional[SQLModel] = None,
    ) -> None:
        super().__init__(secret_key, user_model)
        self.secret_key = secret_key or self.config.app.secret_key
        self.name = "firebase"
        self.user_model = user_model

    async def init(self) -> None:
        global firebase_app
        firebase_options: dict[str, str | None] = dict(
            projectId=self.config.app.project
        )
        firebase_app = initialize_app(options=firebase_options)
        self.middlewares = [
            Middleware(
                SessionMiddleware,  # type: ignore
                secret_key=self.secret_key.get_secret_value(),
                session_cookie=f"{self.token_id}_admin",
                https_only=True if self.config.deployed else False,
            )
        ]

    async def login(self, request: Request) -> bool:
        id_token = request.cookies.get(self.token_id)
        if id_token:
            if self.current_user.is_authenticated(request):
                return True
            user_data = None
            with suppress(
                firebase_auth.ExpiredIdTokenError,
                firebase_auth.RevokedIdTokenError,
                firebase_auth.InvalidIdTokenError,
            ):
                user_data = firebase_auth.verify_id_token(id_token, check_revoked=True)
            debug(user_data)
            if user_data:
                self.user_model = depends.get("models").sql.Person
                sql = depends.get()
                async with sql.session as session:
                    user_query = select(self.user_model).where(  # type: ignore
                        self.user_model.gmail == user_data["email"]  # type: ignore
                        and self.user_model.is_active  # type: ignore
                        and self.user_model.is_superuser  # type: ignore
                    )
                    result = await session.execute(user_query)
                    enabled_user = result.one_or_none()
                debug(enabled_user)
                if enabled_user and (time() - user_data["auth_time"] < 5 * 6):
                    enabled_user = enabled_user[0]
                    firebase_auth.set_custom_user_claims(
                        user_data["uid"], {enabled_user.role: True}
                    )
                    enabled_user.name = user_data["name"]
                    enabled_user.google_uid = user_data["uid"]
                    enabled_user.picture = user_data["picture"]
                    await enabled_user.save()
                    expires_in = timedelta(days=14)
                    session_cookie = firebase_auth.create_session_cookie(
                        id_token, expires_in=expires_in
                    )
                    self.config.auth.session_cookie = session_cookie
                    request.session.update({self.token_id: session_cookie})
                    return True
                firebase_auth.revoke_refresh_tokens(user_data["uid"])
        request.session.pop(self.token_id, None)
        self.current_user.user_data = {}
        return False

    async def logout(self, request: Request) -> bool:
        request.session.pop(self.token_id, None)
        with suppress(
            firebase_auth.ExpiredIdTokenError,
            firebase_auth.RevokedIdTokenError,
            firebase_auth.InvalidIdTokenError,
            firebase_auth.ExpiredSessionCookieError,
            ValueError,
        ):
            id_token = request.cookies.get(self.token_id)
            user_data = firebase_auth.verify_id_token(id_token, check_revoked=True)
            firebase_auth.revoke_refresh_tokens(user_data["uid"])
        self.current_user.user_data = {}
        return True

    async def authenticate(self, request: Request) -> bool:
        return self.current_user.is_authenticated(request)


depends.set(Auth)
