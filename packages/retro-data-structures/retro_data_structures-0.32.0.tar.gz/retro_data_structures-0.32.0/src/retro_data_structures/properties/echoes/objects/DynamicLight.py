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
from retro_data_structures.properties.echoes.archetypes.DynamicLightFalloff import DynamicLightFalloff
from retro_data_structures.properties.echoes.archetypes.DynamicLightIntensity import DynamicLightIntensity
from retro_data_structures.properties.echoes.archetypes.DynamicLightMotionSpline import DynamicLightMotionSpline
from retro_data_structures.properties.echoes.archetypes.DynamicLightParent import DynamicLightParent
from retro_data_structures.properties.echoes.archetypes.DynamicLightSpotlight import DynamicLightSpotlight
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DynamicLightJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        light_type: int
        light_set: int
        color: json_util.JsonValue
        intensity: json_util.JsonObject
        falloff: json_util.JsonObject
        spotlight: json_util.JsonObject
        motion_spline: json_util.JsonObject
        parent: json_util.JsonObject
    

@dataclasses.dataclass()
class DynamicLight(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    light_type: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7fc4e336, original_name='LightType'
        ),
    })
    light_set: int = dataclasses.field(default=6, metadata={
        'reflection': FieldReflection[int](
            int, id=0x3e8b3b2f, original_name='LightSet'
        ),
    })
    color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x37c7d09d, original_name='Color', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    intensity: DynamicLightIntensity = dataclasses.field(default_factory=DynamicLightIntensity, metadata={
        'reflection': FieldReflection[DynamicLightIntensity](
            DynamicLightIntensity, id=0x72531ede, original_name='Intensity', from_json=DynamicLightIntensity.from_json, to_json=DynamicLightIntensity.to_json
        ),
    })
    falloff: DynamicLightFalloff = dataclasses.field(default_factory=DynamicLightFalloff, metadata={
        'reflection': FieldReflection[DynamicLightFalloff](
            DynamicLightFalloff, id=0x219b52da, original_name='Falloff', from_json=DynamicLightFalloff.from_json, to_json=DynamicLightFalloff.to_json
        ),
    })
    spotlight: DynamicLightSpotlight = dataclasses.field(default_factory=DynamicLightSpotlight, metadata={
        'reflection': FieldReflection[DynamicLightSpotlight](
            DynamicLightSpotlight, id=0x9546f449, original_name='Spotlight', from_json=DynamicLightSpotlight.from_json, to_json=DynamicLightSpotlight.to_json
        ),
    })
    motion_spline: DynamicLightMotionSpline = dataclasses.field(default_factory=DynamicLightMotionSpline, metadata={
        'reflection': FieldReflection[DynamicLightMotionSpline](
            DynamicLightMotionSpline, id=0x14322138, original_name='MotionSpline', from_json=DynamicLightMotionSpline.from_json, to_json=DynamicLightMotionSpline.to_json
        ),
    })
    parent: DynamicLightParent = dataclasses.field(default_factory=DynamicLightParent, metadata={
        'reflection': FieldReflection[DynamicLightParent](
            DynamicLightParent, id=0xf734df8c, original_name='Parent', from_json=DynamicLightParent.from_json, to_json=DynamicLightParent.to_json
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
        return 'DLHT'

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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fc4e336
        light_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e8b3b2f
        light_set = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37c7d09d
        color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x72531ede
        intensity = DynamicLightIntensity.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x219b52da
        falloff = DynamicLightFalloff.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9546f449
        spotlight = DynamicLightSpotlight.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14322138
        motion_spline = DynamicLightMotionSpline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf734df8c
        parent = DynamicLightParent.from_stream(data, property_size)
    
        return cls(editor_properties, light_type, light_set, color, intensity, falloff, spotlight, motion_spline, parent)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\t')  # 9 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x7f\xc4\xe36')  # 0x7fc4e336
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.light_type))

        data.write(b'>\x8b;/')  # 0x3e8b3b2f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.light_set))

        data.write(b'7\xc7\xd0\x9d')  # 0x37c7d09d
        data.write(b'\x00\x10')  # size
        self.color.to_stream(data)

        data.write(b'rS\x1e\xde')  # 0x72531ede
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.intensity.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'!\x9bR\xda')  # 0x219b52da
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.falloff.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95F\xf4I')  # 0x9546f449
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.spotlight.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x142!8')  # 0x14322138
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion_spline.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf74\xdf\x8c')  # 0xf734df8c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.parent.to_stream(data)
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
        json_data = typing.cast("DynamicLightJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            light_type=json_data['light_type'],
            light_set=json_data['light_set'],
            color=Color.from_json(json_data['color']),
            intensity=DynamicLightIntensity.from_json(json_data['intensity']),
            falloff=DynamicLightFalloff.from_json(json_data['falloff']),
            spotlight=DynamicLightSpotlight.from_json(json_data['spotlight']),
            motion_spline=DynamicLightMotionSpline.from_json(json_data['motion_spline']),
            parent=DynamicLightParent.from_json(json_data['parent']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'light_type': self.light_type,
            'light_set': self.light_set,
            'color': self.color.to_json(),
            'intensity': self.intensity.to_json(),
            'falloff': self.falloff.to_json(),
            'spotlight': self.spotlight.to_json(),
            'motion_spline': self.motion_spline.to_json(),
            'parent': self.parent.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.intensity.dependencies_for, "intensity", "DynamicLightIntensity"),
            (self.falloff.dependencies_for, "falloff", "DynamicLightFalloff"),
            (self.spotlight.dependencies_for, "spotlight", "DynamicLightSpotlight"),
            (self.motion_spline.dependencies_for, "motion_spline", "DynamicLightMotionSpline"),
            (self.parent.dependencies_for, "parent", "DynamicLightParent"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for DynamicLight.{field_name} ({field_type}): {e}"
                )


def _decode_light_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_light_set(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x7fc4e336: ('light_type', _decode_light_type),
    0x3e8b3b2f: ('light_set', _decode_light_set),
    0x37c7d09d: ('color', _decode_color),
    0x72531ede: ('intensity', DynamicLightIntensity.from_stream),
    0x219b52da: ('falloff', DynamicLightFalloff.from_stream),
    0x9546f449: ('spotlight', DynamicLightSpotlight.from_stream),
    0x14322138: ('motion_spline', DynamicLightMotionSpline.from_stream),
    0xf734df8c: ('parent', DynamicLightParent.from_stream),
}
