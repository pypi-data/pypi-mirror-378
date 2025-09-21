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

    class GrappleParametersJson(typing_extensions.TypedDict):
        grapple_length: float
        grapple_attach_length: float
        grapple_spring_constant: float
        grapple_spring_length: float
        unknown_0x987f68c7: float
        swing_force: float
        swing_max_force: float
        swing_arc_angle: float
        swing_turn_angle: float
        swing_camera_pitch: float
        unknown_0xf9e45827: float
        unknown_0x11b6a17a: bool
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x7a797e4f, 0x1d852415, 0xfdf5cb82, 0x2ec254e3, 0x987f68c7, 0x1a6b49ab, 0x1e5124d4, 0x450ea130, 0x55f2bc8f, 0xf12bace9, 0xf9e45827, 0x11b6a17a)


@dataclasses.dataclass()
class GrappleParameters(BaseProperty):
    grapple_length: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a797e4f, original_name='GrappleLength'
        ),
    })
    grapple_attach_length: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1d852415, original_name='GrappleAttachLength'
        ),
    })
    grapple_spring_constant: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfdf5cb82, original_name='GrappleSpringConstant'
        ),
    })
    grapple_spring_length: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ec254e3, original_name='GrappleSpringLength'
        ),
    })
    unknown_0x987f68c7: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x987f68c7, original_name='Unknown'
        ),
    })
    swing_force: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1a6b49ab, original_name='SwingForce'
        ),
    })
    swing_max_force: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1e5124d4, original_name='SwingMaxForce'
        ),
    })
    swing_arc_angle: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x450ea130, original_name='SwingArcAngle'
        ),
    })
    swing_turn_angle: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x55f2bc8f, original_name='SwingTurnAngle'
        ),
    })
    swing_camera_pitch: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf12bace9, original_name='SwingCameraPitch'
        ),
    })
    unknown_0xf9e45827: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf9e45827, original_name='Unknown'
        ),
    })
    unknown_0x11b6a17a: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x11b6a17a, original_name='Unknown'
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
        if property_count != 12:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLH?')
    
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

        data.write(b'zy~O')  # 0x7a797e4f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grapple_length))

        data.write(b'\x1d\x85$\x15')  # 0x1d852415
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grapple_attach_length))

        data.write(b'\xfd\xf5\xcb\x82')  # 0xfdf5cb82
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grapple_spring_constant))

        data.write(b'.\xc2T\xe3')  # 0x2ec254e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grapple_spring_length))

        data.write(b'\x98\x7fh\xc7')  # 0x987f68c7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x987f68c7))

        data.write(b'\x1akI\xab')  # 0x1a6b49ab
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.swing_force))

        data.write(b'\x1eQ$\xd4')  # 0x1e5124d4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.swing_max_force))

        data.write(b'E\x0e\xa10')  # 0x450ea130
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.swing_arc_angle))

        data.write(b'U\xf2\xbc\x8f')  # 0x55f2bc8f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.swing_turn_angle))

        data.write(b'\xf1+\xac\xe9')  # 0xf12bace9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.swing_camera_pitch))

        data.write(b"\xf9\xe4X'")  # 0xf9e45827
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf9e45827))

        data.write(b'\x11\xb6\xa1z')  # 0x11b6a17a
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x11b6a17a))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GrappleParametersJson", data)
        return cls(
            grapple_length=json_data['grapple_length'],
            grapple_attach_length=json_data['grapple_attach_length'],
            grapple_spring_constant=json_data['grapple_spring_constant'],
            grapple_spring_length=json_data['grapple_spring_length'],
            unknown_0x987f68c7=json_data['unknown_0x987f68c7'],
            swing_force=json_data['swing_force'],
            swing_max_force=json_data['swing_max_force'],
            swing_arc_angle=json_data['swing_arc_angle'],
            swing_turn_angle=json_data['swing_turn_angle'],
            swing_camera_pitch=json_data['swing_camera_pitch'],
            unknown_0xf9e45827=json_data['unknown_0xf9e45827'],
            unknown_0x11b6a17a=json_data['unknown_0x11b6a17a'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'grapple_length': self.grapple_length,
            'grapple_attach_length': self.grapple_attach_length,
            'grapple_spring_constant': self.grapple_spring_constant,
            'grapple_spring_length': self.grapple_spring_length,
            'unknown_0x987f68c7': self.unknown_0x987f68c7,
            'swing_force': self.swing_force,
            'swing_max_force': self.swing_max_force,
            'swing_arc_angle': self.swing_arc_angle,
            'swing_turn_angle': self.swing_turn_angle,
            'swing_camera_pitch': self.swing_camera_pitch,
            'unknown_0xf9e45827': self.unknown_0xf9e45827,
            'unknown_0x11b6a17a': self.unknown_0x11b6a17a,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_grapple_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_attach_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_spring_constant(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_spring_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x987f68c7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_swing_force(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_swing_max_force(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_swing_arc_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_swing_turn_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_swing_camera_pitch(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf9e45827(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x11b6a17a(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7a797e4f: ('grapple_length', _decode_grapple_length),
    0x1d852415: ('grapple_attach_length', _decode_grapple_attach_length),
    0xfdf5cb82: ('grapple_spring_constant', _decode_grapple_spring_constant),
    0x2ec254e3: ('grapple_spring_length', _decode_grapple_spring_length),
    0x987f68c7: ('unknown_0x987f68c7', _decode_unknown_0x987f68c7),
    0x1a6b49ab: ('swing_force', _decode_swing_force),
    0x1e5124d4: ('swing_max_force', _decode_swing_max_force),
    0x450ea130: ('swing_arc_angle', _decode_swing_arc_angle),
    0x55f2bc8f: ('swing_turn_angle', _decode_swing_turn_angle),
    0xf12bace9: ('swing_camera_pitch', _decode_swing_camera_pitch),
    0xf9e45827: ('unknown_0xf9e45827', _decode_unknown_0xf9e45827),
    0x11b6a17a: ('unknown_0x11b6a17a', _decode_unknown_0x11b6a17a),
}
