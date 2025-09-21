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
import retro_data_structures.enums.corruption as enums

if typing.TYPE_CHECKING:
    class TweakPlayer_AimStuffJson(typing_extensions.TypedDict):
        aim_min_time: float
        aim_max_time: float
        aim_max_distance: float
        aim_max_angle_left: float
        aim_max_angle_right: float
        aim_max_angle_up: float
        aim_max_angle_down: float
        aim_angle_per_second: float
        aim_threshold_distance: float
        aim_turn_angle_per_second: float
        unknown_0x54354c80: float
        aim_box_width: float
        aim_box_height: float
        aim_target_timer: float
        aim_assist_horizontal_angle: float
        aim_assist_vertical_angle: float
        unknown_0x38ee6d6e: bool
        unknown_0x9e3aceb5: bool
        unknown_0x228a8def: bool
        unknown_0x534a7b3c: bool
        unknown_0xd2dfc16a: bool
        unknown_0x60f08beb: int
        unknown_0xcca13e22: bool
        unknown_0x85437c89: float
        unknown_0x21047226: bool
        unknown_0x95f112be: float
        unknown_0xb5d9e201: bool
        unknown_0x747a79cb: float
        unknown_0x189d7017: int
        unknown_0xa065b70c: bool
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x27c60d0a, 0xb7b51de0, 0xf77d0359, 0xde887cca, 0xb4b07d5d, 0xe5f8c567, 0x9774749d, 0x133f3002, 0x96fab602, 0x94164a2f, 0x54354c80, 0x5361ce18, 0x4b2e9260, 0x3b9a3789, 0x38dd0b85, 0x1157883e, 0x38ee6d6e, 0x9e3aceb5, 0x228a8def, 0x534a7b3c, 0xd2dfc16a, 0x60f08beb, 0xcca13e22, 0x85437c89, 0x21047226, 0x95f112be, 0xb5d9e201, 0x747a79cb, 0x189d7017, 0xa065b70c)


