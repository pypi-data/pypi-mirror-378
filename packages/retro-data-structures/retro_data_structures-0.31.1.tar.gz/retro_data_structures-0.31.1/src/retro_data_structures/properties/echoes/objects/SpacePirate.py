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
from retro_data_structures.properties.echoes.archetypes.IngPossessionData import IngPossessionData
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.archetypes.SpacePirateWeaponData import SpacePirateWeaponData
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SpacePirateJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        ing_possession_data: json_util.JsonObject
        aggressiveness: float
        cover_check: float
        search_radius: float
        fall_back_check: float
        fall_back_radius: float
        hearing_radius: float
        sound: int
        unknown_0xce670970: bool
        projectile: int
        projectile_damage: json_util.JsonObject
        sound_projectile: int
        blade_damage: json_util.JsonObject
        kneel_attack_chance: float
        kneel_attack_shot: int
        kneel_attack_damage: json_util.JsonObject
        dodge_check: float
        sound_impact: int
        unknown_0x71587b45: float
        unknown_0x7903312e: float
        unknown_0x5080162a: float
        unknown_0xc78b40e0: float
        sound_alert: int
        gun_track_delay: float
        unknown_0x1b454a27: int
        cloak_opacity: float
        max_cloak_opacity: float
        unknown_0x61e801d4: float
        unknown_0xf19b113e: float
        sound_hurled: int
        sound_death: int
        unknown_0x8708b7d3: float
        avoid_distance: float
        weapon_data: json_util.JsonObject
    

