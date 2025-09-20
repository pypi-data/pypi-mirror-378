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
from retro_data_structures.properties.prime.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.prime.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.prime.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class WarWaspJson(typing_extensions.TypedDict):
        name: str
        patterned_flavor_type: int
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed_0x00000005: json_util.JsonObject
        unnamed_0x00000006: json_util.JsonObject
        collider: bool
        damage_info_1: json_util.JsonObject
        wpsc: int
        damage_info_2: json_util.JsonObject
        particle: int
        unknown_3: int
    

@dataclasses.dataclass()
class WarWasp(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    patterned_flavor_type: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000001, original_name='Patterned Flavor Type'
        ),
    })
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    rotation: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000003, original_name='Rotation', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000004, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unnamed_0x00000005: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x00000005, original_name='5', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    unnamed_0x00000006: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000006, original_name='6', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    collider: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000007, original_name='Collider'
        ),
    })
    damage_info_1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000008, original_name='DamageInfo 1', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    wpsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000009, original_name='WPSC'
        ),
    })
    damage_info_2: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000a, original_name='DamageInfo 2', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000b, original_name='Particle'
        ),
    })
    unknown_3: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x0000000c, original_name='Unknown 3'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    @classmethod
    def object_type(cls) -> int:
        return 0x21

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        patterned_flavor_type = struct.unpack('>l', data.read(4))[0]
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed_0x00000005 = PatternedAITypedef.from_stream(data, property_size)
        unnamed_0x00000006 = ActorParameters.from_stream(data, property_size)
        collider = struct.unpack('>?', data.read(1))[0]
        damage_info_1 = DamageInfo.from_stream(data, property_size)
        wpsc = struct.unpack(">L", data.read(4))[0]
        damage_info_2 = DamageInfo.from_stream(data, property_size)
        particle = struct.unpack(">L", data.read(4))[0]
        unknown_3 = struct.unpack('>l', data.read(4))[0]
        return cls(name, patterned_flavor_type, position, rotation, scale, unnamed_0x00000005, unnamed_0x00000006, collider, damage_info_1, wpsc, damage_info_2, particle, unknown_3)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\r')  # 13 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>l', self.patterned_flavor_type))
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed_0x00000005.to_stream(data)
        self.unnamed_0x00000006.to_stream(data)
        data.write(struct.pack('>?', self.collider))
        self.damage_info_1.to_stream(data)
        data.write(struct.pack(">L", self.wpsc))
        self.damage_info_2.to_stream(data)
        data.write(struct.pack(">L", self.particle))
        data.write(struct.pack('>l', self.unknown_3))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("WarWaspJson", data)
        return cls(
            name=json_data['name'],
            patterned_flavor_type=json_data['patterned_flavor_type'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unnamed_0x00000005=PatternedAITypedef.from_json(json_data['unnamed_0x00000005']),
            unnamed_0x00000006=ActorParameters.from_json(json_data['unnamed_0x00000006']),
            collider=json_data['collider'],
            damage_info_1=DamageInfo.from_json(json_data['damage_info_1']),
            wpsc=json_data['wpsc'],
            damage_info_2=DamageInfo.from_json(json_data['damage_info_2']),
            particle=json_data['particle'],
            unknown_3=json_data['unknown_3'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'patterned_flavor_type': self.patterned_flavor_type,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unnamed_0x00000005': self.unnamed_0x00000005.to_json(),
            'unnamed_0x00000006': self.unnamed_0x00000006.to_json(),
            'collider': self.collider,
            'damage_info_1': self.damage_info_1.to_json(),
            'wpsc': self.wpsc,
            'damage_info_2': self.damage_info_2.to_json(),
            'particle': self.particle,
            'unknown_3': self.unknown_3,
        }

    def _dependencies_for_wpsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc)

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def _dependencies_for_unknown_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.unknown_3)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000005.dependencies_for, "unnamed_0x00000005", "PatternedAITypedef"),
            (self.unnamed_0x00000006.dependencies_for, "unnamed_0x00000006", "ActorParameters"),
            (self.damage_info_1.dependencies_for, "damage_info_1", "DamageInfo"),
            (self._dependencies_for_wpsc, "wpsc", "AssetId"),
            (self.damage_info_2.dependencies_for, "damage_info_2", "DamageInfo"),
            (self._dependencies_for_particle, "particle", "AssetId"),
            (self._dependencies_for_unknown_3, "unknown_3", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for WarWasp.{field_name} ({field_type}): {e}"
                )