@dataclasses.dataclass()
class TweakPlayer_AimStuff(BaseProperty):
    aim_min_time: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x27c60d0a, original_name='AimMinTime'
        ),
    })
    aim_max_time: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb7b51de0, original_name='AimMaxTime'
        ),
    })
    aim_max_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf77d0359, original_name='AimMaxDistance'
        ),
    })
    aim_max_angle_left: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xde887cca, original_name='AimMaxAngleLeft'
        ),
    })
    aim_max_angle_right: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb4b07d5d, original_name='AimMaxAngleRight'
        ),
    })
    aim_max_angle_up: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe5f8c567, original_name='AimMaxAngleUp'
        ),
    })
    aim_max_angle_down: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9774749d, original_name='AimMaxAngleDown'
        ),
    })
    aim_angle_per_second: float = dataclasses.field(default=110.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x133f3002, original_name='AimAnglePerSecond'
        ),
    })
    aim_threshold_distance: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x96fab602, original_name='AimThresholdDistance'
        ),
    })
    aim_turn_angle_per_second: float = dataclasses.field(default=360.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x94164a2f, original_name='AimTurnAnglePerSecond'
        ),
    })
    unknown_0x54354c80: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x54354c80, original_name='Unknown'
        ),
    })
    aim_box_width: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5361ce18, original_name='AimBoxWidth'
        ),
    })
    aim_box_height: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4b2e9260, original_name='AimBoxHeight'
        ),
    })
    aim_target_timer: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3b9a3789, original_name='AimTargetTimer'
        ),
    })
    aim_assist_horizontal_angle: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x38dd0b85, original_name='AimAssistHorizontalAngle'
        ),
    })
    aim_assist_vertical_angle: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1157883e, original_name='AimAssistVerticalAngle'
        ),
    })
    unknown_0x38ee6d6e: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x38ee6d6e, original_name='Unknown'
        ),
    })
    unknown_0x9e3aceb5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x9e3aceb5, original_name='Unknown'
        ),
    })
    unknown_0x228a8def: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x228a8def, original_name='Unknown'
        ),
    })
    unknown_0x534a7b3c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x534a7b3c, original_name='Unknown'
        ),
    })
    unknown_0xd2dfc16a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xd2dfc16a, original_name='Unknown'
        ),
    })
    unknown_0x60f08beb: enums.TweakPlayer_AimStuff_UnknownEnum1Enum = dataclasses.field(default=enums.TweakPlayer_AimStuff_UnknownEnum1Enum.Unknown1, metadata={
        'reflection': FieldReflection[enums.TweakPlayer_AimStuff_UnknownEnum1Enum](
            enums.TweakPlayer_AimStuff_UnknownEnum1Enum, id=0x60f08beb, original_name='Unknown', from_json=enums.TweakPlayer_AimStuff_UnknownEnum1Enum.from_json, to_json=enums.TweakPlayer_AimStuff_UnknownEnum1Enum.to_json
        ),
    })
    unknown_0xcca13e22: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcca13e22, original_name='Unknown'
        ),
    })
    unknown_0x85437c89: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x85437c89, original_name='Unknown'
        ),
    })
    unknown_0x21047226: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x21047226, original_name='Unknown'
        ),
    })
    unknown_0x95f112be: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x95f112be, original_name='Unknown'
        ),
    })
    unknown_0xb5d9e201: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xb5d9e201, original_name='Unknown'
        ),
    })
    unknown_0x747a79cb: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x747a79cb, original_name='Unknown'
        ),
    })
    unknown_0x189d7017: enums.TweakPlayer_AimStuff_UnknownEnum2Enum = dataclasses.field(default=enums.TweakPlayer_AimStuff_UnknownEnum2Enum.Unknown2, metadata={
        'reflection': FieldReflection[enums.TweakPlayer_AimStuff_UnknownEnum2Enum](
            enums.TweakPlayer_AimStuff_UnknownEnum2Enum, id=0x189d7017, original_name='Unknown', from_json=enums.TweakPlayer_AimStuff_UnknownEnum2Enum.from_json, to_json=enums.TweakPlayer_AimStuff_UnknownEnum2Enum.to_json
        ),
    })
    unknown_0xa065b70c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa065b70c, original_name='Unknown'
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
        if property_count != 30:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLH?LH?LH?LH?LH?LHLLH?LHfLH?LHfLH?LHfLHLLH?')
    
        dec = _FAST_FORMAT.unpack(data.read(273))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39], dec[42], dec[45], dec[48], dec[51], dec[54], dec[57], dec[60], dec[63], dec[66], dec[69], dec[72], dec[75], dec[78], dec[81], dec[84], dec[87]) == _FAST_IDS
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
            dec[44],
            dec[47],
            dec[50],
            dec[53],
            dec[56],
            dec[59],
            dec[62],
            enums.TweakPlayer_AimStuff_UnknownEnum1Enum(dec[65]),
            dec[68],
            dec[71],
            dec[74],
            dec[77],
            dec[80],
            dec[83],
            enums.TweakPlayer_AimStuff_UnknownEnum2Enum(dec[86]),
            dec[89],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x1e')  # 30 properties

        data.write(b"'\xc6\r\n")  # 0x27c60d0a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_min_time))

        data.write(b'\xb7\xb5\x1d\xe0')  # 0xb7b51de0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_max_time))

        data.write(b'\xf7}\x03Y')  # 0xf77d0359
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_max_distance))

        data.write(b'\xde\x88|\xca')  # 0xde887cca
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_max_angle_left))

        data.write(b'\xb4\xb0}]')  # 0xb4b07d5d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_max_angle_right))

        data.write(b'\xe5\xf8\xc5g')  # 0xe5f8c567
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_max_angle_up))

        data.write(b'\x97tt\x9d')  # 0x9774749d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_max_angle_down))

        data.write(b'\x13?0\x02')  # 0x133f3002
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_angle_per_second))

        data.write(b'\x96\xfa\xb6\x02')  # 0x96fab602
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_threshold_distance))

        data.write(b'\x94\x16J/')  # 0x94164a2f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_turn_angle_per_second))

        data.write(b'T5L\x80')  # 0x54354c80
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x54354c80))

        data.write(b'Sa\xce\x18')  # 0x5361ce18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_box_width))

        data.write(b'K.\x92`')  # 0x4b2e9260
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_box_height))

        data.write(b';\x9a7\x89')  # 0x3b9a3789
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_target_timer))

        data.write(b'8\xdd\x0b\x85')  # 0x38dd0b85
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_assist_horizontal_angle))

        data.write(b'\x11W\x88>')  # 0x1157883e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aim_assist_vertical_angle))

        data.write(b'8\xeemn')  # 0x38ee6d6e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x38ee6d6e))

        data.write(b'\x9e:\xce\xb5')  # 0x9e3aceb5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x9e3aceb5))

        data.write(b'"\x8a\x8d\xef')  # 0x228a8def
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x228a8def))

        data.write(b'SJ{<')  # 0x534a7b3c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x534a7b3c))

        data.write(b'\xd2\xdf\xc1j')  # 0xd2dfc16a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xd2dfc16a))

        data.write(b'`\xf0\x8b\xeb')  # 0x60f08beb
        data.write(b'\x00\x04')  # size
        self.unknown_0x60f08beb.to_stream(data)

        data.write(b'\xcc\xa1>"')  # 0xcca13e22
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xcca13e22))

        data.write(b'\x85C|\x89')  # 0x85437c89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x85437c89))

        data.write(b'!\x04r&')  # 0x21047226
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x21047226))

        data.write(b'\x95\xf1\x12\xbe')  # 0x95f112be
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x95f112be))

        data.write(b'\xb5\xd9\xe2\x01')  # 0xb5d9e201
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xb5d9e201))

        data.write(b'tzy\xcb')  # 0x747a79cb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x747a79cb))

        data.write(b'\x18\x9dp\x17')  # 0x189d7017
        data.write(b'\x00\x04')  # size
        self.unknown_0x189d7017.to_stream(data)

        data.write(b'\xa0e\xb7\x0c')  # 0xa065b70c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xa065b70c))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayer_AimStuffJson", data)
        return cls(
            aim_min_time=json_data['aim_min_time'],
            aim_max_time=json_data['aim_max_time'],
            aim_max_distance=json_data['aim_max_distance'],
            aim_max_angle_left=json_data['aim_max_angle_left'],
            aim_max_angle_right=json_data['aim_max_angle_right'],
            aim_max_angle_up=json_data['aim_max_angle_up'],
            aim_max_angle_down=json_data['aim_max_angle_down'],
            aim_angle_per_second=json_data['aim_angle_per_second'],
            aim_threshold_distance=json_data['aim_threshold_distance'],
            aim_turn_angle_per_second=json_data['aim_turn_angle_per_second'],
            unknown_0x54354c80=json_data['unknown_0x54354c80'],
            aim_box_width=json_data['aim_box_width'],
            aim_box_height=json_data['aim_box_height'],
            aim_target_timer=json_data['aim_target_timer'],
            aim_assist_horizontal_angle=json_data['aim_assist_horizontal_angle'],
            aim_assist_vertical_angle=json_data['aim_assist_vertical_angle'],
            unknown_0x38ee6d6e=json_data['unknown_0x38ee6d6e'],
            unknown_0x9e3aceb5=json_data['unknown_0x9e3aceb5'],
            unknown_0x228a8def=json_data['unknown_0x228a8def'],
            unknown_0x534a7b3c=json_data['unknown_0x534a7b3c'],
            unknown_0xd2dfc16a=json_data['unknown_0xd2dfc16a'],
            unknown_0x60f08beb=enums.TweakPlayer_AimStuff_UnknownEnum1Enum.from_json(json_data['unknown_0x60f08beb']),
            unknown_0xcca13e22=json_data['unknown_0xcca13e22'],
            unknown_0x85437c89=json_data['unknown_0x85437c89'],
            unknown_0x21047226=json_data['unknown_0x21047226'],
            unknown_0x95f112be=json_data['unknown_0x95f112be'],
            unknown_0xb5d9e201=json_data['unknown_0xb5d9e201'],
            unknown_0x747a79cb=json_data['unknown_0x747a79cb'],
            unknown_0x189d7017=enums.TweakPlayer_AimStuff_UnknownEnum2Enum.from_json(json_data['unknown_0x189d7017']),
            unknown_0xa065b70c=json_data['unknown_0xa065b70c'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'aim_min_time': self.aim_min_time,
            'aim_max_time': self.aim_max_time,
            'aim_max_distance': self.aim_max_distance,
            'aim_max_angle_left': self.aim_max_angle_left,
            'aim_max_angle_right': self.aim_max_angle_right,
            'aim_max_angle_up': self.aim_max_angle_up,
            'aim_max_angle_down': self.aim_max_angle_down,
            'aim_angle_per_second': self.aim_angle_per_second,
            'aim_threshold_distance': self.aim_threshold_distance,
            'aim_turn_angle_per_second': self.aim_turn_angle_per_second,
            'unknown_0x54354c80': self.unknown_0x54354c80,
            'aim_box_width': self.aim_box_width,
            'aim_box_height': self.aim_box_height,
            'aim_target_timer': self.aim_target_timer,
            'aim_assist_horizontal_angle': self.aim_assist_horizontal_angle,
            'aim_assist_vertical_angle': self.aim_assist_vertical_angle,
            'unknown_0x38ee6d6e': self.unknown_0x38ee6d6e,
            'unknown_0x9e3aceb5': self.unknown_0x9e3aceb5,
            'unknown_0x228a8def': self.unknown_0x228a8def,
            'unknown_0x534a7b3c': self.unknown_0x534a7b3c,
            'unknown_0xd2dfc16a': self.unknown_0xd2dfc16a,
            'unknown_0x60f08beb': self.unknown_0x60f08beb.to_json(),
            'unknown_0xcca13e22': self.unknown_0xcca13e22,
            'unknown_0x85437c89': self.unknown_0x85437c89,
            'unknown_0x21047226': self.unknown_0x21047226,
            'unknown_0x95f112be': self.unknown_0x95f112be,
            'unknown_0xb5d9e201': self.unknown_0xb5d9e201,
            'unknown_0x747a79cb': self.unknown_0x747a79cb,
            'unknown_0x189d7017': self.unknown_0x189d7017.to_json(),
            'unknown_0xa065b70c': self.unknown_0xa065b70c,
        }


def _decode_aim_min_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_max_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_max_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_max_angle_left(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_max_angle_right(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_max_angle_up(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_max_angle_down(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_angle_per_second(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_threshold_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_turn_angle_per_second(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x54354c80(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_box_width(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_box_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_target_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_assist_horizontal_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_aim_assist_vertical_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x38ee6d6e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x9e3aceb5(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x228a8def(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x534a7b3c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xd2dfc16a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x60f08beb(data: typing.BinaryIO, property_size: int) -> enums.TweakPlayer_AimStuff_UnknownEnum1Enum:
    return enums.TweakPlayer_AimStuff_UnknownEnum1Enum.from_stream(data)


def _decode_unknown_0xcca13e22(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x85437c89(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x21047226(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x95f112be(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb5d9e201(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x747a79cb(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x189d7017(data: typing.BinaryIO, property_size: int) -> enums.TweakPlayer_AimStuff_UnknownEnum2Enum:
    return enums.TweakPlayer_AimStuff_UnknownEnum2Enum.from_stream(data)


def _decode_unknown_0xa065b70c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x27c60d0a: ('aim_min_time', _decode_aim_min_time),
    0xb7b51de0: ('aim_max_time', _decode_aim_max_time),
    0xf77d0359: ('aim_max_distance', _decode_aim_max_distance),
    0xde887cca: ('aim_max_angle_left', _decode_aim_max_angle_left),
    0xb4b07d5d: ('aim_max_angle_right', _decode_aim_max_angle_right),
    0xe5f8c567: ('aim_max_angle_up', _decode_aim_max_angle_up),
    0x9774749d: ('aim_max_angle_down', _decode_aim_max_angle_down),
    0x133f3002: ('aim_angle_per_second', _decode_aim_angle_per_second),
    0x96fab602: ('aim_threshold_distance', _decode_aim_threshold_distance),
    0x94164a2f: ('aim_turn_angle_per_second', _decode_aim_turn_angle_per_second),
    0x54354c80: ('unknown_0x54354c80', _decode_unknown_0x54354c80),
    0x5361ce18: ('aim_box_width', _decode_aim_box_width),
    0x4b2e9260: ('aim_box_height', _decode_aim_box_height),
    0x3b9a3789: ('aim_target_timer', _decode_aim_target_timer),
    0x38dd0b85: ('aim_assist_horizontal_angle', _decode_aim_assist_horizontal_angle),
    0x1157883e: ('aim_assist_vertical_angle', _decode_aim_assist_vertical_angle),
    0x38ee6d6e: ('unknown_0x38ee6d6e', _decode_unknown_0x38ee6d6e),
    0x9e3aceb5: ('unknown_0x9e3aceb5', _decode_unknown_0x9e3aceb5),
    0x228a8def: ('unknown_0x228a8def', _decode_unknown_0x228a8def),
    0x534a7b3c: ('unknown_0x534a7b3c', _decode_unknown_0x534a7b3c),
    0xd2dfc16a: ('unknown_0xd2dfc16a', _decode_unknown_0xd2dfc16a),
    0x60f08beb: ('unknown_0x60f08beb', _decode_unknown_0x60f08beb),
    0xcca13e22: ('unknown_0xcca13e22', _decode_unknown_0xcca13e22),
    0x85437c89: ('unknown_0x85437c89', _decode_unknown_0x85437c89),
    0x21047226: ('unknown_0x21047226', _decode_unknown_0x21047226),
    0x95f112be: ('unknown_0x95f112be', _decode_unknown_0x95f112be),
    0xb5d9e201: ('unknown_0xb5d9e201', _decode_unknown_0xb5d9e201),
    0x747a79cb: ('unknown_0x747a79cb', _decode_unknown_0x747a79cb),
    0x189d7017: ('unknown_0x189d7017', _decode_unknown_0x189d7017),
    0xa065b70c: ('unknown_0xa065b70c', _decode_unknown_0xa065b70c),
}
