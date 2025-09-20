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

if typing.TYPE_CHECKING:
    class VectorMP1Json(typing_extensions.TypedDict):
        x: float
        y: float
        z: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x2649e551, 0xd2bb5bc6, 0x7f9499b2)


@dataclasses.dataclass()
class VectorMP1(BaseProperty):
    x: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2649e551, original_name='x'
        ),
    })
    y: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd2bb5bc6, original_name='y'
        ),
    })
    z: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7f9499b2, original_name='z'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('<LHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(30))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x00')  # 0 properties
        num_properties_written = 0

        if self.x != default_override.get('x', 0.0):
            num_properties_written += 1
            data.write(b'Q\xe5I&')  # 0x2649e551
            data.write(b'\x04\x00')  # size
            data.write(struct.pack('<f', self.x))

        if self.y != default_override.get('y', 0.0):
            num_properties_written += 1
            data.write(b'\xc6[\xbb\xd2')  # 0xd2bb5bc6
            data.write(b'\x04\x00')  # size
            data.write(struct.pack('<f', self.y))

        if self.z != default_override.get('z', 0.0):
            num_properties_written += 1
            data.write(b'\xb2\x99\x94\x7f')  # 0x7f9499b2
            data.write(b'\x04\x00')  # size
            data.write(struct.pack('<f', self.z))

        if num_properties_written != 0:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack("<H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("VectorMP1Json", data)
        return cls(
            x=json_data['x'],
            y=json_data['y'],
            z=json_data['z'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
        }


def _decode_x(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('<f', data.read(4))[0]


def _decode_y(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('<f', data.read(4))[0]


def _decode_z(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('<f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2649e551: ('x', _decode_x),
    0xd2bb5bc6: ('y', _decode_y),
    0x7f9499b2: ('z', _decode_z),
}
