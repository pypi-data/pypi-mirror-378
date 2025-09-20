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
from retro_data_structures.properties.prime.archetypes.RidleyStruct1 import RidleyStruct1
from retro_data_structures.properties.prime.archetypes.RidleyStruct2 import RidleyStruct2
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class RidleyJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed_0x00000004: json_util.JsonObject
        unnamed_0x00000005: json_util.JsonObject
        model_1: int
        model_2: int
        model_3: int
        model_4: int
        model_5: int
        model_6: int
        model_7: int
        model_8: int
        model_9: int
        model_10: int
        model_11: int
        model_12: int
        particle: int
        unknown_1: float
        unknown_2: float
        unknown_3: float
        unknown_4: float
        wpsc_1: int
        damage_info_1: json_util.JsonObject
        unnamed_0x00000019: json_util.JsonObject
        sound_id_1: int
        wpsc_2: int
        damage_info_2: json_util.JsonObject
        ridley_struct2_1: json_util.JsonObject
        wpsc_3: int
        damage_info_3: json_util.JsonObject
        ridley_struct2_2: json_util.JsonObject
        sound_id_2: int
        damage_info_4: json_util.JsonObject
        ridley_struct2_3: json_util.JsonObject
        unknown_18: float
        unknown_19: float
        damage_info_5: json_util.JsonObject
        unknown_20: float
        damage_info_6: json_util.JsonObject
        unknown_21: float
        damage_info_7: json_util.JsonObject
        unknown_22: float
        elsc: int
        unknown_23: float
        sound_id_3: int
        damage_info_8: json_util.JsonObject
    

