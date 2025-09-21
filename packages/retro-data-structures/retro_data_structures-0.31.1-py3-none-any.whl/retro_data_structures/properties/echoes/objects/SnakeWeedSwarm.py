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
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SnakeWeedSwarmJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        animation_information: json_util.JsonObject
        actor_information: json_util.JsonObject
        density: float
        max_depth: float
        location_variance: float
        detection_radius: float
        grab_radius: float
        unknown_0x723737bc: float
        unknown_0x57452dd9: float
        retreat_depth: float
        move_speed: float
        unknown_0x11f854e2: float
        max_slope: float
        min_size: float
        max_size: float
        height_offset: float
        contact_damage: json_util.JsonObject
        damage_wait_time: float
        sound_looped: int
        sound_into_ground: int
        sound_outof_ground: int
    

@dataclasses.dataclass()
class SnakeWeedSwarm(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    animation_information: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0xe25fb08c, original_name='AnimationInformation', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    density: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x64e5fe9f, original_name='Density'
        ),
    })
    max_depth: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x23cef95f, original_name='MaxDepth'
        ),
    })
    location_variance: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbe02e456, original_name='LocationVariance'
        ),
    })
    detection_radius: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x21cdcf21, original_name='DetectionRadius'
        ),
    })
    grab_radius: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x89664723, original_name='GrabRadius'
        ),
    })
    unknown_0x723737bc: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x723737bc, original_name='Unknown'
        ),
    })
    unknown_0x57452dd9: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x57452dd9, original_name='Unknown'
        ),
    })
    retreat_depth: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5c20b0c7, original_name='RetreatDepth'
        ),
    })
    move_speed: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6497c750, original_name='MoveSpeed'
        ),
    })
    unknown_0x11f854e2: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x11f854e2, original_name='Unknown'
        ),
    })
    max_slope: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa755c1df, original_name='MaxSlope'
        ),
    })
    min_size: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x558c6dd7, original_name='MinSize'
        ),
    })
    max_size: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc5ff7d3d, original_name='MaxSize'
        ),
    })
    height_offset: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb2ebc23a, original_name='HeightOffset'
        ),
    })
    contact_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd756416e, original_name='ContactDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_wait_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe0cdc7e3, original_name='DamageWaitTime'
        ),
    })
    sound_looped: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xcd7d996e, original_name='Sound_Looped'
        ),
    })
    sound_into_ground: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x1026db89, original_name='Sound_IntoGround'
        ),
    })
    sound_outof_ground: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xcde17346, original_name='Sound_OutofGround'
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
        return 'SNAK'

    @classmethod
    def modules(cls) -> list[str]:
        return ['SnakeWeedSwarm.rel']

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
        if property_count != 22:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe25fb08c
        animation_information = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x64e5fe9f
        density = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x23cef95f
        max_depth = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe02e456
        location_variance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21cdcf21
        detection_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x89664723
        grab_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x723737bc
        unknown_0x723737bc = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x57452dd9
        unknown_0x57452dd9 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c20b0c7
        retreat_depth = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6497c750
        move_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x11f854e2
        unknown_0x11f854e2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa755c1df
        max_slope = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x558c6dd7
        min_size = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc5ff7d3d
        max_size = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2ebc23a
        height_offset = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd756416e
        contact_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 9})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0cdc7e3
        damage_wait_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcd7d996e
        sound_looped = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1026db89
        sound_into_ground = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcde17346
        sound_outof_ground = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, animation_information, actor_information, density, max_depth, location_variance, detection_radius, grab_radius, unknown_0x723737bc, unknown_0x57452dd9, retreat_depth, move_speed, unknown_0x11f854e2, max_slope, min_size, max_size, height_offset, contact_damage, damage_wait_time, sound_looped, sound_into_ground, sound_outof_ground)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x16')  # 22 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe2_\xb0\x8c')  # 0xe25fb08c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'd\xe5\xfe\x9f')  # 0x64e5fe9f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.density))

        data.write(b'#\xce\xf9_')  # 0x23cef95f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_depth))

        data.write(b'\xbe\x02\xe4V')  # 0xbe02e456
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.location_variance))

        data.write(b'!\xcd\xcf!')  # 0x21cdcf21
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.detection_radius))

        data.write(b'\x89fG#')  # 0x89664723
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grab_radius))

        data.write(b'r77\xbc')  # 0x723737bc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x723737bc))

        data.write(b'WE-\xd9')  # 0x57452dd9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x57452dd9))

        data.write(b'\\ \xb0\xc7')  # 0x5c20b0c7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.retreat_depth))

        data.write(b'd\x97\xc7P')  # 0x6497c750
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.move_speed))

        data.write(b'\x11\xf8T\xe2')  # 0x11f854e2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x11f854e2))

        data.write(b'\xa7U\xc1\xdf')  # 0xa755c1df
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_slope))

        data.write(b'U\x8cm\xd7')  # 0x558c6dd7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_size))

        data.write(b'\xc5\xff}=')  # 0xc5ff7d3d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_size))

        data.write(b'\xb2\xeb\xc2:')  # 0xb2ebc23a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.height_offset))

        data.write(b'\xd7VAn')  # 0xd756416e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.contact_damage.to_stream(data, default_override={'di_weapon_type': 9})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe0\xcd\xc7\xe3')  # 0xe0cdc7e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_wait_time))

        data.write(b'\xcd}\x99n')  # 0xcd7d996e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_looped))

        data.write(b'\x10&\xdb\x89')  # 0x1026db89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_into_ground))

        data.write(b'\xcd\xe1sF')  # 0xcde17346
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_outof_ground))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SnakeWeedSwarmJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            animation_information=AnimationParameters.from_json(json_data['animation_information']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            density=json_data['density'],
            max_depth=json_data['max_depth'],
            location_variance=json_data['location_variance'],
            detection_radius=json_data['detection_radius'],
            grab_radius=json_data['grab_radius'],
            unknown_0x723737bc=json_data['unknown_0x723737bc'],
            unknown_0x57452dd9=json_data['unknown_0x57452dd9'],
            retreat_depth=json_data['retreat_depth'],
            move_speed=json_data['move_speed'],
            unknown_0x11f854e2=json_data['unknown_0x11f854e2'],
            max_slope=json_data['max_slope'],
            min_size=json_data['min_size'],
            max_size=json_data['max_size'],
            height_offset=json_data['height_offset'],
            contact_damage=DamageInfo.from_json(json_data['contact_damage']),
            damage_wait_time=json_data['damage_wait_time'],
            sound_looped=json_data['sound_looped'],
            sound_into_ground=json_data['sound_into_ground'],
            sound_outof_ground=json_data['sound_outof_ground'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'animation_information': self.animation_information.to_json(),
            'actor_information': self.actor_information.to_json(),
            'density': self.density,
            'max_depth': self.max_depth,
            'location_variance': self.location_variance,
            'detection_radius': self.detection_radius,
            'grab_radius': self.grab_radius,
            'unknown_0x723737bc': self.unknown_0x723737bc,
            'unknown_0x57452dd9': self.unknown_0x57452dd9,
            'retreat_depth': self.retreat_depth,
            'move_speed': self.move_speed,
            'unknown_0x11f854e2': self.unknown_0x11f854e2,
            'max_slope': self.max_slope,
            'min_size': self.min_size,
            'max_size': self.max_size,
            'height_offset': self.height_offset,
            'contact_damage': self.contact_damage.to_json(),
            'damage_wait_time': self.damage_wait_time,
            'sound_looped': self.sound_looped,
            'sound_into_ground': self.sound_into_ground,
            'sound_outof_ground': self.sound_outof_ground,
        }

    def _dependencies_for_sound_looped(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_looped)

    def _dependencies_for_sound_into_ground(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_into_ground)

    def _dependencies_for_sound_outof_ground(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_outof_ground)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.animation_information.dependencies_for, "animation_information", "AnimationParameters"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self.contact_damage.dependencies_for, "contact_damage", "DamageInfo"),
            (self._dependencies_for_sound_looped, "sound_looped", "int"),
            (self._dependencies_for_sound_into_ground, "sound_into_ground", "int"),
            (self._dependencies_for_sound_outof_ground, "sound_outof_ground", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SnakeWeedSwarm.{field_name} ({field_type}): {e}"
                )


