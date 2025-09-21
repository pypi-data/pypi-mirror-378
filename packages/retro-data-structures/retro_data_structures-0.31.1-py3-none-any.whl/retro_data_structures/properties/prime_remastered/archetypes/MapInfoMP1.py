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
import uuid

if typing.TYPE_CHECKING:
    class MapInfoMP1Json(typing_extensions.TypedDict):
        unk_int_1: int
        unk_int_2: int
        unk_guid: str
    

def _from_json_unk_guid(data: json_util.JsonValue) -> AssetId:
    json_data = typing.cast(str, data)
    return uuid.UUID(json_data)


def _to_json_unk_guid(obj: AssetId) -> json_util.JsonValue:
    return str(obj)


@dataclasses.dataclass()
class MapInfoMP1(BaseProperty):
    unk_int_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x70f8474b, original_name='Unk Int 1'
        ),
    })
    unk_int_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9caf8d12, original_name='Unk Int 2'
        ),
    })
    unk_guid: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x91a53221, original_name='Unk GUID', from_json=_from_json_unk_guid, to_json=_to_json_unk_guid
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
        assert property_id == 0x70f8474b
        unk_int_1 = struct.unpack('<l', data.read(4))[0]
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0x9caf8d12
        unk_int_2 = struct.unpack('<l', data.read(4))[0]
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0x91a53221
        unk_guid = uuid.UUID(bytes_le=data.read(16))
    
        return cls(unk_int_1, unk_int_2, unk_guid)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x00')  # 0 properties
        num_properties_written = 0

        if self.unk_int_1 != default_override.get('unk_int_1', 0):
            num_properties_written += 1
            data.write(b'KG\xf8p')  # 0x70f8474b
            data.write(b'\x04\x00')  # size
            data.write(struct.pack('<l', self.unk_int_1))

        if self.unk_int_2 != default_override.get('unk_int_2', 0):
            num_properties_written += 1
            data.write(b'\x12\x8d\xaf\x9c')  # 0x9caf8d12
            data.write(b'\x04\x00')  # size
            data.write(struct.pack('<l', self.unk_int_2))

        if self.unk_guid != default_override.get('unk_guid', default_asset_id):
            num_properties_written += 1
            data.write(b'!2\xa5\x91')  # 0x91a53221
            data.write(b'\x10\x00')  # size
            data.write(self.unk_guid.bytes_le)

        if num_properties_written != 0:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack("<H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MapInfoMP1Json", data)
        return cls(
            unk_int_1=json_data['unk_int_1'],
            unk_int_2=json_data['unk_int_2'],
            unk_guid=uuid.UUID(json_data['unk_guid']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unk_int_1': self.unk_int_1,
            'unk_int_2': self.unk_int_2,
            'unk_guid': str(self.unk_guid),
        }


def _decode_unk_int_1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('<l', data.read(4))[0]


def _decode_unk_int_2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('<l', data.read(4))[0]


def _decode_unk_guid(data: typing.BinaryIO, property_size: int) -> AssetId:
    return uuid.UUID(bytes_le=data.read(16))


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x70f8474b: ('unk_int_1', _decode_unk_int_1),
    0x9caf8d12: ('unk_int_2', _decode_unk_int_2),
    0x91a53221: ('unk_guid', _decode_unk_guid),
}
