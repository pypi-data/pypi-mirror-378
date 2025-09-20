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
from retro_data_structures.properties.echoes.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DebrisJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        impulse: float
        impulse_variance: json_util.JsonValue
        fade_out_color: json_util.JsonValue
        mass: float
        unknown_0x417f4a91: float
        life_time: float
        scale_type: int
        random_spin: bool
        model: int
        actor_information: json_util.JsonObject
        particle: int
        particle_system_scale: json_util.JsonValue
        is_collider: bool
        unknown_0x4edb1d0e: bool
    

@dataclasses.dataclass()
class Debris(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    impulse: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf3a724ef, original_name='Impulse'
        ),
    })
    impulse_variance: Vector = dataclasses.field(default_factory=lambda: Vector(x=20.0, y=20.0, z=25.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x32fbb512, original_name='ImpulseVariance', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    fade_out_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd82ad573, original_name='FadeOutColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    mass: float = dataclasses.field(default=12.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75dbb375, original_name='Mass'
        ),
    })
    unknown_0x417f4a91: float = dataclasses.field(default=0.375, metadata={
        'reflection': FieldReflection[float](
            float, id=0x417f4a91, original_name='Unknown'
        ),
    })
    life_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb02de555, original_name='LifeTime'
        ),
    })
    scale_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x71829ad6, original_name='ScaleType'
        ),
    })
    random_spin: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xdd17b34f, original_name='RandomSpin'
        ),
    })
    model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc27ffa8f, original_name='Model'
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6d1ce525, original_name='Particle'
        ),
    })
    particle_system_scale: Vector = dataclasses.field(default_factory=lambda: Vector(x=1.0, y=1.0, z=1.0), metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x18bc419e, original_name='ParticleSystemScale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    is_collider: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2c7b18dd, original_name='IsCollider'
        ),
    })
    unknown_0x4edb1d0e: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x4edb1d0e, original_name='Unknown'
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
        return 'DBR1'

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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size, default_override={'active': False})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3a724ef
        impulse = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x32fbb512
        impulse_variance = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd82ad573
        fade_out_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x75dbb375
        mass = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x417f4a91
        unknown_0x417f4a91 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb02de555
        life_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71829ad6
        scale_type = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd17b34f
        random_spin = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc27ffa8f
        model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d1ce525
        particle = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x18bc419e
        particle_system_scale = Vector.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2c7b18dd
        is_collider = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4edb1d0e
        unknown_0x4edb1d0e = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, impulse, impulse_variance, fade_out_color, mass, unknown_0x417f4a91, life_time, scale_type, random_spin, model, actor_information, particle, particle_system_scale, is_collider, unknown_0x4edb1d0e)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data, default_override={'active': False})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf3\xa7$\xef')  # 0xf3a724ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.impulse))

        data.write(b'2\xfb\xb5\x12')  # 0x32fbb512
        data.write(b'\x00\x0c')  # size
        self.impulse_variance.to_stream(data)

        data.write(b'\xd8*\xd5s')  # 0xd82ad573
        data.write(b'\x00\x10')  # size
        self.fade_out_color.to_stream(data)

        data.write(b'u\xdb\xb3u')  # 0x75dbb375
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.mass))

        data.write(b'A\x7fJ\x91')  # 0x417f4a91
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x417f4a91))

        data.write(b'\xb0-\xe5U')  # 0xb02de555
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.life_time))

        data.write(b'q\x82\x9a\xd6')  # 0x71829ad6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.scale_type))

        data.write(b'\xdd\x17\xb3O')  # 0xdd17b34f
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.random_spin))

        data.write(b'\xc2\x7f\xfa\x8f')  # 0xc27ffa8f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.model))

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'm\x1c\xe5%')  # 0x6d1ce525
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.particle))

        data.write(b'\x18\xbcA\x9e')  # 0x18bc419e
        data.write(b'\x00\x0c')  # size
        self.particle_system_scale.to_stream(data)

        data.write(b',{\x18\xdd')  # 0x2c7b18dd
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_collider))

        data.write(b'N\xdb\x1d\x0e')  # 0x4edb1d0e
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x4edb1d0e))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DebrisJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            impulse=json_data['impulse'],
            impulse_variance=Vector.from_json(json_data['impulse_variance']),
            fade_out_color=Color.from_json(json_data['fade_out_color']),
            mass=json_data['mass'],
            unknown_0x417f4a91=json_data['unknown_0x417f4a91'],
            life_time=json_data['life_time'],
            scale_type=json_data['scale_type'],
            random_spin=json_data['random_spin'],
            model=json_data['model'],
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            particle=json_data['particle'],
            particle_system_scale=Vector.from_json(json_data['particle_system_scale']),
            is_collider=json_data['is_collider'],
            unknown_0x4edb1d0e=json_data['unknown_0x4edb1d0e'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'impulse': self.impulse,
            'impulse_variance': self.impulse_variance.to_json(),
            'fade_out_color': self.fade_out_color.to_json(),
            'mass': self.mass,
            'unknown_0x417f4a91': self.unknown_0x417f4a91,
            'life_time': self.life_time,
            'scale_type': self.scale_type,
            'random_spin': self.random_spin,
            'model': self.model,
            'actor_information': self.actor_information.to_json(),
            'particle': self.particle,
            'particle_system_scale': self.particle_system_scale.to_json(),
            'is_collider': self.is_collider,
            'unknown_0x4edb1d0e': self.unknown_0x4edb1d0e,
        }

    def _dependencies_for_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model)

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self._dependencies_for_model, "model", "AssetId"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_particle, "particle", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Debris.{field_name} ({field_type}): {e}"
                )


def _decode_editor_properties(data: typing.BinaryIO, property_size: int) -> EditorProperties:
    return EditorProperties.from_stream(data, property_size, default_override={'active': False})


def _decode_impulse(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_impulse_variance(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_fade_out_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_mass(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x417f4a91(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_life_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scale_type(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_random_spin(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_particle(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_particle_system_scale(data: typing.BinaryIO, property_size: int) -> Vector:
    return Vector.from_stream(data)


def _decode_is_collider(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x4edb1d0e(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', _decode_editor_properties),
    0xf3a724ef: ('impulse', _decode_impulse),
    0x32fbb512: ('impulse_variance', _decode_impulse_variance),
    0xd82ad573: ('fade_out_color', _decode_fade_out_color),
    0x75dbb375: ('mass', _decode_mass),
    0x417f4a91: ('unknown_0x417f4a91', _decode_unknown_0x417f4a91),
    0xb02de555: ('life_time', _decode_life_time),
    0x71829ad6: ('scale_type', _decode_scale_type),
    0xdd17b34f: ('random_spin', _decode_random_spin),
    0xc27ffa8f: ('model', _decode_model),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x6d1ce525: ('particle', _decode_particle),
    0x18bc419e: ('particle_system_scale', _decode_particle_system_scale),
    0x2c7b18dd: ('is_collider', _decode_is_collider),
    0x4edb1d0e: ('unknown_0x4edb1d0e', _decode_unknown_0x4edb1d0e),
}
