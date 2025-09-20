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
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct42Json(typing_extensions.TypedDict):
        angle: float
        cloud_color1: json_util.JsonValue
        cloud_color2: json_util.JsonValue
        add_color1: json_util.JsonValue
        add_color2: json_util.JsonValue
        cloud_scale: float
        fade_off_size: float
        open_speed: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x382a1973, 0x4c41dcd4, 0xcad5ae7a, 0x1e52124e, 0x98c660e0, 0x10c1ded2, 0xae71a22a, 0x4e29c85a)


@dataclasses.dataclass()
class UnknownStruct42(BaseProperty):
    angle: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x382a1973, original_name='Angle'
        ),
    })
    cloud_color1: Color = dataclasses.field(default_factory=lambda: Color(r=0.24705900251865387, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x4c41dcd4, original_name='CloudColor1', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    cloud_color2: Color = dataclasses.field(default_factory=lambda: Color(r=0.49803900718688965, g=0.09803900122642517, b=0.09803900122642517, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xcad5ae7a, original_name='CloudColor2', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    add_color1: Color = dataclasses.field(default_factory=lambda: Color(r=0.34902000427246094, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1e52124e, original_name='AddColor1', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    add_color2: Color = dataclasses.field(default_factory=lambda: Color(r=0.1490200012922287, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x98c660e0, original_name='AddColor2', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    cloud_scale: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x10c1ded2, original_name='CloudScale'
        ),
    })
    fade_off_size: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xae71a22a, original_name='FadeOffSize'
        ),
    })
    open_speed: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4e29c85a, original_name='OpenSpeed'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        if property_count != 8:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHffffLHffffLHffffLHffffLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(128))
        assert (dec[0], dec[3], dec[9], dec[15], dec[21], dec[27], dec[30], dec[33]) == _FAST_IDS
        return cls(
            dec[2],
            Color(*dec[5:9]),
            Color(*dec[11:15]),
            Color(*dec[17:21]),
            Color(*dec[23:27]),
            dec[29],
            dec[32],
            dec[35],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'8*\x19s')  # 0x382a1973
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.angle))

        data.write(b'LA\xdc\xd4')  # 0x4c41dcd4
        data.write(b'\x00\x10')  # size
        self.cloud_color1.to_stream(data)

        data.write(b'\xca\xd5\xaez')  # 0xcad5ae7a
        data.write(b'\x00\x10')  # size
        self.cloud_color2.to_stream(data)

        data.write(b'\x1eR\x12N')  # 0x1e52124e
        data.write(b'\x00\x10')  # size
        self.add_color1.to_stream(data)

        data.write(b'\x98\xc6`\xe0')  # 0x98c660e0
        data.write(b'\x00\x10')  # size
        self.add_color2.to_stream(data)

        data.write(b'\x10\xc1\xde\xd2')  # 0x10c1ded2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cloud_scale))

        data.write(b'\xaeq\xa2*')  # 0xae71a22a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_off_size))

        data.write(b'N)\xc8Z')  # 0x4e29c85a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.open_speed))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct42Json", data)
        return cls(
            angle=json_data['angle'],
            cloud_color1=Color.from_json(json_data['cloud_color1']),
            cloud_color2=Color.from_json(json_data['cloud_color2']),
            add_color1=Color.from_json(json_data['add_color1']),
            add_color2=Color.from_json(json_data['add_color2']),
            cloud_scale=json_data['cloud_scale'],
            fade_off_size=json_data['fade_off_size'],
            open_speed=json_data['open_speed'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'angle': self.angle,
            'cloud_color1': self.cloud_color1.to_json(),
            'cloud_color2': self.cloud_color2.to_json(),
            'add_color1': self.add_color1.to_json(),
            'add_color2': self.add_color2.to_json(),
            'cloud_scale': self.cloud_scale,
            'fade_off_size': self.fade_off_size,
            'open_speed': self.open_speed,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cloud_color1(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_cloud_color2(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_add_color1(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_add_color2(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_cloud_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_off_size(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_open_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x382a1973: ('angle', _decode_angle),
    0x4c41dcd4: ('cloud_color1', _decode_cloud_color1),
    0xcad5ae7a: ('cloud_color2', _decode_cloud_color2),
    0x1e52124e: ('add_color1', _decode_add_color1),
    0x98c660e0: ('add_color2', _decode_add_color2),
    0x10c1ded2: ('cloud_scale', _decode_cloud_scale),
    0xae71a22a: ('fade_off_size', _decode_fade_off_size),
    0x4e29c85a: ('open_speed', _decode_open_speed),
}
