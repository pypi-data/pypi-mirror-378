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
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class RiftPortalJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        model: int
        animation_information: json_util.JsonObject
        background_model: int
        background_animation: json_util.JsonObject
        incandescent_model: int
        incandescent_animation: json_util.JsonObject
        line_model: int
        line_animation: json_util.JsonObject
        rip_portal: bool
        projectile_attraction: int
        projectile_box_width: float
        projectile_angle: float
        projectile_destruction_radius: float
    

@dataclasses.dataclass()
class RiftPortal(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc27ffa8f, original_name='Model'
        ),
    })
    animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xe25fb08c, original_name='AnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    background_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x90c42387, original_name='BackgroundModel'
        ),
    })
    background_animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x80c6a38d, original_name='BackgroundAnimation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    incandescent_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xa71696b0, original_name='IncandescentModel'
        ),
    })
    incandescent_animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x5cb18eb4, original_name='IncandescentAnimation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    line_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf284d838, original_name='LineModel'
        ),
    })
    line_animation: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xe845fa67, original_name='LineAnimation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    rip_portal: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xf5b73af8, original_name='RipPortal'
        ),
    })
    projectile_attraction: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x87d5a35f, original_name='ProjectileAttraction'
        ),
    })
    projectile_box_width: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x709c1413, original_name='ProjectileBoxWidth'
        ),
    })
    projectile_angle: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3b692a03, original_name='ProjectileAngle'
        ),
    })
    projectile_destruction_radius: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe1e5551f, original_name='ProjectileDestructionRadius'
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
        return 'RPTL'

    @classmethod
    def modules(cls) -> list[str]:
        return ['ScriptRiftPortal.rel']

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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc27ffa8f
        model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe25fb08c
        animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90c42387
        background_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80c6a38d
        background_animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa71696b0
        incandescent_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5cb18eb4
        incandescent_animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf284d838
        line_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe845fa67
        line_animation = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5b73af8
        rip_portal = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87d5a35f
        projectile_attraction = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x709c1413
        projectile_box_width = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3b692a03
        projectile_angle = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe1e5551f
        projectile_destruction_radius = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, model, animation_information, background_model, background_animation, incandescent_model, incandescent_animation, line_model, line_animation, rip_portal, projectile_attraction, projectile_box_width, projectile_angle, projectile_destruction_radius)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc2\x7f\xfa\x8f')  # 0xc27ffa8f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.model))

        data.write(b'\xe2_\xb0\x8c')  # 0xe25fb08c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x90\xc4#\x87')  # 0x90c42387
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.background_model))

        data.write(b'\x80\xc6\xa3\x8d')  # 0x80c6a38d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.background_animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa7\x16\x96\xb0')  # 0xa71696b0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.incandescent_model))

        data.write(b'\\\xb1\x8e\xb4')  # 0x5cb18eb4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.incandescent_animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf2\x84\xd88')  # 0xf284d838
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.line_model))

        data.write(b'\xe8E\xfag')  # 0xe845fa67
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.line_animation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf5\xb7:\xf8')  # 0xf5b73af8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.rip_portal))

        data.write(b'\x87\xd5\xa3_')  # 0x87d5a35f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.projectile_attraction))

        data.write(b'p\x9c\x14\x13')  # 0x709c1413
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_box_width))

        data.write(b';i*\x03')  # 0x3b692a03
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_angle))

        data.write(b'\xe1\xe5U\x1f')  # 0xe1e5551f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.projectile_destruction_radius))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RiftPortalJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            model=json_data['model'],
            animation_information=AnimationParameters.from_json(json_data['animation_information']),
            background_model=json_data['background_model'],
            background_animation=AnimationParameters.from_json(json_data['background_animation']),
            incandescent_model=json_data['incandescent_model'],
            incandescent_animation=AnimationParameters.from_json(json_data['incandescent_animation']),
            line_model=json_data['line_model'],
            line_animation=AnimationParameters.from_json(json_data['line_animation']),
            rip_portal=json_data['rip_portal'],
            projectile_attraction=json_data['projectile_attraction'],
            projectile_box_width=json_data['projectile_box_width'],
            projectile_angle=json_data['projectile_angle'],
            projectile_destruction_radius=json_data['projectile_destruction_radius'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'model': self.model,
            'animation_information': self.animation_information.to_json(),
            'background_model': self.background_model,
            'background_animation': self.background_animation.to_json(),
            'incandescent_model': self.incandescent_model,
            'incandescent_animation': self.incandescent_animation.to_json(),
            'line_model': self.line_model,
            'line_animation': self.line_animation.to_json(),
            'rip_portal': self.rip_portal,
            'projectile_attraction': self.projectile_attraction,
            'projectile_box_width': self.projectile_box_width,
            'projectile_angle': self.projectile_angle,
            'projectile_destruction_radius': self.projectile_destruction_radius,
        }

    def _dependencies_for_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model)

    def _dependencies_for_background_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.background_model)

    def _dependencies_for_incandescent_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.incandescent_model)

    def _dependencies_for_line_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.line_model)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self._dependencies_for_model, "model", "AssetId"),
            (self.animation_information.dependencies_for, "animation_information", "AnimationParameters"),
            (self._dependencies_for_background_model, "background_model", "AssetId"),
            (self.background_animation.dependencies_for, "background_animation", "AnimationParameters"),
            (self._dependencies_for_incandescent_model, "incandescent_model", "AssetId"),
            (self.incandescent_animation.dependencies_for, "incandescent_animation", "AnimationParameters"),
            (self._dependencies_for_line_model, "line_model", "AssetId"),
            (self.line_animation.dependencies_for, "line_animation", "AnimationParameters"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for RiftPortal.{field_name} ({field_type}): {e}"
                )


def _decode_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_background_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_incandescent_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_line_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_rip_portal(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_projectile_attraction(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_projectile_box_width(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_projectile_destruction_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xc27ffa8f: ('model', _decode_model),
    0xe25fb08c: ('animation_information', AnimationParameters.from_stream),
    0x90c42387: ('background_model', _decode_background_model),
    0x80c6a38d: ('background_animation', AnimationParameters.from_stream),
    0xa71696b0: ('incandescent_model', _decode_incandescent_model),
    0x5cb18eb4: ('incandescent_animation', AnimationParameters.from_stream),
    0xf284d838: ('line_model', _decode_line_model),
    0xe845fa67: ('line_animation', AnimationParameters.from_stream),
    0xf5b73af8: ('rip_portal', _decode_rip_portal),
    0x87d5a35f: ('projectile_attraction', _decode_projectile_attraction),
    0x709c1413: ('projectile_box_width', _decode_projectile_box_width),
    0x3b692a03: ('projectile_angle', _decode_projectile_angle),
    0xe1e5551f: ('projectile_destruction_radius', _decode_projectile_destruction_radius),
}
