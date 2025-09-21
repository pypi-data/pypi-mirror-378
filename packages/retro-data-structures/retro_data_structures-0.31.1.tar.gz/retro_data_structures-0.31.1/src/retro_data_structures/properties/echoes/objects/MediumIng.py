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
from retro_data_structures.properties.echoes.archetypes.CameraShakerData import CameraShakerData
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.echoes.core.Color import Color
from retro_data_structures.properties.echoes.core.Spline import Spline

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class MediumIngJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        spawn_mode: int
        actor_information: json_util.JsonObject
        aggressiveness: float
        unknown_0x4d1d840d: float
        min_melee_attack_interval: float
        max_melee_attack_range: float
        melee_damage: json_util.JsonObject
        unknown_0x636f11e5: float
        mist_damage: json_util.JsonObject
        min_mist_attack_interval: float
        misting_vulnerability: json_util.JsonObject
        min_arm_attack_interval: float
        unknown_0x9d3cfeb0: float
        unknown_0xdc2bc136: float
        min_tentacle_length: float
        max_tentacle_length: float
        arm_attack_time: float
        unknown_0x8f1d597c: float
        attack_tentacle: json_util.JsonObject
        actor_parameters: json_util.JsonObject
        attack_motion: json_util.JsonObject
        camera_shaker_data: json_util.JsonObject
        attack_tentacle_damage: json_util.JsonObject
        taunt_chance: float
        double_dash_chance: float
        light_color: json_util.JsonValue
        light_attenuation: float
        unknown_0xb459c3e9: json_util.JsonObject
        dash_speed: json_util.JsonObject
        ing_spot_blob_fx: int
        ing_spot_sound: int
        unknown_0x0e3d3708: float
    

