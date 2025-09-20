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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class ScannableParametersJson(typing_extensions.TypedDict):
        scannable_info0: int
        max_scannable_distance: float
        priority: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xb94e9be7, 0xff4ae2ec, 0x42087650)


@dataclasses.dataclass()
class ScannableParameters(BaseProperty):
    scannable_info0: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['SCAN'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb94e9be7, original_name='ScannableInfo0'
        ),
    })
    max_scannable_distance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xff4ae2ec, original_name='MaxScannableDistance'
        ),
    })
    priority: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x42087650, original_name='Priority'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack(">LH", data.read(6))
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHQLHfLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(34))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\xb9N\x9b\xe7')  # 0xb94e9be7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.scannable_info0))

        data.write(b'\xffJ\xe2\xec')  # 0xff4ae2ec
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_scannable_distance))

        data.write(b'B\x08vP')  # 0x42087650
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.priority))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ScannableParametersJson", data)
        return cls(
            scannable_info0=json_data['scannable_info0'],
            max_scannable_distance=json_data['max_scannable_distance'],
            priority=json_data['priority'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'scannable_info0': self.scannable_info0,
            'max_scannable_distance': self.max_scannable_distance,
            'priority': self.priority,
        }


def _decode_scannable_info0(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_max_scannable_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_priority(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb94e9be7: ('scannable_info0', _decode_scannable_info0),
    0xff4ae2ec: ('max_scannable_distance', _decode_max_scannable_distance),
    0x42087650: ('priority', _decode_priority),
}
