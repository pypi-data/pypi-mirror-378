# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.ChasePosition import ChasePosition
from retro_data_structures.properties.corruption.archetypes.ColliderPosition import ColliderPosition
from retro_data_structures.properties.corruption.archetypes.OffsetPosition import OffsetPosition
from retro_data_structures.properties.corruption.archetypes.PathPosition import PathPosition
from retro_data_structures.properties.corruption.archetypes.SpindlePosition import SpindlePosition
from retro_data_structures.properties.corruption.archetypes.SurfacePosition import SurfacePosition

if typing.TYPE_CHECKING:
    class CameraPositionJson(typing_extensions.TypedDict):
        position_type: int
        flags_camera_position: int
        colliders: json_util.JsonObject
        chase: json_util.JsonObject
        path: json_util.JsonObject
        spindle: json_util.JsonObject
        surface: json_util.JsonObject
        offset: json_util.JsonObject
    

class PositionType(enum.IntEnum):
    Unknown1 = 3258570459
    Unknown2 = 700093416
    Unknown3 = 2482478106
    Unknown4 = 1505753942
    Unknown5 = 279679312
    Unknown6 = 330387643
    Unknown7 = 2897552223

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


@dataclasses.dataclass()
class CameraPosition(BaseProperty):
    position_type: PositionType = dataclasses.field(default=PositionType.Unknown1, metadata={
        'reflection': FieldReflection[PositionType](
            PositionType, id=0xb7cd4710, original_name='PositionType', from_json=PositionType.from_json, to_json=PositionType.to_json
        ),
    })
    flags_camera_position: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb1b6cf33, original_name='FlagsCameraPosition'
        ),
    })  # Flagset
    colliders: ColliderPosition = dataclasses.field(default_factory=ColliderPosition, metadata={
        'reflection': FieldReflection[ColliderPosition](
            ColliderPosition, id=0x501ed3a3, original_name='Colliders', from_json=ColliderPosition.from_json, to_json=ColliderPosition.to_json
        ),
    })
    chase: ChasePosition = dataclasses.field(default_factory=ChasePosition, metadata={
        'reflection': FieldReflection[ChasePosition](
            ChasePosition, id=0xbbddc576, original_name='Chase', from_json=ChasePosition.from_json, to_json=ChasePosition.to_json
        ),
    })
    path: PathPosition = dataclasses.field(default_factory=PathPosition, metadata={
        'reflection': FieldReflection[PathPosition](
            PathPosition, id=0xe8ab9bc8, original_name='Path', from_json=PathPosition.from_json, to_json=PathPosition.to_json
        ),
    })
    spindle: SpindlePosition = dataclasses.field(default_factory=SpindlePosition, metadata={
        'reflection': FieldReflection[SpindlePosition](
            SpindlePosition, id=0x9ec1df0c, original_name='Spindle', from_json=SpindlePosition.from_json, to_json=SpindlePosition.to_json
        ),
    })
    surface: SurfacePosition = dataclasses.field(default_factory=SurfacePosition, metadata={
        'reflection': FieldReflection[SurfacePosition](
            SurfacePosition, id=0xbbb2d1e6, original_name='Surface', from_json=SurfacePosition.from_json, to_json=SurfacePosition.to_json
        ),
    })
    offset: OffsetPosition = dataclasses.field(default_factory=OffsetPosition, metadata={
        'reflection': FieldReflection[OffsetPosition](
            OffsetPosition, id=0x07d194af, original_name='Offset', from_json=OffsetPosition.from_json, to_json=OffsetPosition.to_json
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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb7cd4710
        position_type = PositionType.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb1b6cf33
        flags_camera_position = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x501ed3a3
        colliders = ColliderPosition.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbbddc576
        chase = ChasePosition.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe8ab9bc8
        path = PathPosition.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ec1df0c
        spindle = SpindlePosition.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbbb2d1e6
        surface = SurfacePosition.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x07d194af
        offset = OffsetPosition.from_stream(data, property_size)
    
        return cls(position_type, flags_camera_position, colliders, chase, path, spindle, surface, offset)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\xb7\xcdG\x10')  # 0xb7cd4710
        data.write(b'\x00\x04')  # size
        self.position_type.to_stream(data)

        data.write(b'\xb1\xb6\xcf3')  # 0xb1b6cf33
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.flags_camera_position))

        data.write(b'P\x1e\xd3\xa3')  # 0x501ed3a3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.colliders.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbb\xdd\xc5v')  # 0xbbddc576
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.chase.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe8\xab\x9b\xc8')  # 0xe8ab9bc8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.path.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9e\xc1\xdf\x0c')  # 0x9ec1df0c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spindle.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbb\xb2\xd1\xe6')  # 0xbbb2d1e6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.surface.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x07\xd1\x94\xaf')  # 0x7d194af
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.offset.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CameraPositionJson", data)
        return cls(
            position_type=PositionType.from_json(json_data['position_type']),
            flags_camera_position=json_data['flags_camera_position'],
            colliders=ColliderPosition.from_json(json_data['colliders']),
            chase=ChasePosition.from_json(json_data['chase']),
            path=PathPosition.from_json(json_data['path']),
            spindle=SpindlePosition.from_json(json_data['spindle']),
            surface=SurfacePosition.from_json(json_data['surface']),
            offset=OffsetPosition.from_json(json_data['offset']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'position_type': self.position_type.to_json(),
            'flags_camera_position': self.flags_camera_position,
            'colliders': self.colliders.to_json(),
            'chase': self.chase.to_json(),
            'path': self.path.to_json(),
            'spindle': self.spindle.to_json(),
            'surface': self.surface.to_json(),
            'offset': self.offset.to_json(),
        }


def _decode_position_type(data: typing.BinaryIO, property_size: int) -> PositionType:
    return PositionType.from_stream(data)


def _decode_flags_camera_position(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack(">L", data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb7cd4710: ('position_type', _decode_position_type),
    0xb1b6cf33: ('flags_camera_position', _decode_flags_camera_position),
    0x501ed3a3: ('colliders', ColliderPosition.from_stream),
    0xbbddc576: ('chase', ChasePosition.from_stream),
    0xe8ab9bc8: ('path', PathPosition.from_stream),
    0x9ec1df0c: ('spindle', SpindlePosition.from_stream),
    0xbbb2d1e6: ('surface', SurfacePosition.from_stream),
    0x7d194af: ('offset', OffsetPosition.from_stream),
}