@dataclasses.dataclass()
class MediumIng(BaseObjectType):
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
    spawn_mode: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc96ae3df, original_name='SpawnMode'
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    aggressiveness: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9579b1f2, original_name='Aggressiveness'
        ),
    })
    unknown_0x4d1d840d: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4d1d840d, original_name='Unknown'
        ),
    })
    min_melee_attack_interval: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd189a7aa, original_name='MinMeleeAttackInterval'
        ),
    })
    max_melee_attack_range: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf3ea2def, original_name='MaxMeleeAttackRange'
        ),
    })
    melee_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc9416034, original_name='MeleeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x636f11e5: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x636f11e5, original_name='Unknown'
        ),
    })
    mist_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xd2254430, original_name='MistDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    min_mist_attack_interval: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb787f412, original_name='MinMistAttackInterval'
        ),
    })
    misting_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x49c8d0c7, original_name='MistingVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    min_arm_attack_interval: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x15294900, original_name='MinArmAttackInterval'
        ),
    })
    unknown_0x9d3cfeb0: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9d3cfeb0, original_name='Unknown'
        ),
    })
    unknown_0xdc2bc136: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xdc2bc136, original_name='Unknown'
        ),
    })
    min_tentacle_length: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x74ffed99, original_name='MinTentacleLength'
        ),
    })
    max_tentacle_length: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x35e8d21f, original_name='MaxTentacleLength'
        ),
    })
    arm_attack_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb93573f7, original_name='ArmAttackTime'
        ),
    })
    unknown_0x8f1d597c: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8f1d597c, original_name='Unknown'
        ),
    })
    attack_tentacle: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x7a9f8249, original_name='AttackTentacle', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    actor_parameters: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x38cf133b, original_name='ActorParameters', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    attack_motion: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x0767060d, original_name='AttackMotion', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    camera_shaker_data: CameraShakerData = dataclasses.field(default_factory=CameraShakerData, metadata={
        'reflection': FieldReflection[CameraShakerData](
            CameraShakerData, id=0x0e6b1e70, original_name='CameraShakerData', from_json=CameraShakerData.from_json, to_json=CameraShakerData.to_json
        ),
    })
    attack_tentacle_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xf683fe08, original_name='AttackTentacleDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    taunt_chance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa77f6212, original_name='TauntChance'
        ),
    })
    double_dash_chance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9cf01473, original_name='DoubleDashChance'
        ),
    })
    light_color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xbd3efe7d, original_name='LightColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    light_attenuation: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd24b888f, original_name='LightAttenuation'
        ),
    })
    unknown_0xb459c3e9: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xb459c3e9, original_name='Unknown', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    dash_speed: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x323e4ed0, original_name='DashSpeed', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    ing_spot_blob_fx: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x079bc576, original_name='IngSpotBlobFx'
        ),
    })
    ing_spot_sound: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x7cb63cd3, original_name='IngSpotSound'
        ),
    })
    unknown_0x0e3d3708: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0e3d3708, original_name='Unknown'
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
        return 'MING'

    @classmethod
    def modules(cls) -> list[str]:
        return ['GeomBlobV2.rel', 'MediumIng.rel']

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
        if property_count != 34:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 360.0, 'creature_size': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc96ae3df
        spawn_mode = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9579b1f2
        aggressiveness = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d1d840d
        unknown_0x4d1d840d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd189a7aa
        min_melee_attack_interval = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf3ea2def
        max_melee_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc9416034
        melee_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x636f11e5
        unknown_0x636f11e5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd2254430
        mist_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb787f412
        min_mist_attack_interval = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x49c8d0c7
        misting_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x15294900
        min_arm_attack_interval = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9d3cfeb0
        unknown_0x9d3cfeb0 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdc2bc136
        unknown_0xdc2bc136 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x74ffed99
        min_tentacle_length = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x35e8d21f
        max_tentacle_length = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb93573f7
        arm_attack_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f1d597c
        unknown_0x8f1d597c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a9f8249
        attack_tentacle = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x38cf133b
        actor_parameters = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0767060d
        attack_motion = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0e6b1e70
        camera_shaker_data = CameraShakerData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf683fe08
        attack_tentacle_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa77f6212
        taunt_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9cf01473
        double_dash_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbd3efe7d
        light_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd24b888f
        light_attenuation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb459c3e9
        unknown_0xb459c3e9 = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x323e4ed0
        dash_speed = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x079bc576
        ing_spot_blob_fx = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7cb63cd3
        ing_spot_sound = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0e3d3708
        unknown_0x0e3d3708 = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, patterned, spawn_mode, actor_information, aggressiveness, unknown_0x4d1d840d, min_melee_attack_interval, max_melee_attack_range, melee_damage, unknown_0x636f11e5, mist_damage, min_mist_attack_interval, misting_vulnerability, min_arm_attack_interval, unknown_0x9d3cfeb0, unknown_0xdc2bc136, min_tentacle_length, max_tentacle_length, arm_attack_time, unknown_0x8f1d597c, attack_tentacle, actor_parameters, attack_motion, camera_shaker_data, attack_tentacle_damage, taunt_chance, double_dash_chance, light_color, light_attenuation, unknown_0xb459c3e9, dash_speed, ing_spot_blob_fx, ing_spot_sound, unknown_0x0e3d3708)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00"')  # 34 properties

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
        self.patterned.to_stream(data, default_override={'turn_speed': 360.0, 'creature_size': 1})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc9j\xe3\xdf')  # 0xc96ae3df
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.spawn_mode))

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x95y\xb1\xf2')  # 0x9579b1f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.aggressiveness))

        data.write(b'M\x1d\x84\r')  # 0x4d1d840d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4d1d840d))

        data.write(b'\xd1\x89\xa7\xaa')  # 0xd189a7aa
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_melee_attack_interval))

        data.write(b'\xf3\xea-\xef')  # 0xf3ea2def
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_melee_attack_range))

        data.write(b'\xc9A`4')  # 0xc9416034
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.melee_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'co\x11\xe5')  # 0x636f11e5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x636f11e5))

        data.write(b'\xd2%D0')  # 0xd2254430
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.mist_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb7\x87\xf4\x12')  # 0xb787f412
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_mist_attack_interval))

        data.write(b'I\xc8\xd0\xc7')  # 0x49c8d0c7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.misting_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x15)I\x00')  # 0x15294900
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_arm_attack_interval))

        data.write(b'\x9d<\xfe\xb0')  # 0x9d3cfeb0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9d3cfeb0))

        data.write(b'\xdc+\xc16')  # 0xdc2bc136
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xdc2bc136))

        data.write(b't\xff\xed\x99')  # 0x74ffed99
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_tentacle_length))

        data.write(b'5\xe8\xd2\x1f')  # 0x35e8d21f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_tentacle_length))

        data.write(b'\xb95s\xf7')  # 0xb93573f7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.arm_attack_time))

        data.write(b'\x8f\x1dY|')  # 0x8f1d597c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8f1d597c))

        data.write(b'z\x9f\x82I')  # 0x7a9f8249
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_tentacle.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'8\xcf\x13;')  # 0x38cf133b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_parameters.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x07g\x06\r')  # 0x767060d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0ek\x1ep')  # 0xe6b1e70
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera_shaker_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf6\x83\xfe\x08')  # 0xf683fe08
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.attack_tentacle_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa7\x7fb\x12')  # 0xa77f6212
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.taunt_chance))

        data.write(b'\x9c\xf0\x14s')  # 0x9cf01473
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.double_dash_chance))

        data.write(b'\xbd>\xfe}')  # 0xbd3efe7d
        data.write(b'\x00\x10')  # size
        self.light_color.to_stream(data)

        data.write(b'\xd2K\x88\x8f')  # 0xd24b888f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.light_attenuation))

        data.write(b'\xb4Y\xc3\xe9')  # 0xb459c3e9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_0xb459c3e9.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'2>N\xd0')  # 0x323e4ed0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dash_speed.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x07\x9b\xc5v')  # 0x79bc576
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.ing_spot_blob_fx))

        data.write(b'|\xb6<\xd3')  # 0x7cb63cd3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.ing_spot_sound))

        data.write(b'\x0e=7\x08')  # 0xe3d3708
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0e3d3708))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MediumIngJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            spawn_mode=json_data['spawn_mode'],
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            aggressiveness=json_data['aggressiveness'],
            unknown_0x4d1d840d=json_data['unknown_0x4d1d840d'],
            min_melee_attack_interval=json_data['min_melee_attack_interval'],
            max_melee_attack_range=json_data['max_melee_attack_range'],
            melee_damage=DamageInfo.from_json(json_data['melee_damage']),
            unknown_0x636f11e5=json_data['unknown_0x636f11e5'],
            mist_damage=DamageInfo.from_json(json_data['mist_damage']),
            min_mist_attack_interval=json_data['min_mist_attack_interval'],
            misting_vulnerability=DamageVulnerability.from_json(json_data['misting_vulnerability']),
            min_arm_attack_interval=json_data['min_arm_attack_interval'],
            unknown_0x9d3cfeb0=json_data['unknown_0x9d3cfeb0'],
            unknown_0xdc2bc136=json_data['unknown_0xdc2bc136'],
            min_tentacle_length=json_data['min_tentacle_length'],
            max_tentacle_length=json_data['max_tentacle_length'],
            arm_attack_time=json_data['arm_attack_time'],
            unknown_0x8f1d597c=json_data['unknown_0x8f1d597c'],
            attack_tentacle=AnimationParameters.from_json(json_data['attack_tentacle']),
            actor_parameters=ActorParameters.from_json(json_data['actor_parameters']),
            attack_motion=Spline.from_json(json_data['attack_motion']),
            camera_shaker_data=CameraShakerData.from_json(json_data['camera_shaker_data']),
            attack_tentacle_damage=DamageInfo.from_json(json_data['attack_tentacle_damage']),
            taunt_chance=json_data['taunt_chance'],
            double_dash_chance=json_data['double_dash_chance'],
            light_color=Color.from_json(json_data['light_color']),
            light_attenuation=json_data['light_attenuation'],
            unknown_0xb459c3e9=Spline.from_json(json_data['unknown_0xb459c3e9']),
            dash_speed=Spline.from_json(json_data['dash_speed']),
            ing_spot_blob_fx=json_data['ing_spot_blob_fx'],
            ing_spot_sound=json_data['ing_spot_sound'],
            unknown_0x0e3d3708=json_data['unknown_0x0e3d3708'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'spawn_mode': self.spawn_mode,
            'actor_information': self.actor_information.to_json(),
            'aggressiveness': self.aggressiveness,
            'unknown_0x4d1d840d': self.unknown_0x4d1d840d,
            'min_melee_attack_interval': self.min_melee_attack_interval,
            'max_melee_attack_range': self.max_melee_attack_range,
            'melee_damage': self.melee_damage.to_json(),
            'unknown_0x636f11e5': self.unknown_0x636f11e5,
            'mist_damage': self.mist_damage.to_json(),
            'min_mist_attack_interval': self.min_mist_attack_interval,
            'misting_vulnerability': self.misting_vulnerability.to_json(),
            'min_arm_attack_interval': self.min_arm_attack_interval,
            'unknown_0x9d3cfeb0': self.unknown_0x9d3cfeb0,
            'unknown_0xdc2bc136': self.unknown_0xdc2bc136,
            'min_tentacle_length': self.min_tentacle_length,
            'max_tentacle_length': self.max_tentacle_length,
            'arm_attack_time': self.arm_attack_time,
            'unknown_0x8f1d597c': self.unknown_0x8f1d597c,
            'attack_tentacle': self.attack_tentacle.to_json(),
            'actor_parameters': self.actor_parameters.to_json(),
            'attack_motion': self.attack_motion.to_json(),
            'camera_shaker_data': self.camera_shaker_data.to_json(),
            'attack_tentacle_damage': self.attack_tentacle_damage.to_json(),
            'taunt_chance': self.taunt_chance,
            'double_dash_chance': self.double_dash_chance,
            'light_color': self.light_color.to_json(),
            'light_attenuation': self.light_attenuation,
            'unknown_0xb459c3e9': self.unknown_0xb459c3e9.to_json(),
            'dash_speed': self.dash_speed.to_json(),
            'ing_spot_blob_fx': self.ing_spot_blob_fx,
            'ing_spot_sound': self.ing_spot_sound,
            'unknown_0x0e3d3708': self.unknown_0x0e3d3708,
        }

    def _dependencies_for_ing_spot_blob_fx(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.ing_spot_blob_fx)

    def _dependencies_for_ing_spot_sound(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.ing_spot_sound)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self.melee_damage.dependencies_for, "melee_damage", "DamageInfo"),
            (self.mist_damage.dependencies_for, "mist_damage", "DamageInfo"),
            (self.misting_vulnerability.dependencies_for, "misting_vulnerability", "DamageVulnerability"),
            (self.attack_tentacle.dependencies_for, "attack_tentacle", "AnimationParameters"),
            (self.actor_parameters.dependencies_for, "actor_parameters", "ActorParameters"),
            (self.camera_shaker_data.dependencies_for, "camera_shaker_data", "CameraShakerData"),
            (self.attack_tentacle_damage.dependencies_for, "attack_tentacle_damage", "DamageInfo"),
            (self._dependencies_for_ing_spot_blob_fx, "ing_spot_blob_fx", "AssetId"),
            (self._dependencies_for_ing_spot_sound, "ing_spot_sound", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for MediumIng.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 360.0, 'creature_size': 1})


