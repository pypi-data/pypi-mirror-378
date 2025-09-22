import typing as t

from acb.config import AdapterBase, Settings


class PwaBaseSettings(Settings):
    name: str = "Splashstand"
    short_name: str = "Splashstand"
    description: str = "Splashstand"
    start_url: str = "/"
    scope: str = "/"
    lang: str = "en-US"
    display: str = "standalone"
    orientation: str = "portrait"
    background_color: str = "#fff"
    theme_color: str = "#fff"
    prefer_related_applications: bool = True
    related_applications: list[dict[str, str]] = [
        {"platform": "play", "id": "com.app.path"}
    ]
    icons: list[dict[str, str]] = [
        {"src": "/media/icon-192x192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "/media/icon-512x512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "/media/icon-1024x1024.png", "sizes": "512x512", "type": "image/png"},
        {"src": "/media/icon-384x384.png", "sizes": "512x512", "type": "image/png"},
    ]


class PwaProtocol(t.Protocol):
    manifest: dict[str, str | bool]


class PwaBase(AdapterBase):
    manifest: dict[str, str | bool] = {}
