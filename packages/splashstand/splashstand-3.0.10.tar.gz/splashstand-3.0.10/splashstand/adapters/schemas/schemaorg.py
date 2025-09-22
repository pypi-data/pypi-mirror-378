import asyncio
import csv
import re
import typing as t
from contextlib import suppress

from acb.adapters import import_adapter
from acb.config import Config
from acb.debug import debug
from acb.depends import depends
from acb.logger import Logger
from inflection import underscore

from ._base import SchemasBase, SchemasBaseSettings

Cache, Requests = import_adapter()  # type: ignore

latest_url = "https://schema.org/version/latest/"
data_url = "https://github.com/schemaorg/schemaorg/tree/main/data/releases"


def strip_url(url: str) -> str:
    return url.strip().removeprefix("https://schema.org/")


class SchemasSettings(SchemasBaseSettings):
    version: t.Optional[str] = "29.0"


class SchemaOrg:
    config: Config = depends()
    logger: Logger = depends()
    requests: Requests = depends()

    def __init__(
        self,
        schema_type: str,
        base: str | None = None,
    ) -> None:
        self.type: str = schema_type
        self.loaded: dict[str, t.Any] = {}
        self.properties: dict[str, str] = {}
        self._properties: dict[str, dict[str, t.Any]] = {}
        self.type_spec: dict[str, t.Any] = {}
        self._set_base(base)
        self._set_version()
        self.load_type(schema_type)
        self.url: str | None = None
        self._set_type(schema_type)

    def __str__(self) -> str:
        return self.type

    def __repr__(self) -> str:
        return self.__str__()

    def _set_base(self, base: str | None) -> None:
        if base is None:
            base = "https://www.schema.org"
        if not re.search("^http", base):
            self.logger.error(f"{base} must be a valid URL starting with http or https")
        self.base = base

    @depends.inject
    def _set_version(self, requests: Requests = depends()) -> None:
        resp = asyncio.run(requests.get(data_url, timeout=5))
        self.version = max(re.findall(r"/(\d\d\.\d)", resp.text), default="0.0")

    @depends.inject
    async def read_csv(
        self,
        url: str,
        header: list[str] | None = None,
        keyfield: str | None = None,
    ) -> dict[str, str] | list[str]:
        data = []
        if keyfield is not None:
            data = {}
        csv_file = (await self.requests.get(url)).text.splitlines()
        if header is None:
            header = next(csv.reader(csv_file))
        csv_reader = csv.DictReader(csv_file, fieldnames=header)
        for row in csv_reader:
            if isinstance(data, dict):
                data[row[keyfield]] = row
            else:
                data.append(row)
        return data

    async def read_properties_csv(
        self, keyfield: str = "id"
    ) -> dict[str, str] | list[str]:
        url = f"{latest_url}/schemaorg-current-https-properties.csv"
        return await self.read_csv(url, keyfield=keyfield)

    async def read_types_csv(
        self, keyfield: str = "label"
    ) -> dict[str, str] | list[str]:
        url = f"{latest_url}/schemaorg-current-https-types.csv"
        return await self.read_csv(url, keyfield=keyfield)

    async def find_similar_types(self, term: str | None) -> list[str] | None:
        if term:
            typs = await self.read_types_csv()
            term = term.split("/")[-1].lower()
            return [x for x in typs if term in x.lower()]

    def add_property(self, name: str, value: t.Any) -> None:
        if value not in ("", None, [], ()) and name in self._properties:
            self.properties[name] = value
            self.logger.debug(f"{name} set to {value}")

    def remove_property(self, name: str) -> None:
        if name.lower() in self.properties:
            del self.properties[name.lower()]

    def load_type(self, schema_type: str) -> None:
        asyncio.run(self._load_type(schema_type))
        asyncio.run(self._load_props())
        self._load_attributes()

    async def _load_custom_props(
        self, key: str = "mapping", field: str = "property"
    ) -> None:
        lookup = await self.read_properties_csv()
        props: list[dict[str, t.Any]] = self.loaded.get(key, [])
        for prop in props:
            name = f"https://schema.org/{prop[field]}"
            self._properties[prop[field]] = {}
            prop = {k: v for k, v in prop.items() if v}
            if name in lookup:
                self._properties[prop[field]].update(lookup[name])  # type: ignore
            self._properties[prop[field]].update(prop)
        self.logger.debug(f"{self.type}: found {len(self._properties)} properties")

    async def _load_props(self) -> None:
        lookup = await self.read_properties_csv()
        with suppress(AttributeError):
            if "properties" in self.type_spec:
                props = self.type_spec["properties"].split(",")
                props = [p.strip() for p in props]
                for prop in props:
                    if prop in lookup:
                        prop_data = lookup[prop]
                        label = prop_data.get("label")  # type: ignore
                        if label:
                            self._properties[label] = prop_data  # type: ignore
                self.logger.debug(
                    f"{self.type}: found {len(self._properties)} properties"
                )

    async def _load_type(self, schema_type: str) -> None:
        typs: t.Union[
            dict[str, dict[str, t.Any]], dict[str, str], list[str]
        ] = await self.read_types_csv()
        if isinstance(typs, dict):
            if schema_type not in typs:
                self.logger.error(f"{schema_type} is not a valid type!")
                await self.print_similar_types(schema_type)
                return
            type_spec = typs.get(self.type)
            if isinstance(type_spec, dict):
                self.type_spec = type_spec
            else:
                self.logger.error(
                    f"Type specification for {self.type} is not a valid dictionary."
                )
        else:
            self.logger.error(
                f"Unexpected type returned from read_types_csv: {type(typs)}"
            )

    def _set_type(self, schema_type: str) -> None:
        self.type = schema_type
        self.url = "/".join([self.base, self.type])

    def _load_attributes(self) -> None:
        with suppress(AttributeError):
            for attr in list(self.type_spec.keys()):
                if attr != "properties":
                    setattr(self, attr, self.type_spec[attr])

    async def print_similar_types(self, schema_type: str | None = None) -> None:
        contenders = await self.find_similar_types(schema_type or self.type)
        if contenders:
            self.logger.debug("Did you mean:")
            self.logger.debug("\n\t".join(contenders))


