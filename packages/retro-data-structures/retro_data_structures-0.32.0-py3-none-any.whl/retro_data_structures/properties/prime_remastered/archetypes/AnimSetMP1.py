# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.prime_remastered.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime_remastered.core.PooledString import PooledString
import uuid

if typing.TYPE_CHECKING:
    class AnimSetMP1Json(typing_extensions.TypedDict):
        id: str
        str1: json_util.JsonObject
        str2: json_util.JsonObject
    

def _from_json_id(data: json_util.JsonValue) -> AssetId:
    json_data = typing.cast(str, data)
    return uuid.UUID(json_data)


def _to_json_id(obj: AssetId) -> json_util.JsonValue:
    return str(obj)


@dataclasses.dataclass()
class AnimSetMP1(BaseProperty):
    id: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa589d885, original_name='id', from_json=_from_json_id, to_json=_to_json_id
        ),
    })
    str1: PooledString = dataclasses.field(default_factory=PooledString, metadata={
        'reflection': FieldReflection[PooledString](
            PooledString, id=0xd6f0c0f0, original_name='str1', from_json=PooledString.from_json, to_json=PooledString.to_json
        ),
    })
    str2: PooledString = dataclasses.field(default_factory=PooledString, metadata={
        'reflection': FieldReflection[PooledString](
            PooledString, id=0x87c03a01, original_name='str2', from_json=PooledString.from_json, to_json=PooledString.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME_REMASTER

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack("<H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack("<LH", data.read(6))
            start = data.tell()
            try:
                property_name, decoder = _property_decoder[property_id]
                present_fields[property_name] = decoder(data, property_size)
            except KeyError:
                raise RuntimeError(f"Unknown property: 0x{property_id:08x}")
            assert data.tell() - start == property_size

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0xa589d885
        id = uuid.UUID(bytes_le=data.read(16))
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0xd6f0c0f0
        str1 = PooledString.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0x87c03a01
        str2 = PooledString.from_stream(data, property_size)
    
        return cls(id, str1, str2)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x00')  # 0 properties
        num_properties_written = 0

        if self.id != default_override.get('id', default_asset_id):
            num_properties_written += 1
            data.write(b'\x85\xd8\x89\xa5')  # 0xa589d885
            data.write(b'\x10\x00')  # size
            data.write(self.id.bytes_le)

        if self.str1 != default_override.get('str1', PooledString()):
            num_properties_written += 1
            data.write(b'\xf0\xc0\xf0\xd6')  # 0xd6f0c0f0
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.str1.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack("<H", after - before - 2))
            data.seek(after)

        if self.str2 != default_override.get('str2', PooledString()):
            num_properties_written += 1
            data.write(b'\x01:\xc0\x87')  # 0x87c03a01
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.str2.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack("<H", after - before - 2))
            data.seek(after)

        if num_properties_written != 0:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack("<H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AnimSetMP1Json", data)
        return cls(
            id=uuid.UUID(json_data['id']),
            str1=PooledString.from_json(json_data['str1']),
            str2=PooledString.from_json(json_data['str2']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'id': str(self.id),
            'str1': self.str1.to_json(),
            'str2': self.str2.to_json(),
        }


def _decode_id(data: typing.BinaryIO, property_size: int) -> AssetId:
    return uuid.UUID(bytes_le=data.read(16))


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xa589d885: ('id', _decode_id),
    0xd6f0c0f0: ('str1', PooledString.from_stream),
    0x87c03a01: ('str2', PooledString.from_stream),
}
