# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class GeneratorJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        random_count: int
        unique_locations: bool
        keep_orientation: bool
        use_originator_transform: bool
        offset: json_util.JsonValue
        random_scale_min: float
        random_scale_max: float
    

@dataclasses.dataclass()
class Generator(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    random_count: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x3fa67145, original_name='RandomCount'
        ),
    })
    unique_locations: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x88978e49, original_name='UniqueLocations'
        ),
    })
    keep_orientation: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1eb8e254, original_name='KeepOrientation'
        ),
    })
    use_originator_transform: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x035a5e10, original_name='UseOriginatorTransform'
        ),
    })
    offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x46477064, original_name='Offset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    random_scale_min: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3861b64, original_name='RandomScaleMin'
        ),
    })
    random_scale_max: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x25e6b485, original_name='RandomScaleMax'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'GENR'

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3fa67145
        random_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x88978e49
        unique_locations = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1eb8e254
        keep_orientation = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x035a5e10
        use_originator_transform = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x46477064
        offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3861b64
        random_scale_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x25e6b485
        random_scale_max = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, random_count, unique_locations, keep_orientation, use_originator_transform, offset, random_scale_min, random_scale_max)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'?\xa6qE')  # 0x3fa67145
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.random_count))

        data.write(b'\x88\x97\x8eI')  # 0x88978e49
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unique_locations))

        data.write(b'\x1e\xb8\xe2T')  # 0x1eb8e254
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.keep_orientation))

        data.write(b'\x03Z^\x10')  # 0x35a5e10
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_originator_transform))

        data.write(b'FGpd')  # 0x46477064
        data.write(b'\x00\x0c')  # size
        self.offset.to_stream(data)

        data.write(b'\xc3\x86\x1bd')  # 0xc3861b64
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.random_scale_min))

        data.write(b'%\xe6\xb4\x85')  # 0x25e6b485
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.random_scale_max))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("GeneratorJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            random_count=json_data['random_count'],
            unique_locations=json_data['unique_locations'],
            keep_orientation=json_data['keep_orientation'],
            use_originator_transform=json_data['use_originator_transform'],
            offset=Vector.from_json(json_data['offset']),
            random_scale_min=json_data['random_scale_min'],
            random_scale_max=json_data['random_scale_max'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'random_count': self.random_count,
            'unique_locations': self.unique_locations,
            'keep_orientation': self.keep_orientation,
            'use_originator_transform': self.use_originator_transform,
            'offset': self.offset.to_json(),
            'random_scale_min': self.random_scale_min,
            'random_scale_max': self.random_scale_max,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Generator.{field_name} ({field_type}): {e}"
                )


def _decode_random_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unique_locations(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_keep_orientation(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_use_originator_transform(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_random_scale_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_random_scale_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x3fa67145: ('random_count', _decode_random_count),
    0x88978e49: ('unique_locations', _decode_unique_locations),
    0x1eb8e254: ('keep_orientation', _decode_keep_orientation),
    0x35a5e10: ('use_originator_transform', _decode_use_originator_transform),
    0x46477064: ('offset', _decode_offset),
    0xc3861b64: ('random_scale_min', _decode_random_scale_min),
    0x25e6b485: ('random_scale_max', _decode_random_scale_max),
}