def _decode_spawn_mode(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_aggressiveness(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4d1d840d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_melee_attack_interval(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_melee_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x636f11e5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_mist_attack_interval(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_arm_attack_interval(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9d3cfeb0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xdc2bc136(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_tentacle_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_tentacle_length(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_arm_attack_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x8f1d597c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_taunt_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_double_dash_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_light_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_light_attenuation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ing_spot_blob_fx(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_ing_spot_sound(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x0e3d3708(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0xc96ae3df: ('spawn_mode', _decode_spawn_mode),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x9579b1f2: ('aggressiveness', _decode_aggressiveness),
    0x4d1d840d: ('unknown_0x4d1d840d', _decode_unknown_0x4d1d840d),
    0xd189a7aa: ('min_melee_attack_interval', _decode_min_melee_attack_interval),
    0xf3ea2def: ('max_melee_attack_range', _decode_max_melee_attack_range),
    0xc9416034: ('melee_damage', DamageInfo.from_stream),
    0x636f11e5: ('unknown_0x636f11e5', _decode_unknown_0x636f11e5),
    0xd2254430: ('mist_damage', DamageInfo.from_stream),
    0xb787f412: ('min_mist_attack_interval', _decode_min_mist_attack_interval),
    0x49c8d0c7: ('misting_vulnerability', DamageVulnerability.from_stream),
    0x15294900: ('min_arm_attack_interval', _decode_min_arm_attack_interval),
    0x9d3cfeb0: ('unknown_0x9d3cfeb0', _decode_unknown_0x9d3cfeb0),
    0xdc2bc136: ('unknown_0xdc2bc136', _decode_unknown_0xdc2bc136),
    0x74ffed99: ('min_tentacle_length', _decode_min_tentacle_length),
    0x35e8d21f: ('max_tentacle_length', _decode_max_tentacle_length),
    0xb93573f7: ('arm_attack_time', _decode_arm_attack_time),
    0x8f1d597c: ('unknown_0x8f1d597c', _decode_unknown_0x8f1d597c),
    0x7a9f8249: ('attack_tentacle', AnimationParameters.from_stream),
    0x38cf133b: ('actor_parameters', ActorParameters.from_stream),
    0x767060d: ('attack_motion', Spline.from_stream),
    0xe6b1e70: ('camera_shaker_data', CameraShakerData.from_stream),
    0xf683fe08: ('attack_tentacle_damage', DamageInfo.from_stream),
    0xa77f6212: ('taunt_chance', _decode_taunt_chance),
    0x9cf01473: ('double_dash_chance', _decode_double_dash_chance),
    0xbd3efe7d: ('light_color', _decode_light_color),
    0xd24b888f: ('light_attenuation', _decode_light_attenuation),
    0xb459c3e9: ('unknown_0xb459c3e9', Spline.from_stream),
    0x323e4ed0: ('dash_speed', Spline.from_stream),
    0x79bc576: ('ing_spot_blob_fx', _decode_ing_spot_blob_fx),
    0x7cb63cd3: ('ing_spot_sound', _decode_ing_spot_sound),
    0xe3d3708: ('unknown_0x0e3d3708', _decode_unknown_0x0e3d3708),
}
