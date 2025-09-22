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
    class TweakGui_Misc_UnknownStruct1Json(typing_extensions.TypedDict):
        unknown_0xe7c4becd: float
        unknown_0xbaa1b7c1: float
        unknown_0x3b8d9a8e: float
        unknown_0xbd735f69: float
        unknown_0x5ad522c2: float
        unknown_0x4358b0f1: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xe7c4becd, 0xbaa1b7c1, 0x3b8d9a8e, 0xbd735f69, 0x5ad522c2, 0x4358b0f1)


@dataclasses.dataclass()
class TweakGui_Misc_UnknownStruct1(BaseProperty):
    unknown_0xe7c4becd: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe7c4becd, original_name='Unknown'
        ),
    })
    unknown_0xbaa1b7c1: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbaa1b7c1, original_name='Unknown'
        ),
    })
    unknown_0x3b8d9a8e: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3b8d9a8e, original_name='Unknown'
        ),
    })
    unknown_0xbd735f69: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbd735f69, original_name='Unknown'
        ),
    })
    unknown_0x5ad522c2: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5ad522c2, original_name='Unknown'
        ),
    })
    unknown_0x4358b0f1: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4358b0f1, original_name='Unknown'
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
        if property_count != 6:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(60))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'\xe7\xc4\xbe\xcd')  # 0xe7c4becd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe7c4becd))

        data.write(b'\xba\xa1\xb7\xc1')  # 0xbaa1b7c1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbaa1b7c1))

        data.write(b';\x8d\x9a\x8e')  # 0x3b8d9a8e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3b8d9a8e))

        data.write(b'\xbds_i')  # 0xbd735f69
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbd735f69))

        data.write(b'Z\xd5"\xc2')  # 0x5ad522c2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5ad522c2))

        data.write(b'CX\xb0\xf1')  # 0x4358b0f1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4358b0f1))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGui_Misc_UnknownStruct1Json", data)
        return cls(
            unknown_0xe7c4becd=json_data['unknown_0xe7c4becd'],
            unknown_0xbaa1b7c1=json_data['unknown_0xbaa1b7c1'],
            unknown_0x3b8d9a8e=json_data['unknown_0x3b8d9a8e'],
            unknown_0xbd735f69=json_data['unknown_0xbd735f69'],
            unknown_0x5ad522c2=json_data['unknown_0x5ad522c2'],
            unknown_0x4358b0f1=json_data['unknown_0x4358b0f1'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xe7c4becd': self.unknown_0xe7c4becd,
            'unknown_0xbaa1b7c1': self.unknown_0xbaa1b7c1,
            'unknown_0x3b8d9a8e': self.unknown_0x3b8d9a8e,
            'unknown_0xbd735f69': self.unknown_0xbd735f69,
            'unknown_0x5ad522c2': self.unknown_0x5ad522c2,
            'unknown_0x4358b0f1': self.unknown_0x4358b0f1,
        }


def _decode_unknown_0xe7c4becd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbaa1b7c1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3b8d9a8e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbd735f69(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5ad522c2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4358b0f1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xe7c4becd: ('unknown_0xe7c4becd', _decode_unknown_0xe7c4becd),
    0xbaa1b7c1: ('unknown_0xbaa1b7c1', _decode_unknown_0xbaa1b7c1),
    0x3b8d9a8e: ('unknown_0x3b8d9a8e', _decode_unknown_0x3b8d9a8e),
    0xbd735f69: ('unknown_0xbd735f69', _decode_unknown_0xbd735f69),
    0x5ad522c2: ('unknown_0x5ad522c2', _decode_unknown_0x5ad522c2),
    0x4358b0f1: ('unknown_0x4358b0f1', _decode_unknown_0x4358b0f1),
}
