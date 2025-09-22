from acb.config import AdapterBase, Settings


class AdminBaseSettings(Settings):
    style: str = "bootstrap"
    theme: str = "light"
    title: str = "SplashStand Dashboard"


class AdminBase(AdapterBase): ...