@dataclasses.dataclass()
class SpacePirate(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    ing_possession_data: IngPossessionData = dataclasses.field(default_factory=IngPossessionData, metadata={
        'reflection': FieldReflection[IngPossessionData](
            IngPossessionData, id=0xe61748ed, original_name='IngPossessionData', from_json=IngPossessionData.from_json, to_json=IngPossessionData.to_json
        ),
    })
    aggressiveness: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9579b1f2, original_name='Aggressiveness'
        ),
    })
    cover_check: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf89ab419, original_name='CoverCheck'
        ),
    })
    search_radius: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed9bf5a3, original_name='SearchRadius'
        ),
    })
    fall_back_check: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3a27cf8, original_name='FallBackCheck'
        ),
    })
    fall_back_radius: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0cf5dd7, original_name='FallBackRadius'
        ),
    })
    hearing_radius: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xed69488f, original_name='HearingRadius'
        ),
    })
    sound: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa64ab9b8, original_name='Sound?'
        ),
    })
    unknown_0xce670970: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xce670970, original_name='Unknown'
        ),
    })
    projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xef485db9, original_name='Projectile'
        ),
    })
    projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x553b1339, original_name='ProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    sound_projectile: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xeac27605, original_name='Sound_Projectile'
        ),
    })
    blade_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xa5912430, original_name='BladeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    kneel_attack_chance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4f4087ed, original_name='KneelAttackChance'
        ),
    })
    kneel_attack_shot: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xda1122eb, original_name='KneelAttackShot'
        ),
    })
    kneel_attack_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x44143921, original_name='KneelAttackDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    dodge_check: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdc36e745, original_name='DodgeCheck'
        ),
    })
    sound_impact: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x1bb16ea5, original_name='Sound_Impact'
        ),
    })
    unknown_0x71587b45: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x71587b45, original_name='Unknown'
        ),
    })
    unknown_0x7903312e: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7903312e, original_name='Unknown'
        ),
    })
    unknown_0x5080162a: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5080162a, original_name='Unknown'
        ),
    })
    unknown_0xc78b40e0: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc78b40e0, original_name='Unknown'
        ),
    })
    sound_alert: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x386431ac, original_name='Sound_Alert'
        ),
    })
    gun_track_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb2ac2d96, original_name='GunTrackDelay'
        ),
    })
    unknown_0x1b454a27: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1b454a27, original_name='Unknown'
        ),
    })
    cloak_opacity: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5bc6f1d5, original_name='CloakOpacity'
        ),
    })
    max_cloak_opacity: float = dataclasses.field(default=0.75, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c021d7e, original_name='MaxCloakOpacity'
        ),
    })
    unknown_0x61e801d4: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x61e801d4, original_name='Unknown'
        ),
    })
    unknown_0xf19b113e: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf19b113e, original_name='Unknown'
        ),
    })
    sound_hurled: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x3bb37a8f, original_name='Sound_Hurled'
        ),
    })
    sound_death: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xe160b593, original_name='Sound_Death'
        ),
    })
    unknown_0x8708b7d3: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8708b7d3, original_name='Unknown'
        ),
    })
    avoid_distance: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b19cd88, original_name='AvoidDistance'
        ),
    })
    weapon_data: SpacePirateWeaponData = dataclasses.field(default_factory=SpacePirateWeaponData, metadata={
        'reflection': FieldReflection[SpacePirateWeaponData](
            SpacePirateWeaponData, id=0xdc89cc3c, original_name='WeaponData', from_json=SpacePirateWeaponData.from_json, to_json=SpacePirateWeaponData.to_json
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
        return 'PIRT'

    @classmethod
    def modules(cls) -> list[str]:
        return ['PirateRagDoll.rel', 'SpacePirate.rel']

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
        if property_count != 37:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 360.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'average_attack_time': 1.0, 'attack_time_variation': 0.5, 'damage_wait_time': 3.0, 'collision_radius': 0.800000011920929, 'collision_height': 3.0, 'step_up_height': 0.30000001192092896, 'creature_size': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe61748ed
        ing_possession_data = IngPossessionData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9579b1f2
        aggressiveness = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf89ab419
        cover_check = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed9bf5a3
        search_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3a27cf8
        fall_back_check = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf0cf5dd7
        fall_back_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed69488f
        hearing_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa64ab9b8
        sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce670970
        unknown_0xce670970 = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef485db9
        projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x553b1339
        projectile_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeac27605
        sound_projectile = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa5912430
        blade_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_knock_back_power': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4f4087ed
        kneel_attack_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xda1122eb
        kneel_attack_shot = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x44143921
        kneel_attack_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdc36e745
        dodge_check = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1bb16ea5
        sound_impact = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71587b45
        unknown_0x71587b45 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7903312e
        unknown_0x7903312e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5080162a
        unknown_0x5080162a = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc78b40e0
        unknown_0xc78b40e0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x386431ac
        sound_alert = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb2ac2d96
        gun_track_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1b454a27
        unknown_0x1b454a27 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5bc6f1d5
        cloak_opacity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c021d7e
        max_cloak_opacity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x61e801d4
        unknown_0x61e801d4 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf19b113e
        unknown_0xf19b113e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3bb37a8f
        sound_hurled = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe160b593
        sound_death = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8708b7d3
        unknown_0x8708b7d3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b19cd88
        avoid_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdc89cc3c
        weapon_data = SpacePirateWeaponData.from_stream(data, property_size)
    
        return cls(editor_properties, patterned, actor_information, ing_possession_data, aggressiveness, cover_check, search_radius, fall_back_check, fall_back_radius, hearing_radius, sound, unknown_0xce670970, projectile, projectile_damage, sound_projectile, blade_damage, kneel_attack_chance, kneel_attack_shot, kneel_attack_damage, dodge_check, sound_impact, unknown_0x71587b45, unknown_0x7903312e, unknown_0x5080162a, unknown_0xc78b40e0, sound_alert, gun_track_delay, unknown_0x1b454a27, cloak_opacity, max_cloak_opacity, unknown_0x61e801d4, unknown_0xf19b113e, sound_hurled, sound_death, unknown_0x8708b7d3, avoid_distance, weapon_data)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00%')  # 37 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'turn_speed': 360.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'average_attack_time': 1.0, 'attack_time_variation': 0.5, 'damage_wait_time': 3.0, 'collision_radius': 0.800000011920929, 'collision_height': 3.0, 'step_up_height': 0.30000001192092896, 'creature_size': 1})
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

        data.write(b'\xe6\x17H\xed')  # 0xe61748ed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ing_possession_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95y\xb1\xf2')  # 0x9579b1f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aggressiveness))

        data.write(b'\xf8\x9a\xb4\x19')  # 0xf89ab419
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cover_check))

        data.write(b'\xed\x9b\xf5\xa3')  # 0xed9bf5a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.search_radius))

        data.write(b'\xc3\xa2|\xf8')  # 0xc3a27cf8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fall_back_check))

        data.write(b'\xf0\xcf]\xd7')  # 0xf0cf5dd7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fall_back_radius))

        data.write(b'\xediH\x8f')  # 0xed69488f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hearing_radius))

        data.write(b'\xa6J\xb9\xb8')  # 0xa64ab9b8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound))

        data.write(b'\xceg\tp')  # 0xce670970
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xce670970))

        data.write(b'\xefH]\xb9')  # 0xef485db9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.projectile))

        data.write(b'U;\x139')  # 0x553b1339
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xea\xc2v\x05')  # 0xeac27605
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_projectile))

        data.write(b'\xa5\x91$0')  # 0xa5912430
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.blade_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_knock_back_power': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'O@\x87\xed')  # 0x4f4087ed
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.kneel_attack_chance))

        data.write(b'\xda\x11"\xeb')  # 0xda1122eb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.kneel_attack_shot))

        data.write(b'D\x149!')  # 0x44143921
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.kneel_attack_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdc6\xe7E')  # 0xdc36e745
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_check))

        data.write(b'\x1b\xb1n\xa5')  # 0x1bb16ea5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_impact))

        data.write(b'qX{E')  # 0x71587b45
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x71587b45))

        data.write(b'y\x031.')  # 0x7903312e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7903312e))

        data.write(b'P\x80\x16*')  # 0x5080162a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x5080162a))

        data.write(b'\xc7\x8b@\xe0')  # 0xc78b40e0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc78b40e0))

        data.write(b'8d1\xac')  # 0x386431ac
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_alert))

        data.write(b'\xb2\xac-\x96')  # 0xb2ac2d96
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.gun_track_delay))

        data.write(b"\x1bEJ'")  # 0x1b454a27
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x1b454a27))

        data.write(b'[\xc6\xf1\xd5')  # 0x5bc6f1d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cloak_opacity))

        data.write(b'|\x02\x1d~')  # 0x7c021d7e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_cloak_opacity))

        data.write(b'a\xe8\x01\xd4')  # 0x61e801d4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x61e801d4))

        data.write(b'\xf1\x9b\x11>')  # 0xf19b113e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf19b113e))

        data.write(b';\xb3z\x8f')  # 0x3bb37a8f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_hurled))

        data.write(b'\xe1`\xb5\x93')  # 0xe160b593
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_death))

        data.write(b'\x87\x08\xb7\xd3')  # 0x8708b7d3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8708b7d3))

        data.write(b'+\x19\xcd\x88')  # 0x2b19cd88
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.avoid_distance))

        data.write(b'\xdc\x89\xcc<')  # 0xdc89cc3c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weapon_data.to_stream(data)
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
        json_data = typing.cast("SpacePirateJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            ing_possession_data=IngPossessionData.from_json(json_data['ing_possession_data']),
            aggressiveness=json_data['aggressiveness'],
            cover_check=json_data['cover_check'],
            search_radius=json_data['search_radius'],
            fall_back_check=json_data['fall_back_check'],
            fall_back_radius=json_data['fall_back_radius'],
            hearing_radius=json_data['hearing_radius'],
            sound=json_data['sound'],
            unknown_0xce670970=json_data['unknown_0xce670970'],
            projectile=json_data['projectile'],
            projectile_damage=DamageInfo.from_json(json_data['projectile_damage']),
            sound_projectile=json_data['sound_projectile'],
            blade_damage=DamageInfo.from_json(json_data['blade_damage']),
            kneel_attack_chance=json_data['kneel_attack_chance'],
            kneel_attack_shot=json_data['kneel_attack_shot'],
            kneel_attack_damage=DamageInfo.from_json(json_data['kneel_attack_damage']),
            dodge_check=json_data['dodge_check'],
            sound_impact=json_data['sound_impact'],
            unknown_0x71587b45=json_data['unknown_0x71587b45'],
            unknown_0x7903312e=json_data['unknown_0x7903312e'],
            unknown_0x5080162a=json_data['unknown_0x5080162a'],
            unknown_0xc78b40e0=json_data['unknown_0xc78b40e0'],
            sound_alert=json_data['sound_alert'],
            gun_track_delay=json_data['gun_track_delay'],
            unknown_0x1b454a27=json_data['unknown_0x1b454a27'],
            cloak_opacity=json_data['cloak_opacity'],
            max_cloak_opacity=json_data['max_cloak_opacity'],
            unknown_0x61e801d4=json_data['unknown_0x61e801d4'],
            unknown_0xf19b113e=json_data['unknown_0xf19b113e'],
            sound_hurled=json_data['sound_hurled'],
            sound_death=json_data['sound_death'],
            unknown_0x8708b7d3=json_data['unknown_0x8708b7d3'],
            avoid_distance=json_data['avoid_distance'],
            weapon_data=SpacePirateWeaponData.from_json(json_data['weapon_data']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'ing_possession_data': self.ing_possession_data.to_json(),
            'aggressiveness': self.aggressiveness,
            'cover_check': self.cover_check,
            'search_radius': self.search_radius,
            'fall_back_check': self.fall_back_check,
            'fall_back_radius': self.fall_back_radius,
            'hearing_radius': self.hearing_radius,
            'sound': self.sound,
            'unknown_0xce670970': self.unknown_0xce670970,
            'projectile': self.projectile,
            'projectile_damage': self.projectile_damage.to_json(),
            'sound_projectile': self.sound_projectile,
            'blade_damage': self.blade_damage.to_json(),
            'kneel_attack_chance': self.kneel_attack_chance,
            'kneel_attack_shot': self.kneel_attack_shot,
            'kneel_attack_damage': self.kneel_attack_damage.to_json(),
            'dodge_check': self.dodge_check,
            'sound_impact': self.sound_impact,
            'unknown_0x71587b45': self.unknown_0x71587b45,
            'unknown_0x7903312e': self.unknown_0x7903312e,
            'unknown_0x5080162a': self.unknown_0x5080162a,
            'unknown_0xc78b40e0': self.unknown_0xc78b40e0,
            'sound_alert': self.sound_alert,
            'gun_track_delay': self.gun_track_delay,
            'unknown_0x1b454a27': self.unknown_0x1b454a27,
            'cloak_opacity': self.cloak_opacity,
            'max_cloak_opacity': self.max_cloak_opacity,
            'unknown_0x61e801d4': self.unknown_0x61e801d4,
            'unknown_0xf19b113e': self.unknown_0xf19b113e,
            'sound_hurled': self.sound_hurled,
            'sound_death': self.sound_death,
            'unknown_0x8708b7d3': self.unknown_0x8708b7d3,
            'avoid_distance': self.avoid_distance,
            'weapon_data': self.weapon_data.to_json(),
        }

    def _dependencies_for_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.projectile)

    def _dependencies_for_sound_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_projectile)

    def _dependencies_for_kneel_attack_shot(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.kneel_attack_shot)

    def _dependencies_for_sound_impact(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_impact)

    def _dependencies_for_sound_hurled(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_hurled)

    def _dependencies_for_sound_death(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_death)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self.ing_possession_data.dependencies_for, "ing_possession_data", "IngPossessionData"),
            (self._dependencies_for_projectile, "projectile", "AssetId"),
            (self.projectile_damage.dependencies_for, "projectile_damage", "DamageInfo"),
            (self._dependencies_for_sound_projectile, "sound_projectile", "int"),
            (self.blade_damage.dependencies_for, "blade_damage", "DamageInfo"),
            (self._dependencies_for_kneel_attack_shot, "kneel_attack_shot", "AssetId"),
            (self.kneel_attack_damage.dependencies_for, "kneel_attack_damage", "DamageInfo"),
            (self._dependencies_for_sound_impact, "sound_impact", "int"),
            (self._dependencies_for_sound_hurled, "sound_hurled", "int"),
            (self._dependencies_for_sound_death, "sound_death", "int"),
            (self.weapon_data.dependencies_for, "weapon_data", "SpacePirateWeaponData"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for SpacePirate.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 360.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'average_attack_time': 1.0, 'attack_time_variation': 0.5, 'damage_wait_time': 3.0, 'collision_radius': 0.800000011920929, 'collision_height': 3.0, 'step_up_height': 0.30000001192092896, 'creature_size': 1})


