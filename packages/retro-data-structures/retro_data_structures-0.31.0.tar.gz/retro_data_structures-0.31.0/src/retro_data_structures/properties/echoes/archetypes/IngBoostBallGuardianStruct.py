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
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class IngBoostBallGuardianStructJson(typing_extensions.TypedDict):
        unknown_0x25d02bc5: float
        unknown_0xabe99de0: float
        unknown_0xe2b23f03: float
        unknown_0x2f845006: float
        unknown_0x5d1626fb: float
        unknown_0xbb76891a: float
        unknown_0x285d67ad: int
        unknown_0x6d5f242f: int
        unknown_0xe3ff2ed6: int
        unknown_0xa6fd6d54: int
        unknown_0xecb314b6: int
        unknown_0xa9b15734: int
        locomotion_speed_scale: float
        ing_spot_speed_scale: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x25d02bc5, 0xabe99de0, 0xe2b23f03, 0x2f845006, 0x5d1626fb, 0xbb76891a, 0x285d67ad, 0x6d5f242f, 0xe3ff2ed6, 0xa6fd6d54, 0xecb314b6, 0xa9b15734, 0x1213a7d4, 0xc19ed897)


@dataclasses.dataclass()
class IngBoostBallGuardianStruct(BaseProperty):
    unknown_0x25d02bc5: float = dataclasses.field(default=1.7999999523162842, metadata={
        'reflection': FieldReflection[float](
            float, id=0x25d02bc5, original_name='Unknown'
        ),
    })
    unknown_0xabe99de0: float = dataclasses.field(default=1.7999999523162842, metadata={
        'reflection': FieldReflection[float](
            float, id=0xabe99de0, original_name='Unknown'
        ),
    })
    unknown_0xe2b23f03: float = dataclasses.field(default=1.7999999523162842, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe2b23f03, original_name='Unknown'
        ),
    })
    unknown_0x2f845006: float = dataclasses.field(default=150.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2f845006, original_name='Unknown'
        ),
    })
    unknown_0x5d1626fb: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5d1626fb, original_name='Unknown'
        ),
    })
    unknown_0xbb76891a: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbb76891a, original_name='Unknown'
        ),
    })
    unknown_0x285d67ad: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x285d67ad, original_name='Unknown'
        ),
    })
    unknown_0x6d5f242f: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6d5f242f, original_name='Unknown'
        ),
    })
    unknown_0xe3ff2ed6: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xe3ff2ed6, original_name='Unknown'
        ),
    })
    unknown_0xa6fd6d54: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa6fd6d54, original_name='Unknown'
        ),
    })
    unknown_0xecb314b6: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xecb314b6, original_name='Unknown'
        ),
    })
    unknown_0xa9b15734: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa9b15734, original_name='Unknown'
        ),
    })
    locomotion_speed_scale: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1213a7d4, original_name='LocomotionSpeedScale'
        ),
    })
    ing_spot_speed_scale: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc19ed897, original_name='IngSpotSpeedScale'
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
        if property_count != 14:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHlLHlLHlLHlLHlLHlLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(140))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39]) == _FAST_IDS
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
            dec[38],
            dec[41],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'%\xd0+\xc5')  # 0x25d02bc5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x25d02bc5))

        data.write(b'\xab\xe9\x9d\xe0')  # 0xabe99de0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xabe99de0))

        data.write(b'\xe2\xb2?\x03')  # 0xe2b23f03
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe2b23f03))

        data.write(b'/\x84P\x06')  # 0x2f845006
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2f845006))

        data.write(b']\x16&\xfb')  # 0x5d1626fb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5d1626fb))

        data.write(b'\xbbv\x89\x1a')  # 0xbb76891a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbb76891a))

        data.write(b'(]g\xad')  # 0x285d67ad
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x285d67ad))

        data.write(b'm_$/')  # 0x6d5f242f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x6d5f242f))

        data.write(b'\xe3\xff.\xd6')  # 0xe3ff2ed6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xe3ff2ed6))

        data.write(b'\xa6\xfdmT')  # 0xa6fd6d54
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xa6fd6d54))

        data.write(b'\xec\xb3\x14\xb6')  # 0xecb314b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xecb314b6))

        data.write(b'\xa9\xb1W4')  # 0xa9b15734
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xa9b15734))

        data.write(b'\x12\x13\xa7\xd4')  # 0x1213a7d4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.locomotion_speed_scale))

        data.write(b'\xc1\x9e\xd8\x97')  # 0xc19ed897
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ing_spot_speed_scale))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("IngBoostBallGuardianStructJson", data)
        return cls(
            unknown_0x25d02bc5=json_data['unknown_0x25d02bc5'],
            unknown_0xabe99de0=json_data['unknown_0xabe99de0'],
            unknown_0xe2b23f03=json_data['unknown_0xe2b23f03'],
            unknown_0x2f845006=json_data['unknown_0x2f845006'],
            unknown_0x5d1626fb=json_data['unknown_0x5d1626fb'],
            unknown_0xbb76891a=json_data['unknown_0xbb76891a'],
            unknown_0x285d67ad=json_data['unknown_0x285d67ad'],
            unknown_0x6d5f242f=json_data['unknown_0x6d5f242f'],
            unknown_0xe3ff2ed6=json_data['unknown_0xe3ff2ed6'],
            unknown_0xa6fd6d54=json_data['unknown_0xa6fd6d54'],
            unknown_0xecb314b6=json_data['unknown_0xecb314b6'],
            unknown_0xa9b15734=json_data['unknown_0xa9b15734'],
            locomotion_speed_scale=json_data['locomotion_speed_scale'],
            ing_spot_speed_scale=json_data['ing_spot_speed_scale'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x25d02bc5': self.unknown_0x25d02bc5,
            'unknown_0xabe99de0': self.unknown_0xabe99de0,
            'unknown_0xe2b23f03': self.unknown_0xe2b23f03,
            'unknown_0x2f845006': self.unknown_0x2f845006,
            'unknown_0x5d1626fb': self.unknown_0x5d1626fb,
            'unknown_0xbb76891a': self.unknown_0xbb76891a,
            'unknown_0x285d67ad': self.unknown_0x285d67ad,
            'unknown_0x6d5f242f': self.unknown_0x6d5f242f,
            'unknown_0xe3ff2ed6': self.unknown_0xe3ff2ed6,
            'unknown_0xa6fd6d54': self.unknown_0xa6fd6d54,
            'unknown_0xecb314b6': self.unknown_0xecb314b6,
            'unknown_0xa9b15734': self.unknown_0xa9b15734,
            'locomotion_speed_scale': self.locomotion_speed_scale,
            'ing_spot_speed_scale': self.ing_spot_speed_scale,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0x25d02bc5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xabe99de0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe2b23f03(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2f845006(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5d1626fb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbb76891a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x285d67ad(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x6d5f242f(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xe3ff2ed6(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xa6fd6d54(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xecb314b6(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xa9b15734(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_locomotion_speed_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ing_spot_speed_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x25d02bc5: ('unknown_0x25d02bc5', _decode_unknown_0x25d02bc5),
    0xabe99de0: ('unknown_0xabe99de0', _decode_unknown_0xabe99de0),
    0xe2b23f03: ('unknown_0xe2b23f03', _decode_unknown_0xe2b23f03),
    0x2f845006: ('unknown_0x2f845006', _decode_unknown_0x2f845006),
    0x5d1626fb: ('unknown_0x5d1626fb', _decode_unknown_0x5d1626fb),
    0xbb76891a: ('unknown_0xbb76891a', _decode_unknown_0xbb76891a),
    0x285d67ad: ('unknown_0x285d67ad', _decode_unknown_0x285d67ad),
    0x6d5f242f: ('unknown_0x6d5f242f', _decode_unknown_0x6d5f242f),
    0xe3ff2ed6: ('unknown_0xe3ff2ed6', _decode_unknown_0xe3ff2ed6),
    0xa6fd6d54: ('unknown_0xa6fd6d54', _decode_unknown_0xa6fd6d54),
    0xecb314b6: ('unknown_0xecb314b6', _decode_unknown_0xecb314b6),
    0xa9b15734: ('unknown_0xa9b15734', _decode_unknown_0xa9b15734),
    0x1213a7d4: ('locomotion_speed_scale', _decode_locomotion_speed_scale),
    0xc19ed897: ('ing_spot_speed_scale', _decode_ing_spot_speed_scale),
}
