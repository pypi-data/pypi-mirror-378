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

    class TweakPlayer_ScanVisorJson(typing_extensions.TypedDict):
        scan_distance: float
        scan_retention: bool
        scan_freezes_game: bool
        scan_line_of_sight: bool
        scan_max_target_distance: float
        scan_max_lock_distance: float
        scan_camera_speed: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xb0a32e5b, 0x2a75f2b8, 0x58284bb, 0x1e54f5ae, 0xadfa90fc, 0xf4db84a9, 0x8a7b245f)


@dataclasses.dataclass()
class TweakPlayer_ScanVisor(BaseProperty):
    scan_distance: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb0a32e5b, original_name='ScanDistance'
        ),
    })
    scan_retention: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2a75f2b8, original_name='ScanRetention'
        ),
    })
    scan_freezes_game: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x058284bb, original_name='ScanFreezesGame'
        ),
    })
    scan_line_of_sight: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1e54f5ae, original_name='ScanLineOfSight'
        ),
    })
    scan_max_target_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xadfa90fc, original_name='ScanMaxTargetDistance'
        ),
    })
    scan_max_lock_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf4db84a9, original_name='ScanMaxLockDistance'
        ),
    })
    scan_camera_speed: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8a7b245f, original_name='ScanCameraSpeed'
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
        if property_count != 7:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLH?LH?LH?LHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(61))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\xb0\xa3.[')  # 0xb0a32e5b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_distance))

        data.write(b'*u\xf2\xb8')  # 0x2a75f2b8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scan_retention))

        data.write(b'\x05\x82\x84\xbb')  # 0x58284bb
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scan_freezes_game))

        data.write(b'\x1eT\xf5\xae')  # 0x1e54f5ae
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scan_line_of_sight))

        data.write(b'\xad\xfa\x90\xfc')  # 0xadfa90fc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_max_target_distance))

        data.write(b'\xf4\xdb\x84\xa9')  # 0xf4db84a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_max_lock_distance))

        data.write(b'\x8a{$_')  # 0x8a7b245f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scan_camera_speed))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayer_ScanVisorJson", data)
        return cls(
            scan_distance=json_data['scan_distance'],
            scan_retention=json_data['scan_retention'],
            scan_freezes_game=json_data['scan_freezes_game'],
            scan_line_of_sight=json_data['scan_line_of_sight'],
            scan_max_target_distance=json_data['scan_max_target_distance'],
            scan_max_lock_distance=json_data['scan_max_lock_distance'],
            scan_camera_speed=json_data['scan_camera_speed'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'scan_distance': self.scan_distance,
            'scan_retention': self.scan_retention,
            'scan_freezes_game': self.scan_freezes_game,
            'scan_line_of_sight': self.scan_line_of_sight,
            'scan_max_target_distance': self.scan_max_target_distance,
            'scan_max_lock_distance': self.scan_max_lock_distance,
            'scan_camera_speed': self.scan_camera_speed,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_scan_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_retention(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_scan_freezes_game(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_scan_line_of_sight(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_scan_max_target_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_max_lock_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scan_camera_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb0a32e5b: ('scan_distance', _decode_scan_distance),
    0x2a75f2b8: ('scan_retention', _decode_scan_retention),
    0x58284bb: ('scan_freezes_game', _decode_scan_freezes_game),
    0x1e54f5ae: ('scan_line_of_sight', _decode_scan_line_of_sight),
    0xadfa90fc: ('scan_max_target_distance', _decode_scan_max_target_distance),
    0xf4db84a9: ('scan_max_lock_distance', _decode_scan_max_lock_distance),
    0x8a7b245f: ('scan_camera_speed', _decode_scan_camera_speed),
}
