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

    class PuddleSporeJson(typing_extensions.TypedDict):
        name: str
        unknown_1: int
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed_0x00000005: json_util.JsonObject
        unnamed_0x00000006: json_util.JsonObject
        unknown_2: bool
        particle: int
        unknown_3: float
        unknown_4: float
        unknown_5: float
        unknown_6: float
        unknown_7: float
        wpsc: int
        unnamed_0x0000000f: json_util.JsonObject
    

@dataclasses.dataclass()
class PuddleSpore(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    unknown_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000001, original_name='Unknown 1'
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
    unknown_2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000007, original_name='Unknown 2'
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000008, original_name='Particle'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000009, original_name='Unknown 3'
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000a, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000b, original_name='Unknown 5'
        ),
    })
    unknown_6: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000c, original_name='Unknown 6'
        ),
    })
    unknown_7: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000000d, original_name='Unknown 7'
        ),
    })
    wpsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000e, original_name='WPSC'
        ),
    })
    unnamed_0x0000000f: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000000f, original_name='15', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
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
        return 0x31

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        unknown_1 = struct.unpack('>l', data.read(4))[0]
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed_0x00000005 = PatternedAITypedef.from_stream(data, property_size)
        unnamed_0x00000006 = ActorParameters.from_stream(data, property_size)
        unknown_2 = struct.unpack('>?', data.read(1))[0]
        particle = struct.unpack(">L", data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>f', data.read(4))[0]
        unknown_7 = struct.unpack('>f', data.read(4))[0]
        wpsc = struct.unpack(">L", data.read(4))[0]
        unnamed_0x0000000f = DamageInfo.from_stream(data, property_size)
        return cls(name, unknown_1, position, rotation, scale, unnamed_0x00000005, unnamed_0x00000006, unknown_2, particle, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, wpsc, unnamed_0x0000000f)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x10')  # 16 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        data.write(struct.pack('>l', self.unknown_1))
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed_0x00000005.to_stream(data)
        self.unnamed_0x00000006.to_stream(data)
        data.write(struct.pack('>?', self.unknown_2))
        data.write(struct.pack(">L", self.particle))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>f', self.unknown_6))
        data.write(struct.pack('>f', self.unknown_7))
        data.write(struct.pack(">L", self.wpsc))
        self.unnamed_0x0000000f.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PuddleSporeJson", data)
        return cls(
            name=json_data['name'],
            unknown_1=json_data['unknown_1'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unnamed_0x00000005=PatternedAITypedef.from_json(json_data['unnamed_0x00000005']),
            unnamed_0x00000006=ActorParameters.from_json(json_data['unnamed_0x00000006']),
            unknown_2=json_data['unknown_2'],
            particle=json_data['particle'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            wpsc=json_data['wpsc'],
            unnamed_0x0000000f=DamageInfo.from_json(json_data['unnamed_0x0000000f']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'unknown_1': self.unknown_1,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unnamed_0x00000005': self.unnamed_0x00000005.to_json(),
            'unnamed_0x00000006': self.unnamed_0x00000006.to_json(),
            'unknown_2': self.unknown_2,
            'particle': self.particle,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'wpsc': self.wpsc,
            'unnamed_0x0000000f': self.unnamed_0x0000000f.to_json(),
        }

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def _dependencies_for_wpsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000005.dependencies_for, "unnamed_0x00000005", "PatternedAITypedef"),
            (self.unnamed_0x00000006.dependencies_for, "unnamed_0x00000006", "ActorParameters"),
            (self._dependencies_for_particle, "particle", "AssetId"),
            (self._dependencies_for_wpsc, "wpsc", "AssetId"),
            (self.unnamed_0x0000000f.dependencies_for, "unnamed_0x0000000f", "DamageInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PuddleSpore.{field_name} ({field_type}): {e}"
                )
