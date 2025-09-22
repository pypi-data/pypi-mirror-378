from acb.config import Config
from acb.depends import depends

from ._base import PwaBase, PwaBaseSettings


class PwaSettings(PwaBaseSettings): ...


class Pwa(PwaBase):
    @depends.inject
    async def init(self, config: Config = depends()) -> None:
        self.manifest = config.pwa.model_dump()


depends.set(Pwa)
