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
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class TweakGui_HudColorTypedefJson(typing_extensions.TypedDict):
        energy_bar_filled_color: json_util.JsonValue
        energy_bar_empty_color: json_util.JsonValue
        energy_bar_shadow_color: json_util.JsonValue
        energy_tanks_filled_color: json_util.JsonValue
        energy_tanks_empty_color: json_util.JsonValue
        unknown_0x1fd3d43a: json_util.JsonValue
        unknown_0xe1ff2a4f: json_util.JsonValue
        unknown_0x9cfb8a36: json_util.JsonValue
        unknown_0x89a45bcb: json_util.JsonValue
        unknown_0xc2a8ccc6: json_util.JsonValue
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xacf62d93, 0x37e381c2, 0xb9a9fc6e, 0x4377e677, 0x63384f81, 0x1fd3d43a, 0xe1ff2a4f, 0x9cfb8a36, 0x89a45bcb, 0xc2a8ccc6)


@dataclasses.dataclass()
class TweakGui_HudColorTypedef(BaseProperty):
    energy_bar_filled_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xacf62d93, original_name='EnergyBarFilledColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_bar_empty_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x37e381c2, original_name='EnergyBarEmptyColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_bar_shadow_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xb9a9fc6e, original_name='EnergyBarShadowColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_tanks_filled_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x4377e677, original_name='EnergyTanksFilledColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_tanks_empty_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x63384f81, original_name='EnergyTanksEmptyColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x1fd3d43a: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1fd3d43a, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xe1ff2a4f: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xe1ff2a4f, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x9cfb8a36: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x9cfb8a36, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x89a45bcb: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x89a45bcb, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xc2a8ccc6: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xc2a8ccc6, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
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
        if property_count != 10:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffff')
    
        dec = _FAST_FORMAT.unpack(data.read(220))
        assert (dec[0], dec[6], dec[12], dec[18], dec[24], dec[30], dec[36], dec[42], dec[48], dec[54]) == _FAST_IDS
        return cls(
            Color(*dec[2:6]),
            Color(*dec[8:12]),
            Color(*dec[14:18]),
            Color(*dec[20:24]),
            Color(*dec[26:30]),
            Color(*dec[32:36]),
            Color(*dec[38:42]),
            Color(*dec[44:48]),
            Color(*dec[50:54]),
            Color(*dec[56:60]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b'\xac\xf6-\x93')  # 0xacf62d93
        data.write(b'\x00\x10')  # size
        self.energy_bar_filled_color.to_stream(data)

        data.write(b'7\xe3\x81\xc2')  # 0x37e381c2
        data.write(b'\x00\x10')  # size
        self.energy_bar_empty_color.to_stream(data)

        data.write(b'\xb9\xa9\xfcn')  # 0xb9a9fc6e
        data.write(b'\x00\x10')  # size
        self.energy_bar_shadow_color.to_stream(data)

        data.write(b'Cw\xe6w')  # 0x4377e677
        data.write(b'\x00\x10')  # size
        self.energy_tanks_filled_color.to_stream(data)

        data.write(b'c8O\x81')  # 0x63384f81
        data.write(b'\x00\x10')  # size
        self.energy_tanks_empty_color.to_stream(data)

        data.write(b'\x1f\xd3\xd4:')  # 0x1fd3d43a
        data.write(b'\x00\x10')  # size
        self.unknown_0x1fd3d43a.to_stream(data)

        data.write(b'\xe1\xff*O')  # 0xe1ff2a4f
        data.write(b'\x00\x10')  # size
        self.unknown_0xe1ff2a4f.to_stream(data)

        data.write(b'\x9c\xfb\x8a6')  # 0x9cfb8a36
        data.write(b'\x00\x10')  # size
        self.unknown_0x9cfb8a36.to_stream(data)

        data.write(b'\x89\xa4[\xcb')  # 0x89a45bcb
        data.write(b'\x00\x10')  # size
        self.unknown_0x89a45bcb.to_stream(data)

        data.write(b'\xc2\xa8\xcc\xc6')  # 0xc2a8ccc6
        data.write(b'\x00\x10')  # size
        self.unknown_0xc2a8ccc6.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGui_HudColorTypedefJson", data)
        return cls(
            energy_bar_filled_color=Color.from_json(json_data['energy_bar_filled_color']),
            energy_bar_empty_color=Color.from_json(json_data['energy_bar_empty_color']),
            energy_bar_shadow_color=Color.from_json(json_data['energy_bar_shadow_color']),
            energy_tanks_filled_color=Color.from_json(json_data['energy_tanks_filled_color']),
            energy_tanks_empty_color=Color.from_json(json_data['energy_tanks_empty_color']),
            unknown_0x1fd3d43a=Color.from_json(json_data['unknown_0x1fd3d43a']),
            unknown_0xe1ff2a4f=Color.from_json(json_data['unknown_0xe1ff2a4f']),
            unknown_0x9cfb8a36=Color.from_json(json_data['unknown_0x9cfb8a36']),
            unknown_0x89a45bcb=Color.from_json(json_data['unknown_0x89a45bcb']),
            unknown_0xc2a8ccc6=Color.from_json(json_data['unknown_0xc2a8ccc6']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'energy_bar_filled_color': self.energy_bar_filled_color.to_json(),
            'energy_bar_empty_color': self.energy_bar_empty_color.to_json(),
            'energy_bar_shadow_color': self.energy_bar_shadow_color.to_json(),
            'energy_tanks_filled_color': self.energy_tanks_filled_color.to_json(),
            'energy_tanks_empty_color': self.energy_tanks_empty_color.to_json(),
            'unknown_0x1fd3d43a': self.unknown_0x1fd3d43a.to_json(),
            'unknown_0xe1ff2a4f': self.unknown_0xe1ff2a4f.to_json(),
            'unknown_0x9cfb8a36': self.unknown_0x9cfb8a36.to_json(),
            'unknown_0x89a45bcb': self.unknown_0x89a45bcb.to_json(),
            'unknown_0xc2a8ccc6': self.unknown_0xc2a8ccc6.to_json(),
        }


def _decode_energy_bar_filled_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_bar_empty_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_bar_shadow_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_tanks_filled_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_tanks_empty_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x1fd3d43a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xe1ff2a4f(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x9cfb8a36(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x89a45bcb(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xc2a8ccc6(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xacf62d93: ('energy_bar_filled_color', _decode_energy_bar_filled_color),
    0x37e381c2: ('energy_bar_empty_color', _decode_energy_bar_empty_color),
    0xb9a9fc6e: ('energy_bar_shadow_color', _decode_energy_bar_shadow_color),
    0x4377e677: ('energy_tanks_filled_color', _decode_energy_tanks_filled_color),
    0x63384f81: ('energy_tanks_empty_color', _decode_energy_tanks_empty_color),
    0x1fd3d43a: ('unknown_0x1fd3d43a', _decode_unknown_0x1fd3d43a),
    0xe1ff2a4f: ('unknown_0xe1ff2a4f', _decode_unknown_0xe1ff2a4f),
    0x9cfb8a36: ('unknown_0x9cfb8a36', _decode_unknown_0x9cfb8a36),
    0x89a45bcb: ('unknown_0x89a45bcb', _decode_unknown_0x89a45bcb),
    0xc2a8ccc6: ('unknown_0xc2a8ccc6', _decode_unknown_0xc2a8ccc6),
}
