import typing as t
from base64 import b64encode
from contextlib import asynccontextmanager
from time import perf_counter

from acb.adapters import get_adapter, import_adapter
from acb.config import Config
from acb.depends import depends
from fastblocks.applications import FastBlocks

from ._base import AppBase, AppBaseSettings

main_start = perf_counter()

Cache, Storage = import_adapter()  # type: ignore


class AppSettings(AppBaseSettings):
    pwa_name: str = "SplashStand"
    store_enabled: bool = False
    fontawesome_pro: bool = True
    ios_id: t.Optional[str] = None
    datetime_format: str = "MM-DD-YYYY h:mm A"
    about: str = (
        "SplashStand is a fast, simple, safe, and secure content management system."
    )
    nav_pages: list[str] = []
    social_media: list[str] = []
    favicon: str = "favicon.ico"
    icon: str = "icon.png"
    contact: dict[str, str] = dict(email="", phone="", address="")
    copyright: t.Optional[str] = None
    theme_color: str = "fff"
    bgcolor: str = "fff"
    permanent_session_lifetime: int = 2_678_400
    wtf_csrf_time_limit: int = 172_800
    roles: list[str] = ["admin", "owner", "contributor", "user"]
    media_types: list[str] = ["image", "video", "audio"]
    video_exts: list[str] = [".webm", ".m4v", ".mp4"]
    image_exts: list[str] = [".jpeg", ".jpg", ".png", ".webp"]
    audio_exts: list[str] = [".m4a", ".mp4"]
    allowed_exts: list[str] = [
        ".html",
        ".scss",
        ".json",
        ".js",
        ".xml",
        ".yml",
        ".py",
        ".ini",
        ".gz",
        ".txt",
    ]
    codemirror: t.Optional[dict[str, str]] = dict(version="5.58.3", theme="cobalt")
    fontawesome: t.Optional[dict[str, str]] = dict(version="5.15.1", kit="274806bd44")
    # ckeditor_fields: list[str] = ["text", "description", "about", "intro", "info"]
    # datetime_fields: list[str] = ["date", "published", "created", "released", "born"]
    favicon_sizes: list[str] = ["32", "128", "152", "167", "180", "192", "196"]
    icon_sizes: t.Any = dict(
        square=("120", "152", "180"),
        android=("192", "512"),
        ios=(
            ("1242x2688", "414", "896", "3"),
            ("828x1792", "414", "896", "2"),
            ("1125x2436", "375", "812", "3"),
            ("1242x2208", "414", "736", "3"),
            ("750x1334", "375", "667", "2"),
            ("2048x2732", "1024", "1366", "2"),
            ("1668x2388", "834", "1194", "2"),
            ("1668x2224", "834", "1112", "2"),
            ("1536x2048", "768", "1024", "2"),
        ),
    )
    header: dict[str, tuple[str]] = dict(
        dimensions=("1920x1080",), logo_dimensions=("1024x240",)
    )
    notification_icons: dict[str, str] = dict(
        info="info-circle",
        success="check-circle",
        danger="exclamation-circle",
        warning="exclamation-triangle",
    )
    cache_media_timeout: int = 15_768_000
    cache_media_control: str = f"max-age={cache_media_timeout} public"
    token_id: t.Optional[str] = "_ss_"

    @depends.inject
    def __init__(self, config: Config = depends(), **data: t.Any) -> None:
        super().__init__(**data)
        self.url = (
            f"https://{self.domain}" if config.deployed else "http://localhost:8000"
        )
        self.nav_pages.insert(0, "home")
        self.nav_pages = list(set(self.nav_pages))
        self.token_id = "".join(  # type: ignore
            [self.token_id, b64encode(self.name.encode()).decode().rstrip("=")]  # type: ignore
        )


class App(FastBlocks, AppBase):
    def __init__(self) -> None:
        super().__init__(lifespan=self.lifespan)

    async def init(self) -> None:
        self.templates = depends.get().app
        self.routes.extend(depends.get("routes").routes)

    async def post_startup(self) -> None:
        if not self.config.deployed:
            from aioconsole import aprint
            from pyfiglet import Figlet

            fig = Figlet(font="slant", width=90, justify="center")
            await aprint(f"\n\n{fig.renderText(self.config.app.name.upper())}\n")
        if not self.config.debug.production and self.config.deployed:
            self.logger.info("Entering production mode...")

    @asynccontextmanager
    async def lifespan(self, app: FastBlocks) -> t.AsyncIterator[None]:
        try:
            if get_adapter("admin"):
                sql = depends.get()
                auth = depends.get()
                admin = depends.get()
                admin.__init__(
                    app,
                    engine=sql.engine,
                    title=self.config.admin.title,
                    debug=self.config.debug.admin,
                    base_url=self.config.admin.url,
                    logo_url=self.config.admin.logo_url,
                    authentication_backend=auth,
                )
                self.router.routes.insert(0, self.router.routes.pop())

            await self.post_startup()
            main_start_time = perf_counter() - main_start
            self.logger.warning(f"App started in {main_start_time} s")
        except Exception as e:
            self.logger.error(f"Error during startup: {e}")
            raise e
        yield
        self.logger.critical("Application shut down")
        completer = self.logger.complete()
        await completer


depends.set(App)
