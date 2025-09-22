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
from retro_data_structures.properties.corruption.core.Vector import Vector

if typing.TYPE_CHECKING:
    class TweakPlayer_FirstPersonCameraJson(typing_extensions.TypedDict):
        unknown_0xba5eb7f5: float
        camera_elevation: float
        unknown_0xb400ebd6: float
        unknown_0xfd26b7b9: float
        unknown_0x97b14dc6: float
        unknown_0xeb59925a: float
        unknown_0xa1d73380: float
        unknown_0xc8e8344a: float
        unknown_0xd40c480e: float
        unknown_0x7960c3a0: json_util.JsonValue
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xba5eb7f5, 0xd41e3ba, 0xb400ebd6, 0xfd26b7b9, 0x97b14dc6, 0xeb59925a, 0xa1d73380, 0xc8e8344a, 0xd40c480e, 0x7960c3a0)


@dataclasses.dataclass()
class TweakPlayer_FirstPersonCamera(BaseProperty):
    unknown_0xba5eb7f5: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xba5eb7f5, original_name='Unknown'
        ),
    })
    camera_elevation: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0d41e3ba, original_name='CameraElevation'
        ),
    })
    unknown_0xb400ebd6: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb400ebd6, original_name='Unknown'
        ),
    })
    unknown_0xfd26b7b9: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfd26b7b9, original_name='Unknown'
        ),
    })
    unknown_0x97b14dc6: float = dataclasses.field(default=73.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x97b14dc6, original_name='Unknown'
        ),
    })
    unknown_0xeb59925a: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeb59925a, original_name='Unknown'
        ),
    })
    unknown_0xa1d73380: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa1d73380, original_name='Unknown'
        ),
    })
    unknown_0xc8e8344a: float = dataclasses.field(default=73.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc8e8344a, original_name='Unknown'
        ),
    })
    unknown_0xd40c480e: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd40c480e, original_name='Unknown'
        ),
    })
    unknown_0x7960c3a0: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x7960c3a0, original_name='Unknown', from_json=Vector.from_json, to_json=Vector.to_json
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
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHfLHfLHfLHfLHfLHfff')
    
        dec = _FAST_FORMAT.unpack(data.read(108))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27]) == _FAST_IDS
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
            Vector(*dec[29:32]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\n')  # 10 properties

        data.write(b'\xba^\xb7\xf5')  # 0xba5eb7f5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xba5eb7f5))

        data.write(b'\rA\xe3\xba')  # 0xd41e3ba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.camera_elevation))

        data.write(b'\xb4\x00\xeb\xd6')  # 0xb400ebd6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb400ebd6))

        data.write(b'\xfd&\xb7\xb9')  # 0xfd26b7b9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfd26b7b9))

        data.write(b'\x97\xb1M\xc6')  # 0x97b14dc6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x97b14dc6))

        data.write(b'\xebY\x92Z')  # 0xeb59925a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xeb59925a))

        data.write(b'\xa1\xd73\x80')  # 0xa1d73380
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa1d73380))

        data.write(b'\xc8\xe84J')  # 0xc8e8344a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc8e8344a))

        data.write(b'\xd4\x0cH\x0e')  # 0xd40c480e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd40c480e))

        data.write(b'y`\xc3\xa0')  # 0x7960c3a0
        data.write(b'\x00\x0c')  # size
        self.unknown_0x7960c3a0.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayer_FirstPersonCameraJson", data)
        return cls(
            unknown_0xba5eb7f5=json_data['unknown_0xba5eb7f5'],
            camera_elevation=json_data['camera_elevation'],
            unknown_0xb400ebd6=json_data['unknown_0xb400ebd6'],
            unknown_0xfd26b7b9=json_data['unknown_0xfd26b7b9'],
            unknown_0x97b14dc6=json_data['unknown_0x97b14dc6'],
            unknown_0xeb59925a=json_data['unknown_0xeb59925a'],
            unknown_0xa1d73380=json_data['unknown_0xa1d73380'],
            unknown_0xc8e8344a=json_data['unknown_0xc8e8344a'],
            unknown_0xd40c480e=json_data['unknown_0xd40c480e'],
            unknown_0x7960c3a0=Vector.from_json(json_data['unknown_0x7960c3a0']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xba5eb7f5': self.unknown_0xba5eb7f5,
            'camera_elevation': self.camera_elevation,
            'unknown_0xb400ebd6': self.unknown_0xb400ebd6,
            'unknown_0xfd26b7b9': self.unknown_0xfd26b7b9,
            'unknown_0x97b14dc6': self.unknown_0x97b14dc6,
            'unknown_0xeb59925a': self.unknown_0xeb59925a,
            'unknown_0xa1d73380': self.unknown_0xa1d73380,
            'unknown_0xc8e8344a': self.unknown_0xc8e8344a,
            'unknown_0xd40c480e': self.unknown_0xd40c480e,
            'unknown_0x7960c3a0': self.unknown_0x7960c3a0.to_json(),
        }


def _decode_unknown_0xba5eb7f5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_camera_elevation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb400ebd6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfd26b7b9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x97b14dc6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xeb59925a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa1d73380(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc8e8344a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xd40c480e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7960c3a0(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xba5eb7f5: ('unknown_0xba5eb7f5', _decode_unknown_0xba5eb7f5),
    0xd41e3ba: ('camera_elevation', _decode_camera_elevation),
    0xb400ebd6: ('unknown_0xb400ebd6', _decode_unknown_0xb400ebd6),
    0xfd26b7b9: ('unknown_0xfd26b7b9', _decode_unknown_0xfd26b7b9),
    0x97b14dc6: ('unknown_0x97b14dc6', _decode_unknown_0x97b14dc6),
    0xeb59925a: ('unknown_0xeb59925a', _decode_unknown_0xeb59925a),
    0xa1d73380: ('unknown_0xa1d73380', _decode_unknown_0xa1d73380),
    0xc8e8344a: ('unknown_0xc8e8344a', _decode_unknown_0xc8e8344a),
    0xd40c480e: ('unknown_0xd40c480e', _decode_unknown_0xd40c480e),
    0x7960c3a0: ('unknown_0x7960c3a0', _decode_unknown_0x7960c3a0),
}
