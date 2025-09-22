import typing as t

from acb.config import AdapterBase, Settings
from pydantic import SecretStr


class CaptchaBaseSettings(Settings):
    production_key: t.Optional[SecretStr] = None
    dev_key: t.Optional[SecretStr] = None
    threshold: float = 0.5


class CaptchaBase(AdapterBase): ...
