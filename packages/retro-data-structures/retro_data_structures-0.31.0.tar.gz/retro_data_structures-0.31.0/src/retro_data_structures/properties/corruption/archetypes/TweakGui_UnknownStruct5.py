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
    class TweakGui_UnknownStruct5Json(typing_extensions.TypedDict):
        position_percent: float
        texcoord_percent: float
        alpha_percent: float
        color_percent: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x7be14ee3, 0xf2f3f939, 0x4e324158, 0xde513312)


@dataclasses.dataclass()
class TweakGui_UnknownStruct5(BaseProperty):
    position_percent: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7be14ee3, original_name='PositionPercent'
        ),
    })
    texcoord_percent: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf2f3f939, original_name='TexcoordPercent'
        ),
    })
    alpha_percent: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4e324158, original_name='AlphaPercent'
        ),
    })
    color_percent: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xde513312, original_name='ColorPercent'
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
        if property_count != 4:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(40))
        assert (dec[0], dec[3], dec[6], dec[9]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'{\xe1N\xe3')  # 0x7be14ee3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.position_percent))

        data.write(b'\xf2\xf3\xf99')  # 0xf2f3f939
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.texcoord_percent))

        data.write(b'N2AX')  # 0x4e324158
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alpha_percent))

        data.write(b'\xdeQ3\x12')  # 0xde513312
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.color_percent))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGui_UnknownStruct5Json", data)
        return cls(
            position_percent=json_data['position_percent'],
            texcoord_percent=json_data['texcoord_percent'],
            alpha_percent=json_data['alpha_percent'],
            color_percent=json_data['color_percent'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'position_percent': self.position_percent,
            'texcoord_percent': self.texcoord_percent,
            'alpha_percent': self.alpha_percent,
            'color_percent': self.color_percent,
        }


def _decode_position_percent(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_texcoord_percent(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_alpha_percent(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_color_percent(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7be14ee3: ('position_percent', _decode_position_percent),
    0xf2f3f939: ('texcoord_percent', _decode_texcoord_percent),
    0x4e324158: ('alpha_percent', _decode_alpha_percent),
    0xde513312: ('color_percent', _decode_color_percent),
}
