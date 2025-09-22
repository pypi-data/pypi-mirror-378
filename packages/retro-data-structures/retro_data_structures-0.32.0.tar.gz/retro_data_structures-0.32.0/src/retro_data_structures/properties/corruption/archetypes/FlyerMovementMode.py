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
    class FlyerMovementModeJson(typing_extensions.TypedDict):
        speed: float
        acceleration: float
        turn_rate: float
        facing_turn_rate: float
        turn_threshold: float
        use_avoidance: bool
        avoidance_range: float
        unknown: float
        height_variation_max: float
        height_variation_min: float
        floor_buffer: float
        ceiling_buffer: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x6392404e, 0x39fb7978, 0xe34dc703, 0x6c6426c8, 0xc0ac271e, 0x9699fa45, 0x50a9bd0d, 0x1a7b77ab, 0xdcd1597d, 0x3ab1f69c, 0x6581358c, 0x115bb38c)


@dataclasses.dataclass()
class FlyerMovementMode(BaseProperty):
    speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    acceleration: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x39fb7978, original_name='Acceleration'
        ),
    })
    turn_rate: float = dataclasses.field(default=1080.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe34dc703, original_name='TurnRate'
        ),
    })
    facing_turn_rate: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6c6426c8, original_name='FacingTurnRate'
        ),
    })
    turn_threshold: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc0ac271e, original_name='TurnThreshold'
        ),
    })
    use_avoidance: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x9699fa45, original_name='UseAvoidance'
        ),
    })
    avoidance_range: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x50a9bd0d, original_name='AvoidanceRange'
        ),
    })
    unknown: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1a7b77ab, original_name='Unknown'
        ),
    })
    height_variation_max: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdcd1597d, original_name='HeightVariationMax'
        ),
    })
    height_variation_min: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3ab1f69c, original_name='HeightVariationMin'
        ),
    })
    floor_buffer: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6581358c, original_name='FloorBuffer'
        ),
    })
    ceiling_buffer: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x115bb38c, original_name='CeilingBuffer'
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
        if property_count != 12:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLH?LHfLHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(117))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
            dec[26],
            dec[29],
            dec[32],
            dec[35],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'9\xfbyx')  # 0x39fb7978
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.acceleration))

        data.write(b'\xe3M\xc7\x03')  # 0xe34dc703
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_rate))

        data.write(b'ld&\xc8')  # 0x6c6426c8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.facing_turn_rate))

        data.write(b"\xc0\xac'\x1e")  # 0xc0ac271e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_threshold))

        data.write(b'\x96\x99\xfaE')  # 0x9699fa45
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_avoidance))

        data.write(b'P\xa9\xbd\r')  # 0x50a9bd0d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.avoidance_range))

        data.write(b'\x1a{w\xab')  # 0x1a7b77ab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'\xdc\xd1Y}')  # 0xdcd1597d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.height_variation_max))

        data.write(b':\xb1\xf6\x9c')  # 0x3ab1f69c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.height_variation_min))

        data.write(b'e\x815\x8c')  # 0x6581358c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.floor_buffer))

        data.write(b'\x11[\xb3\x8c')  # 0x115bb38c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ceiling_buffer))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("FlyerMovementModeJson", data)
        return cls(
            speed=json_data['speed'],
            acceleration=json_data['acceleration'],
            turn_rate=json_data['turn_rate'],
            facing_turn_rate=json_data['facing_turn_rate'],
            turn_threshold=json_data['turn_threshold'],
            use_avoidance=json_data['use_avoidance'],
            avoidance_range=json_data['avoidance_range'],
            unknown=json_data['unknown'],
            height_variation_max=json_data['height_variation_max'],
            height_variation_min=json_data['height_variation_min'],
            floor_buffer=json_data['floor_buffer'],
            ceiling_buffer=json_data['ceiling_buffer'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'speed': self.speed,
            'acceleration': self.acceleration,
            'turn_rate': self.turn_rate,
            'facing_turn_rate': self.facing_turn_rate,
            'turn_threshold': self.turn_threshold,
            'use_avoidance': self.use_avoidance,
            'avoidance_range': self.avoidance_range,
            'unknown': self.unknown,
            'height_variation_max': self.height_variation_max,
            'height_variation_min': self.height_variation_min,
            'floor_buffer': self.floor_buffer,
            'ceiling_buffer': self.ceiling_buffer,
        }


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_facing_turn_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_use_avoidance(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_avoidance_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_height_variation_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_height_variation_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_floor_buffer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ceiling_buffer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6392404e: ('speed', _decode_speed),
    0x39fb7978: ('acceleration', _decode_acceleration),
    0xe34dc703: ('turn_rate', _decode_turn_rate),
    0x6c6426c8: ('facing_turn_rate', _decode_facing_turn_rate),
    0xc0ac271e: ('turn_threshold', _decode_turn_threshold),
    0x9699fa45: ('use_avoidance', _decode_use_avoidance),
    0x50a9bd0d: ('avoidance_range', _decode_avoidance_range),
    0x1a7b77ab: ('unknown', _decode_unknown),
    0xdcd1597d: ('height_variation_max', _decode_height_variation_max),
    0x3ab1f69c: ('height_variation_min', _decode_height_variation_min),
    0x6581358c: ('floor_buffer', _decode_floor_buffer),
    0x115bb38c: ('ceiling_buffer', _decode_ceiling_buffer),
}