def _decode_aggressiveness(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cover_check(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_search_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fall_back_check(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fall_back_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hearing_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xce670970(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_projectile_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 5.0})


def _decode_sound_projectile(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_blade_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0, 'di_knock_back_power': 5.0})


def _decode_kneel_attack_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_kneel_attack_shot(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_kneel_attack_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 10.0})


def _decode_dodge_check(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_impact(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x71587b45(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7903312e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x5080162a(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc78b40e0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_alert(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_gun_track_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x1b454a27(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cloak_opacity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_cloak_opacity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x61e801d4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf19b113e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_hurled(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_death(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x8708b7d3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_avoid_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0xe61748ed: ('ing_possession_data', IngPossessionData.from_stream),
    0x9579b1f2: ('aggressiveness', _decode_aggressiveness),
    0xf89ab419: ('cover_check', _decode_cover_check),
    0xed9bf5a3: ('search_radius', _decode_search_radius),
    0xc3a27cf8: ('fall_back_check', _decode_fall_back_check),
    0xf0cf5dd7: ('fall_back_radius', _decode_fall_back_radius),
    0xed69488f: ('hearing_radius', _decode_hearing_radius),
    0xa64ab9b8: ('sound', _decode_sound),
    0xce670970: ('unknown_0xce670970', _decode_unknown_0xce670970),
    0xef485db9: ('projectile', _decode_projectile),
    0x553b1339: ('projectile_damage', _decode_projectile_damage),
    0xeac27605: ('sound_projectile', _decode_sound_projectile),
    0xa5912430: ('blade_damage', _decode_blade_damage),
    0x4f4087ed: ('kneel_attack_chance', _decode_kneel_attack_chance),
    0xda1122eb: ('kneel_attack_shot', _decode_kneel_attack_shot),
    0x44143921: ('kneel_attack_damage', _decode_kneel_attack_damage),
    0xdc36e745: ('dodge_check', _decode_dodge_check),
    0x1bb16ea5: ('sound_impact', _decode_sound_impact),
    0x71587b45: ('unknown_0x71587b45', _decode_unknown_0x71587b45),
    0x7903312e: ('unknown_0x7903312e', _decode_unknown_0x7903312e),
    0x5080162a: ('unknown_0x5080162a', _decode_unknown_0x5080162a),
    0xc78b40e0: ('unknown_0xc78b40e0', _decode_unknown_0xc78b40e0),
    0x386431ac: ('sound_alert', _decode_sound_alert),
    0xb2ac2d96: ('gun_track_delay', _decode_gun_track_delay),
    0x1b454a27: ('unknown_0x1b454a27', _decode_unknown_0x1b454a27),
    0x5bc6f1d5: ('cloak_opacity', _decode_cloak_opacity),
    0x7c021d7e: ('max_cloak_opacity', _decode_max_cloak_opacity),
    0x61e801d4: ('unknown_0x61e801d4', _decode_unknown_0x61e801d4),
    0xf19b113e: ('unknown_0xf19b113e', _decode_unknown_0xf19b113e),
    0x3bb37a8f: ('sound_hurled', _decode_sound_hurled),
    0xe160b593: ('sound_death', _decode_sound_death),
    0x8708b7d3: ('unknown_0x8708b7d3', _decode_unknown_0x8708b7d3),
    0x2b19cd88: ('avoid_distance', _decode_avoid_distance),
    0xdc89cc3c: ('weapon_data', SpacePirateWeaponData.from_stream),
}