class Schema:
    _name: str
    _schema: t.Optional[SchemaOrg] = None
    _table_name: t.Optional[str] = None
    _help: t.Optional[str] = None
    _version: t.Optional[str] = None
    _properties: t.Optional[dict[str, t.Any]] = None

    def __init__(self, name: str, /, **data: t.Any) -> None:
        super().__init__(**data)
        self._name = name
        self._table_name = underscore(name)
        self._schema = SchemaOrg(name)
        self._help = getattr(self._schema, "comment", None)
        self._version = self._schema.version
        self._properties = {
            underscore(k): v for k, v in self._schema._properties.items()
        }

    @property
    @depends.inject
    async def _types(
        self, cache: Cache = depends()
    ) -> t.AsyncGenerator["Schema", None]:
        sub_types = getattr(self._schema, "subTypes", None)
        types = []
        if sub_types:
            types = [strip_url(t) for t in sub_types.split(",")]
        for _type in set(types):
            cache_key = f"schemas:{underscore(_type)}"
            schema = await cache.get(cache_key)
            if not schema:
                schema = Schema(_type)
                await cache.set(cache_key, schema)
            yield schema
            _sub_types = {x async for x in schema._types}
            for _sub_schema in _sub_types:
                setattr(self, _sub_schema._table_name, _sub_schema)
                yield _sub_schema

    @property
    def _fields(self) -> dict[str, list[str]]:
        fields = {
            field: [strip_url(u) for u in props["rangeIncludes"].split(",")]
            for field, props in self._properties.items()
        }
        return fields


class Schemas(SchemasBase):
    thing: t.Optional[Schema] = None

    @depends.inject
    async def init(self, cache: Cache = depends()) -> None:
        if self.config.debug.schemas and self.config.debug.cache:
            await cache.clear("schemas")
        self.thing = await cache.get("schemas:thing")
        if not self.thing:
            self.thing = Schema("Thing")
            await cache.set("schemas:thing", self.thing)
        async for _schema in self.thing._types:
            setattr(self, _schema._table_name, _schema)
        debug(self.thing._fields)


depends.set(Schemas)