def _decode_density(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_depth(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_location_variance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_detection_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grab_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x723737bc(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x57452dd9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_retreat_depth(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_move_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x11f854e2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_slope(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_size(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_size(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_height_offset(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_contact_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 9})


def _decode_damage_wait_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_looped(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_into_ground(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_outof_ground(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xe25fb08c: ('animation_information', AnimationParameters.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x64e5fe9f: ('density', _decode_density),
    0x23cef95f: ('max_depth', _decode_max_depth),
    0xbe02e456: ('location_variance', _decode_location_variance),
    0x21cdcf21: ('detection_radius', _decode_detection_radius),
    0x89664723: ('grab_radius', _decode_grab_radius),
    0x723737bc: ('unknown_0x723737bc', _decode_unknown_0x723737bc),
    0x57452dd9: ('unknown_0x57452dd9', _decode_unknown_0x57452dd9),
    0x5c20b0c7: ('retreat_depth', _decode_retreat_depth),
    0x6497c750: ('move_speed', _decode_move_speed),
    0x11f854e2: ('unknown_0x11f854e2', _decode_unknown_0x11f854e2),
    0xa755c1df: ('max_slope', _decode_max_slope),
    0x558c6dd7: ('min_size', _decode_min_size),
    0xc5ff7d3d: ('max_size', _decode_max_size),
    0xb2ebc23a: ('height_offset', _decode_height_offset),
    0xd756416e: ('contact_damage', _decode_contact_damage),
    0xe0cdc7e3: ('damage_wait_time', _decode_damage_wait_time),
    0xcd7d996e: ('sound_looped', _decode_sound_looped),
    0x1026db89: ('sound_into_ground', _decode_sound_into_ground),
    0xcde17346: ('sound_outof_ground', _decode_sound_outof_ground),
}