@dataclasses.dataclass()
class Ridley(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000001, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    rotation: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Rotation', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000003, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unnamed_0x00000004: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x00000004, original_name='4', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    unnamed_0x00000005: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x00000005, original_name='5', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    model_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000006, original_name='Model 1'
        ),
    })
    model_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000007, original_name='Model 2'
        ),
    })
    model_3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000008, original_name='Model 3'
        ),
    })
    model_4: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000009, original_name='Model 4'
        ),
    })
    model_5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000a, original_name='Model 5'
        ),
    })
    model_6: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000b, original_name='Model 6'
        ),
    })
    model_7: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000c, original_name='Model 7'
        ),
    })
    model_8: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000d, original_name='Model 8'
        ),
    })
    model_9: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000e, original_name='Model 9'
        ),
    })
    model_10: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000000f, original_name='Model 10'
        ),
    })
    model_11: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000010, original_name='Model 11'
        ),
    })
    model_12: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000011, original_name='Model 12'
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000012, original_name='Particle'
        ),
    })
    unknown_1: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000013, original_name='Unknown 1'
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000014, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000015, original_name='Unknown 3'
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000016, original_name='Unknown 4'
        ),
    })
    wpsc_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000017, original_name='WPSC 1'
        ),
    })
    damage_info_1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000018, original_name='DamageInfo 1', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unnamed_0x00000019: RidleyStruct1 = dataclasses.field(default_factory=RidleyStruct1, metadata={
        'reflection': FieldReflection[RidleyStruct1](
            RidleyStruct1, id=0x00000019, original_name='25', from_json=RidleyStruct1.from_json, to_json=RidleyStruct1.to_json
        ),
    })
    sound_id_1: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x0000001a, original_name='Sound ID 1'
        ),
    })
    wpsc_2: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001b, original_name='WPSC 2'
        ),
    })
    damage_info_2: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000001c, original_name='DamageInfo 2', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    ridley_struct2_1: RidleyStruct2 = dataclasses.field(default_factory=RidleyStruct2, metadata={
        'reflection': FieldReflection[RidleyStruct2](
            RidleyStruct2, id=0x0000001d, original_name='RidleyStruct2 1', from_json=RidleyStruct2.from_json, to_json=RidleyStruct2.to_json
        ),
    })
    wpsc_3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000001e, original_name='WPSC 3'
        ),
    })
    damage_info_3: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000001f, original_name='DamageInfo 3', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    ridley_struct2_2: RidleyStruct2 = dataclasses.field(default_factory=RidleyStruct2, metadata={
        'reflection': FieldReflection[RidleyStruct2](
            RidleyStruct2, id=0x00000020, original_name='RidleyStruct2 2', from_json=RidleyStruct2.from_json, to_json=RidleyStruct2.to_json
        ),
    })
    sound_id_2: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x00000021, original_name='Sound ID 2'
        ),
    })
    damage_info_4: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000022, original_name='DamageInfo 4', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    ridley_struct2_3: RidleyStruct2 = dataclasses.field(default_factory=RidleyStruct2, metadata={
        'reflection': FieldReflection[RidleyStruct2](
            RidleyStruct2, id=0x00000023, original_name='RidleyStruct2 3', from_json=RidleyStruct2.from_json, to_json=RidleyStruct2.to_json
        ),
    })
    unknown_18: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000024, original_name='Unknown 18'
        ),
    })
    unknown_19: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000025, original_name='Unknown 19'
        ),
    })
    damage_info_5: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000026, original_name='DamageInfo 5', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_20: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000027, original_name='Unknown 20'
        ),
    })
    damage_info_6: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000028, original_name='DamageInfo 6', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_21: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000029, original_name='Unknown 21'
        ),
    })
    damage_info_7: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000002a, original_name='DamageInfo 7', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_22: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000002b, original_name='Unknown 22'
        ),
    })
    elsc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0000002c, original_name='ELSC'
        ),
    })
    unknown_23: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0000002d, original_name='Unknown 23'
        ),
    })
    sound_id_3: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x0000002e, original_name='Sound ID 3'
        ),
    })
    damage_info_8: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x0000002f, original_name='DamageInfo 8', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
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
        return 0x7B

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed_0x00000004 = PatternedAITypedef.from_stream(data, property_size)
        unnamed_0x00000005 = ActorParameters.from_stream(data, property_size)
        model_1 = struct.unpack(">L", data.read(4))[0]
        model_2 = struct.unpack(">L", data.read(4))[0]
        model_3 = struct.unpack(">L", data.read(4))[0]
        model_4 = struct.unpack(">L", data.read(4))[0]
        model_5 = struct.unpack(">L", data.read(4))[0]
        model_6 = struct.unpack(">L", data.read(4))[0]
        model_7 = struct.unpack(">L", data.read(4))[0]
        model_8 = struct.unpack(">L", data.read(4))[0]
        model_9 = struct.unpack(">L", data.read(4))[0]
        model_10 = struct.unpack(">L", data.read(4))[0]
        model_11 = struct.unpack(">L", data.read(4))[0]
        model_12 = struct.unpack(">L", data.read(4))[0]
        particle = struct.unpack(">L", data.read(4))[0]
        unknown_1 = struct.unpack('>f', data.read(4))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        wpsc_1 = struct.unpack(">L", data.read(4))[0]
        damage_info_1 = DamageInfo.from_stream(data, property_size)
        unnamed_0x00000019 = RidleyStruct1.from_stream(data, property_size)
        sound_id_1 = struct.unpack('>l', data.read(4))[0]
        wpsc_2 = struct.unpack(">L", data.read(4))[0]
        damage_info_2 = DamageInfo.from_stream(data, property_size)
        ridley_struct2_1 = RidleyStruct2.from_stream(data, property_size)
        wpsc_3 = struct.unpack(">L", data.read(4))[0]
        damage_info_3 = DamageInfo.from_stream(data, property_size)
        ridley_struct2_2 = RidleyStruct2.from_stream(data, property_size)
        sound_id_2 = struct.unpack('>l', data.read(4))[0]
        damage_info_4 = DamageInfo.from_stream(data, property_size)
        ridley_struct2_3 = RidleyStruct2.from_stream(data, property_size)
        unknown_18 = struct.unpack('>f', data.read(4))[0]
        unknown_19 = struct.unpack('>f', data.read(4))[0]
        damage_info_5 = DamageInfo.from_stream(data, property_size)
        unknown_20 = struct.unpack('>f', data.read(4))[0]
        damage_info_6 = DamageInfo.from_stream(data, property_size)
        unknown_21 = struct.unpack('>f', data.read(4))[0]
        damage_info_7 = DamageInfo.from_stream(data, property_size)
        unknown_22 = struct.unpack('>f', data.read(4))[0]
        elsc = struct.unpack(">L", data.read(4))[0]
        unknown_23 = struct.unpack('>f', data.read(4))[0]
        sound_id_3 = struct.unpack('>l', data.read(4))[0]
        damage_info_8 = DamageInfo.from_stream(data, property_size)
        return cls(name, position, rotation, scale, unnamed_0x00000004, unnamed_0x00000005, model_1, model_2, model_3, model_4, model_5, model_6, model_7, model_8, model_9, model_10, model_11, model_12, particle, unknown_1, unknown_2, unknown_3, unknown_4, wpsc_1, damage_info_1, unnamed_0x00000019, sound_id_1, wpsc_2, damage_info_2, ridley_struct2_1, wpsc_3, damage_info_3, ridley_struct2_2, sound_id_2, damage_info_4, ridley_struct2_3, unknown_18, unknown_19, damage_info_5, unknown_20, damage_info_6, unknown_21, damage_info_7, unknown_22, elsc, unknown_23, sound_id_3, damage_info_8)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x000')  # 48 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed_0x00000004.to_stream(data)
        self.unnamed_0x00000005.to_stream(data)
        data.write(struct.pack(">L", self.model_1))
        data.write(struct.pack(">L", self.model_2))
        data.write(struct.pack(">L", self.model_3))
        data.write(struct.pack(">L", self.model_4))
        data.write(struct.pack(">L", self.model_5))
        data.write(struct.pack(">L", self.model_6))
        data.write(struct.pack(">L", self.model_7))
        data.write(struct.pack(">L", self.model_8))
        data.write(struct.pack(">L", self.model_9))
        data.write(struct.pack(">L", self.model_10))
        data.write(struct.pack(">L", self.model_11))
        data.write(struct.pack(">L", self.model_12))
        data.write(struct.pack(">L", self.particle))
        data.write(struct.pack('>f', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack(">L", self.wpsc_1))
        self.damage_info_1.to_stream(data)
        self.unnamed_0x00000019.to_stream(data)
        data.write(struct.pack('>l', self.sound_id_1))
        data.write(struct.pack(">L", self.wpsc_2))
        self.damage_info_2.to_stream(data)
        self.ridley_struct2_1.to_stream(data)
        data.write(struct.pack(">L", self.wpsc_3))
        self.damage_info_3.to_stream(data)
        self.ridley_struct2_2.to_stream(data)
        data.write(struct.pack('>l', self.sound_id_2))
        self.damage_info_4.to_stream(data)
        self.ridley_struct2_3.to_stream(data)
        data.write(struct.pack('>f', self.unknown_18))
        data.write(struct.pack('>f', self.unknown_19))
        self.damage_info_5.to_stream(data)
        data.write(struct.pack('>f', self.unknown_20))
        self.damage_info_6.to_stream(data)
        data.write(struct.pack('>f', self.unknown_21))
        self.damage_info_7.to_stream(data)
        data.write(struct.pack('>f', self.unknown_22))
        data.write(struct.pack(">L", self.elsc))
        data.write(struct.pack('>f', self.unknown_23))
        data.write(struct.pack('>l', self.sound_id_3))
        self.damage_info_8.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RidleyJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unnamed_0x00000004=PatternedAITypedef.from_json(json_data['unnamed_0x00000004']),
            unnamed_0x00000005=ActorParameters.from_json(json_data['unnamed_0x00000005']),
            model_1=json_data['model_1'],
            model_2=json_data['model_2'],
            model_3=json_data['model_3'],
            model_4=json_data['model_4'],
            model_5=json_data['model_5'],
            model_6=json_data['model_6'],
            model_7=json_data['model_7'],
            model_8=json_data['model_8'],
            model_9=json_data['model_9'],
            model_10=json_data['model_10'],
            model_11=json_data['model_11'],
            model_12=json_data['model_12'],
            particle=json_data['particle'],
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            wpsc_1=json_data['wpsc_1'],
            damage_info_1=DamageInfo.from_json(json_data['damage_info_1']),
            unnamed_0x00000019=RidleyStruct1.from_json(json_data['unnamed_0x00000019']),
            sound_id_1=json_data['sound_id_1'],
            wpsc_2=json_data['wpsc_2'],
            damage_info_2=DamageInfo.from_json(json_data['damage_info_2']),
            ridley_struct2_1=RidleyStruct2.from_json(json_data['ridley_struct2_1']),
            wpsc_3=json_data['wpsc_3'],
            damage_info_3=DamageInfo.from_json(json_data['damage_info_3']),
            ridley_struct2_2=RidleyStruct2.from_json(json_data['ridley_struct2_2']),
            sound_id_2=json_data['sound_id_2'],
            damage_info_4=DamageInfo.from_json(json_data['damage_info_4']),
            ridley_struct2_3=RidleyStruct2.from_json(json_data['ridley_struct2_3']),
            unknown_18=json_data['unknown_18'],
            unknown_19=json_data['unknown_19'],
            damage_info_5=DamageInfo.from_json(json_data['damage_info_5']),
            unknown_20=json_data['unknown_20'],
            damage_info_6=DamageInfo.from_json(json_data['damage_info_6']),
            unknown_21=json_data['unknown_21'],
            damage_info_7=DamageInfo.from_json(json_data['damage_info_7']),
            unknown_22=json_data['unknown_22'],
            elsc=json_data['elsc'],
            unknown_23=json_data['unknown_23'],
            sound_id_3=json_data['sound_id_3'],
            damage_info_8=DamageInfo.from_json(json_data['damage_info_8']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unnamed_0x00000004': self.unnamed_0x00000004.to_json(),
            'unnamed_0x00000005': self.unnamed_0x00000005.to_json(),
            'model_1': self.model_1,
            'model_2': self.model_2,
            'model_3': self.model_3,
            'model_4': self.model_4,
            'model_5': self.model_5,
            'model_6': self.model_6,
            'model_7': self.model_7,
            'model_8': self.model_8,
            'model_9': self.model_9,
            'model_10': self.model_10,
            'model_11': self.model_11,
            'model_12': self.model_12,
            'particle': self.particle,
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'wpsc_1': self.wpsc_1,
            'damage_info_1': self.damage_info_1.to_json(),
            'unnamed_0x00000019': self.unnamed_0x00000019.to_json(),
            'sound_id_1': self.sound_id_1,
            'wpsc_2': self.wpsc_2,
            'damage_info_2': self.damage_info_2.to_json(),
            'ridley_struct2_1': self.ridley_struct2_1.to_json(),
            'wpsc_3': self.wpsc_3,
            'damage_info_3': self.damage_info_3.to_json(),
            'ridley_struct2_2': self.ridley_struct2_2.to_json(),
            'sound_id_2': self.sound_id_2,
            'damage_info_4': self.damage_info_4.to_json(),
            'ridley_struct2_3': self.ridley_struct2_3.to_json(),
            'unknown_18': self.unknown_18,
            'unknown_19': self.unknown_19,
            'damage_info_5': self.damage_info_5.to_json(),
            'unknown_20': self.unknown_20,
            'damage_info_6': self.damage_info_6.to_json(),
            'unknown_21': self.unknown_21,
            'damage_info_7': self.damage_info_7.to_json(),
            'unknown_22': self.unknown_22,
            'elsc': self.elsc,
            'unknown_23': self.unknown_23,
            'sound_id_3': self.sound_id_3,
            'damage_info_8': self.damage_info_8.to_json(),
        }

    def _dependencies_for_model_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_1)

    def _dependencies_for_model_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_2)

    def _dependencies_for_model_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_3)

    def _dependencies_for_model_4(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_4)

    def _dependencies_for_model_5(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_5)

    def _dependencies_for_model_6(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_6)

    def _dependencies_for_model_7(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_7)

    def _dependencies_for_model_8(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_8)

    def _dependencies_for_model_9(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_9)

    def _dependencies_for_model_10(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_10)

    def _dependencies_for_model_11(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_11)

    def _dependencies_for_model_12(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.model_12)

    def _dependencies_for_particle(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.particle)

    def _dependencies_for_wpsc_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc_1)

    def _dependencies_for_sound_id_1(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_1)

    def _dependencies_for_wpsc_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc_2)

    def _dependencies_for_wpsc_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.wpsc_3)

    def _dependencies_for_sound_id_2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_2)

    def _dependencies_for_elsc(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.elsc)

    def _dependencies_for_sound_id_3(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id_3)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed_0x00000004.dependencies_for, "unnamed_0x00000004", "PatternedAITypedef"),
            (self.unnamed_0x00000005.dependencies_for, "unnamed_0x00000005", "ActorParameters"),
            (self._dependencies_for_model_1, "model_1", "AssetId"),
            (self._dependencies_for_model_2, "model_2", "AssetId"),
            (self._dependencies_for_model_3, "model_3", "AssetId"),
            (self._dependencies_for_model_4, "model_4", "AssetId"),
            (self._dependencies_for_model_5, "model_5", "AssetId"),
            (self._dependencies_for_model_6, "model_6", "AssetId"),
            (self._dependencies_for_model_7, "model_7", "AssetId"),
            (self._dependencies_for_model_8, "model_8", "AssetId"),
            (self._dependencies_for_model_9, "model_9", "AssetId"),
            (self._dependencies_for_model_10, "model_10", "AssetId"),
            (self._dependencies_for_model_11, "model_11", "AssetId"),
            (self._dependencies_for_model_12, "model_12", "AssetId"),
            (self._dependencies_for_particle, "particle", "AssetId"),
            (self._dependencies_for_wpsc_1, "wpsc_1", "AssetId"),
            (self.damage_info_1.dependencies_for, "damage_info_1", "DamageInfo"),
            (self.unnamed_0x00000019.dependencies_for, "unnamed_0x00000019", "RidleyStruct1"),
            (self._dependencies_for_sound_id_1, "sound_id_1", "int"),
            (self._dependencies_for_wpsc_2, "wpsc_2", "AssetId"),
            (self.damage_info_2.dependencies_for, "damage_info_2", "DamageInfo"),
            (self.ridley_struct2_1.dependencies_for, "ridley_struct2_1", "RidleyStruct2"),
            (self._dependencies_for_wpsc_3, "wpsc_3", "AssetId"),
            (self.damage_info_3.dependencies_for, "damage_info_3", "DamageInfo"),
            (self.ridley_struct2_2.dependencies_for, "ridley_struct2_2", "RidleyStruct2"),
            (self._dependencies_for_sound_id_2, "sound_id_2", "int"),
            (self.damage_info_4.dependencies_for, "damage_info_4", "DamageInfo"),
            (self.ridley_struct2_3.dependencies_for, "ridley_struct2_3", "RidleyStruct2"),
            (self.damage_info_5.dependencies_for, "damage_info_5", "DamageInfo"),
            (self.damage_info_6.dependencies_for, "damage_info_6", "DamageInfo"),
            (self.damage_info_7.dependencies_for, "damage_info_7", "DamageInfo"),
            (self._dependencies_for_elsc, "elsc", "AssetId"),
            (self._dependencies_for_sound_id_3, "sound_id_3", "int"),
            (self.damage_info_8.dependencies_for, "damage_info_8", "DamageInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Ridley.{field_name} ({field_type}): {e}"
                )
