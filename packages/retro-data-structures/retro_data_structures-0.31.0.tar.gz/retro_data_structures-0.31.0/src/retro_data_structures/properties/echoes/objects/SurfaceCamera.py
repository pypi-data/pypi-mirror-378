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
from retro_data_structures.properties.echoes.archetypes.SplineType import SplineType
from retro_data_structures.properties.echoes.core.Spline import Spline
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SurfaceCameraJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        flags_surface_camera: int
        surface_type: int
        spline: json_util.JsonObject
        player_offset: json_util.JsonValue
        spline_type: json_util.JsonObject
        unknown_0x431769c6: bool
        target_spline_type: json_util.JsonObject
        unknown_0x33b4f106: bool
        target_control_spline: json_util.JsonObject
        fov_spline: json_util.JsonObject
    

@dataclasses.dataclass()
class SurfaceCamera(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    flags_surface_camera: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1ffc65d8, original_name='FlagsSurfaceCamera'
        ),
    })
    surface_type: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1405b5e4, original_name='SurfaceType'
        ),
    })
    spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x922d151f, original_name='Spline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    player_offset: Vector = dataclasses.field(default_factory=lambda: Vector(x=0.0, y=0.0, z=0.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x1d8b933f, original_name='PlayerOffset', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    spline_type: SplineType = dataclasses.field(default_factory=SplineType, metadata={
        'reflection': FieldReflection[SplineType](
            SplineType, id=0x33e4685b, original_name='SplineType', from_json=SplineType.from_json, to_json=SplineType.to_json
        ),
    })
    unknown_0x431769c6: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x431769c6, original_name='Unknown'
        ),
    })
    target_spline_type: SplineType = dataclasses.field(default_factory=SplineType, metadata={
        'reflection': FieldReflection[SplineType](
            SplineType, id=0x5604d304, original_name='TargetSplineType', from_json=SplineType.from_json, to_json=SplineType.to_json
        ),
    })
    unknown_0x33b4f106: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x33b4f106, original_name='Unknown'
        ),
    })
    target_control_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xc4dfbfa7, original_name='TargetControlSpline', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    fov_spline: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x6868d4b3, original_name='FOVSpline', from_json=Spline.from_json, to_json=Spline.to_json
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
        return 'SURC'

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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ffc65d8
        flags_surface_camera = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1405b5e4
        surface_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x922d151f
        spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1d8b933f
        player_offset = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x33e4685b
        spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x431769c6
        unknown_0x431769c6 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5604d304
        target_spline_type = SplineType.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x33b4f106
        unknown_0x33b4f106 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4dfbfa7
        target_control_spline = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6868d4b3
        fov_spline = Spline.from_stream(data, property_size)
    
        return cls(editor_properties, flags_surface_camera, surface_type, spline, player_offset, spline_type, unknown_0x431769c6, target_spline_type, unknown_0x33b4f106, target_control_spline, fov_spline)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1f\xfce\xd8')  # 0x1ffc65d8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.flags_surface_camera))

        data.write(b'\x14\x05\xb5\xe4')  # 0x1405b5e4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.surface_type))

        data.write(b'\x92-\x15\x1f')  # 0x922d151f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1d\x8b\x93?')  # 0x1d8b933f
        data.write(b'\x00\x0c')  # size
        self.player_offset.to_stream(data)

        data.write(b'3\xe4h[')  # 0x33e4685b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spline_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'C\x17i\xc6')  # 0x431769c6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x431769c6))

        data.write(b'V\x04\xd3\x04')  # 0x5604d304
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.target_spline_type.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3\xb4\xf1\x06')  # 0x33b4f106
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x33b4f106))

        data.write(b'\xc4\xdf\xbf\xa7')  # 0xc4dfbfa7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.target_control_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'hh\xd4\xb3')  # 0x6868d4b3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.fov_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SurfaceCameraJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            flags_surface_camera=json_data['flags_surface_camera'],
            surface_type=json_data['surface_type'],
            spline=Spline.from_json(json_data['spline']),
            player_offset=Vector.from_json(json_data['player_offset']),
            spline_type=SplineType.from_json(json_data['spline_type']),
            unknown_0x431769c6=json_data['unknown_0x431769c6'],
            target_spline_type=SplineType.from_json(json_data['target_spline_type']),
            unknown_0x33b4f106=json_data['unknown_0x33b4f106'],
            target_control_spline=Spline.from_json(json_data['target_control_spline']),
            fov_spline=Spline.from_json(json_data['fov_spline']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'flags_surface_camera': self.flags_surface_camera,
            'surface_type': self.surface_type,
            'spline': self.spline.to_json(),
            'player_offset': self.player_offset.to_json(),
            'spline_type': self.spline_type.to_json(),
            'unknown_0x431769c6': self.unknown_0x431769c6,
            'target_spline_type': self.target_spline_type.to_json(),
            'unknown_0x33b4f106': self.unknown_0x33b4f106,
            'target_control_spline': self.target_control_spline.to_json(),
            'fov_spline': self.fov_spline.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.spline_type.dependencies_for, "spline_type", "SplineType"),
            (self.target_spline_type.dependencies_for, "target_spline_type", "SplineType"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SurfaceCamera.{field_name} ({field_type}): {e}"
                )


def _decode_flags_surface_camera(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_surface_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_player_offset(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_unknown_0x431769c6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x33b4f106(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x1ffc65d8: ('flags_surface_camera', _decode_flags_surface_camera),
    0x1405b5e4: ('surface_type', _decode_surface_type),
    0x922d151f: ('spline', Spline.from_stream),
    0x1d8b933f: ('player_offset', _decode_player_offset),
    0x33e4685b: ('spline_type', SplineType.from_stream),
    0x431769c6: ('unknown_0x431769c6', _decode_unknown_0x431769c6),
    0x5604d304: ('target_spline_type', SplineType.from_stream),
    0x33b4f106: ('unknown_0x33b4f106', _decode_unknown_0x33b4f106),
    0xc4dfbfa7: ('target_control_spline', Spline.from_stream),
    0x6868d4b3: ('fov_spline', Spline.from_stream),
}
