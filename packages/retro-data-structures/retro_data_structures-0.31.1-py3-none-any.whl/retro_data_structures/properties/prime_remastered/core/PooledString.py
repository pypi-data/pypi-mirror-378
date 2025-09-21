# Generated file
import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from .AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class PooledStringJson(typing_extensions.TypedDict):
        index: int
        size_or_str: int | str


@dataclasses.dataclass()
class PooledString(BaseProperty):
    index: int = -1
    size_or_str: int | bytes = b""

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        a, b = struct.unpack('<lL', data.read(8))
        if a == -1:
            b = data.read(b)
        return cls(a, b)

    def to_stream(self, data: typing.BinaryIO) -> None:
        a, b = self.index, self.size_or_str
        if a == -1:
            assert isinstance(b, bytes)
            b = len(b)
        data.write(struct.pack('<lL', a, b))
        if a == -1:
            assert isinstance(self.size_or_str, bytes)
            data.write(self.size_or_str)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PooledStringJson", data)
        if isinstance(json_data["size_or_str"], str):
            size_or_str: int | bytes = json_data["size_or_str"].encode('utf-8')
        else:
            size_or_str = json_data["size_or_str"]
        return cls(json_data["index"], size_or_str)

    def to_json(self) -> json_util.JsonObject:
        if isinstance(self.size_or_str, bytes):
            size_or_str: int | str = self.size_or_str.decode('utf-8')
        else:
            size_or_str = self.size_or_str
        return {
            "index": self.index,
            "size_or_str": size_or_str,
        }

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME_REMASTER
