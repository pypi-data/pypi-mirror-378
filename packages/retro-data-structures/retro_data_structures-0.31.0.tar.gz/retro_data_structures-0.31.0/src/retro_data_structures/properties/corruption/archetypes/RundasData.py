# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability

if typing.TYPE_CHECKING:
    class RundasDataJson(typing_extensions.TypedDict):
        unknown_0x1aeb498d: float
        unknown_0x9c7f3b23: float
        unknown_0x706186d2: float
        unknown_0x3f5d6545: float
        unknown_0x59a93220: float
        unknown_0x6cc73ec1: float
        grapple_struggle_time: float
        hypermode_vulnerability: json_util.JsonObject
        armor_vulnerability: json_util.JsonObject
        damage_info_0x8d4a2668: json_util.JsonObject
        unknown_0xf41394f6: float
        ice_grenade_damage: json_util.JsonObject
        damage_info_0x7fbc7e81: json_util.JsonObject
        unknown_0xff944885: float
        unknown_0x19f4e764: float
        unknown_0x050cb86e: float
        unknown_0xe36c178f: float
        damage_info_0x3063bbf1: json_util.JsonObject
        damage_info_0x5997ebe1: json_util.JsonObject
        rush_range_min: float
        rush_range_max: float
        unknown_0x3be0a66b: float
        unknown_0xf586836f: float
        unknown_0x7312f1c1: float
        unknown_0x775362cf: float
        unknown_0xf1c71061: float
        missile_freeze_distance: float
        surfing_projectile_damage: json_util.JsonObject
        unknown_0xca04d756: int
        unknown_0xd94131fd: int
        unknown_0x821b0c82: float
        unknown_0xe4fe6af6: float
        unknown_0x7ef4effe: float
        unknown_0x3fe3d078: float
        surf_height_min: float
        surf_height_max: float
        elevation_timer: float
        shard_storm_timer: float
        ice_summon_timer: float
        rush_timer: float
        unknown_0xc758f52e: float
        surf_timer: float
        unknown_0xf80fcae2: float
        is_gandrayda: bool
        unknown_0x691746f2: float
        unknown_0xcf197148: float
        unknown_0x9ee0ca15: float
        unknown_0xfc629f72: float
        unknown_0xef2779d9: float
    

@dataclasses.dataclass()
class RundasData(BaseProperty):
    unknown_0x1aeb498d: float = dataclasses.field(default=180.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1aeb498d, original_name='Unknown'
        ),
    })
    unknown_0x9c7f3b23: float = dataclasses.field(default=225.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9c7f3b23, original_name='Unknown'
        ),
    })
    unknown_0x706186d2: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x706186d2, original_name='Unknown'
        ),
    })
    unknown_0x3f5d6545: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3f5d6545, original_name='Unknown'
        ),
    })
    unknown_0x59a93220: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x59a93220, original_name='Unknown'
        ),
    })
    unknown_0x6cc73ec1: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6cc73ec1, original_name='Unknown'
        ),
    })
    grapple_struggle_time: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x57f0a2a7, original_name='GrappleStruggleTime'
        ),
    })
    hypermode_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xd1522831, original_name='HypermodeVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    armor_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x896d5bd9, original_name='ArmorVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    damage_info_0x8d4a2668: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x8d4a2668, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xf41394f6: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf41394f6, original_name='Unknown'
        ),
    })
    ice_grenade_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xb1b44917, original_name='IceGrenadeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0x7fbc7e81: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x7fbc7e81, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xff944885: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xff944885, original_name='Unknown'
        ),
    })
    unknown_0x19f4e764: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x19f4e764, original_name='Unknown'
        ),
    })
    unknown_0x050cb86e: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x050cb86e, original_name='Unknown'
        ),
    })
    unknown_0xe36c178f: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe36c178f, original_name='Unknown'
        ),
    })
    damage_info_0x3063bbf1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x3063bbf1, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0x5997ebe1: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x5997ebe1, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    rush_range_min: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc922f0e0, original_name='RushRangeMin'
        ),
    })
    rush_range_max: float = dataclasses.field(default=200.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2f425f01, original_name='RushRangeMax'
        ),
    })
    unknown_0x3be0a66b: float = dataclasses.field(default=80.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3be0a66b, original_name='Unknown'
        ),
    })
    unknown_0xf586836f: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf586836f, original_name='Unknown'
        ),
    })
    unknown_0x7312f1c1: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7312f1c1, original_name='Unknown'
        ),
    })
    unknown_0x775362cf: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x775362cf, original_name='Unknown'
        ),
    })
    unknown_0xf1c71061: float = dataclasses.field(default=0.949999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf1c71061, original_name='Unknown'
        ),
    })
    missile_freeze_distance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3f196c78, original_name='MissileFreezeDistance'
        ),
    })
    surfing_projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x78df0b7d, original_name='SurfingProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0xca04d756: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xca04d756, original_name='Unknown'
        ),
    })
    unknown_0xd94131fd: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd94131fd, original_name='Unknown'
        ),
    })
    unknown_0x821b0c82: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x821b0c82, original_name='Unknown'
        ),
    })
    unknown_0xe4fe6af6: float = dataclasses.field(default=0.44999998807907104, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe4fe6af6, original_name='Unknown'
        ),
    })
    unknown_0x7ef4effe: float = dataclasses.field(default=0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7ef4effe, original_name='Unknown'
        ),
    })
    unknown_0x3fe3d078: float = dataclasses.field(default=0.44999998807907104, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3fe3d078, original_name='Unknown'
        ),
    })
    surf_height_min: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1dcc7e61, original_name='SurfHeightMin'
        ),
    })
    surf_height_max: float = dataclasses.field(default=11.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfbacd180, original_name='SurfHeightMax'
        ),
    })
    elevation_timer: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe4cd7924, original_name='ElevationTimer'
        ),
    })
    shard_storm_timer: float = dataclasses.field(default=7.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3056ffba, original_name='ShardStormTimer'
        ),
    })
    ice_summon_timer: float = dataclasses.field(default=18.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x595e38d6, original_name='IceSummonTimer'
        ),
    })
    rush_timer: float = dataclasses.field(default=14.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6d0ba041, original_name='RushTimer'
        ),
    })
    unknown_0xc758f52e: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc758f52e, original_name='Unknown'
        ),
    })
    surf_timer: float = dataclasses.field(default=17.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x39d7265e, original_name='SurfTimer'
        ),
    })
    unknown_0xf80fcae2: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf80fcae2, original_name='Unknown'
        ),
    })
    is_gandrayda: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x531a8c85, original_name='IsGandrayda'
        ),
    })
    unknown_0x691746f2: float = dataclasses.field(default=125.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x691746f2, original_name='Unknown'
        ),
    })
    unknown_0xcf197148: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcf197148, original_name='Unknown'
        ),
    })
    unknown_0x9ee0ca15: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9ee0ca15, original_name='Unknown'
        ),
    })
    unknown_0xfc629f72: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfc629f72, original_name='Unknown'
        ),
    })
    unknown_0xef2779d9: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xef2779d9, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
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

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 49:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1aeb498d
        unknown_0x1aeb498d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9c7f3b23
        unknown_0x9c7f3b23 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x706186d2
        unknown_0x706186d2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3f5d6545
        unknown_0x3f5d6545 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x59a93220
        unknown_0x59a93220 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6cc73ec1
        unknown_0x6cc73ec1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x57f0a2a7
        grapple_struggle_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd1522831
        hypermode_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x896d5bd9
        armor_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8d4a2668
        damage_info_0x8d4a2668 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf41394f6
        unknown_0xf41394f6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb1b44917
        ice_grenade_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fbc7e81
        damage_info_0x7fbc7e81 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xff944885
        unknown_0xff944885 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x19f4e764
        unknown_0x19f4e764 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x050cb86e
        unknown_0x050cb86e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe36c178f
        unknown_0xe36c178f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3063bbf1
        damage_info_0x3063bbf1 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5997ebe1
        damage_info_0x5997ebe1 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc922f0e0
        rush_range_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2f425f01
        rush_range_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3be0a66b
        unknown_0x3be0a66b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf586836f
        unknown_0xf586836f = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7312f1c1
        unknown_0x7312f1c1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x775362cf
        unknown_0x775362cf = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf1c71061
        unknown_0xf1c71061 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3f196c78
        missile_freeze_distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x78df0b7d
        surfing_projectile_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xca04d756
        unknown_0xca04d756 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd94131fd
        unknown_0xd94131fd = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x821b0c82
        unknown_0x821b0c82 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe4fe6af6
        unknown_0xe4fe6af6 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ef4effe
        unknown_0x7ef4effe = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3fe3d078
        unknown_0x3fe3d078 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1dcc7e61
        surf_height_min = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfbacd180
        surf_height_max = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe4cd7924
        elevation_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3056ffba
        shard_storm_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x595e38d6
        ice_summon_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6d0ba041
        rush_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc758f52e
        unknown_0xc758f52e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x39d7265e
        surf_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf80fcae2
        unknown_0xf80fcae2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x531a8c85
        is_gandrayda = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x691746f2
        unknown_0x691746f2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf197148
        unknown_0xcf197148 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ee0ca15
        unknown_0x9ee0ca15 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc629f72
        unknown_0xfc629f72 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef2779d9
        unknown_0xef2779d9 = struct.unpack('>f', data.read(4))[0]
    
        return cls(unknown_0x1aeb498d, unknown_0x9c7f3b23, unknown_0x706186d2, unknown_0x3f5d6545, unknown_0x59a93220, unknown_0x6cc73ec1, grapple_struggle_time, hypermode_vulnerability, armor_vulnerability, damage_info_0x8d4a2668, unknown_0xf41394f6, ice_grenade_damage, damage_info_0x7fbc7e81, unknown_0xff944885, unknown_0x19f4e764, unknown_0x050cb86e, unknown_0xe36c178f, damage_info_0x3063bbf1, damage_info_0x5997ebe1, rush_range_min, rush_range_max, unknown_0x3be0a66b, unknown_0xf586836f, unknown_0x7312f1c1, unknown_0x775362cf, unknown_0xf1c71061, missile_freeze_distance, surfing_projectile_damage, unknown_0xca04d756, unknown_0xd94131fd, unknown_0x821b0c82, unknown_0xe4fe6af6, unknown_0x7ef4effe, unknown_0x3fe3d078, surf_height_min, surf_height_max, elevation_timer, shard_storm_timer, ice_summon_timer, rush_timer, unknown_0xc758f52e, surf_timer, unknown_0xf80fcae2, is_gandrayda, unknown_0x691746f2, unknown_0xcf197148, unknown_0x9ee0ca15, unknown_0xfc629f72, unknown_0xef2779d9)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x001')  # 49 properties

        data.write(b'\x1a\xebI\x8d')  # 0x1aeb498d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x1aeb498d))

        data.write(b'\x9c\x7f;#')  # 0x9c7f3b23
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9c7f3b23))

        data.write(b'pa\x86\xd2')  # 0x706186d2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x706186d2))

        data.write(b'?]eE')  # 0x3f5d6545
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3f5d6545))

        data.write(b'Y\xa92 ')  # 0x59a93220
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x59a93220))

        data.write(b'l\xc7>\xc1')  # 0x6cc73ec1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6cc73ec1))

        data.write(b'W\xf0\xa2\xa7')  # 0x57f0a2a7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.grapple_struggle_time))

        data.write(b'\xd1R(1')  # 0xd1522831
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hypermode_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x89m[\xd9')  # 0x896d5bd9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.armor_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8dJ&h')  # 0x8d4a2668
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x8d4a2668.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf4\x13\x94\xf6')  # 0xf41394f6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf41394f6))

        data.write(b'\xb1\xb4I\x17')  # 0xb1b44917
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ice_grenade_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x7f\xbc~\x81')  # 0x7fbc7e81
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x7fbc7e81.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xff\x94H\x85')  # 0xff944885
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xff944885))

        data.write(b'\x19\xf4\xe7d')  # 0x19f4e764
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x19f4e764))

        data.write(b'\x05\x0c\xb8n')  # 0x50cb86e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x050cb86e))

        data.write(b'\xe3l\x17\x8f')  # 0xe36c178f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe36c178f))

        data.write(b'0c\xbb\xf1')  # 0x3063bbf1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x3063bbf1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'Y\x97\xeb\xe1')  # 0x5997ebe1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0x5997ebe1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc9"\xf0\xe0')  # 0xc922f0e0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rush_range_min))

        data.write(b'/B_\x01')  # 0x2f425f01
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rush_range_max))

        data.write(b';\xe0\xa6k')  # 0x3be0a66b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3be0a66b))

        data.write(b'\xf5\x86\x83o')  # 0xf586836f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf586836f))

        data.write(b's\x12\xf1\xc1')  # 0x7312f1c1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7312f1c1))

        data.write(b'wSb\xcf')  # 0x775362cf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x775362cf))

        data.write(b'\xf1\xc7\x10a')  # 0xf1c71061
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf1c71061))

        data.write(b'?\x19lx')  # 0x3f196c78
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.missile_freeze_distance))

        data.write(b'x\xdf\x0b}')  # 0x78df0b7d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.surfing_projectile_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xca\x04\xd7V')  # 0xca04d756
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xca04d756))

        data.write(b'\xd9A1\xfd')  # 0xd94131fd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xd94131fd))

        data.write(b'\x82\x1b\x0c\x82')  # 0x821b0c82
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x821b0c82))

        data.write(b'\xe4\xfej\xf6')  # 0xe4fe6af6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe4fe6af6))

        data.write(b'~\xf4\xef\xfe')  # 0x7ef4effe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7ef4effe))

        data.write(b'?\xe3\xd0x')  # 0x3fe3d078
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3fe3d078))

        data.write(b'\x1d\xcc~a')  # 0x1dcc7e61
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.surf_height_min))

        data.write(b'\xfb\xac\xd1\x80')  # 0xfbacd180
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.surf_height_max))

        data.write(b'\xe4\xcdy$')  # 0xe4cd7924
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.elevation_timer))

        data.write(b'0V\xff\xba')  # 0x3056ffba
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.shard_storm_timer))

        data.write(b'Y^8\xd6')  # 0x595e38d6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.ice_summon_timer))

        data.write(b'm\x0b\xa0A')  # 0x6d0ba041
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.rush_timer))

        data.write(b'\xc7X\xf5.')  # 0xc758f52e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xc758f52e))

        data.write(b'9\xd7&^')  # 0x39d7265e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.surf_timer))

        data.write(b'\xf8\x0f\xca\xe2')  # 0xf80fcae2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf80fcae2))

        data.write(b'S\x1a\x8c\x85')  # 0x531a8c85
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_gandrayda))

        data.write(b'i\x17F\xf2')  # 0x691746f2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x691746f2))

        data.write(b'\xcf\x19qH')  # 0xcf197148
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcf197148))

        data.write(b'\x9e\xe0\xca\x15')  # 0x9ee0ca15
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9ee0ca15))

        data.write(b'\xfcb\x9fr')  # 0xfc629f72
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfc629f72))

        data.write(b"\xef'y\xd9")  # 0xef2779d9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xef2779d9))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RundasDataJson", data)
        return cls(
            unknown_0x1aeb498d=json_data['unknown_0x1aeb498d'],
            unknown_0x9c7f3b23=json_data['unknown_0x9c7f3b23'],
            unknown_0x706186d2=json_data['unknown_0x706186d2'],
            unknown_0x3f5d6545=json_data['unknown_0x3f5d6545'],
            unknown_0x59a93220=json_data['unknown_0x59a93220'],
            unknown_0x6cc73ec1=json_data['unknown_0x6cc73ec1'],
            grapple_struggle_time=json_data['grapple_struggle_time'],
            hypermode_vulnerability=DamageVulnerability.from_json(json_data['hypermode_vulnerability']),
            armor_vulnerability=DamageVulnerability.from_json(json_data['armor_vulnerability']),
            damage_info_0x8d4a2668=DamageInfo.from_json(json_data['damage_info_0x8d4a2668']),
            unknown_0xf41394f6=json_data['unknown_0xf41394f6'],
            ice_grenade_damage=DamageInfo.from_json(json_data['ice_grenade_damage']),
            damage_info_0x7fbc7e81=DamageInfo.from_json(json_data['damage_info_0x7fbc7e81']),
            unknown_0xff944885=json_data['unknown_0xff944885'],
            unknown_0x19f4e764=json_data['unknown_0x19f4e764'],
            unknown_0x050cb86e=json_data['unknown_0x050cb86e'],
            unknown_0xe36c178f=json_data['unknown_0xe36c178f'],
            damage_info_0x3063bbf1=DamageInfo.from_json(json_data['damage_info_0x3063bbf1']),
            damage_info_0x5997ebe1=DamageInfo.from_json(json_data['damage_info_0x5997ebe1']),
            rush_range_min=json_data['rush_range_min'],
            rush_range_max=json_data['rush_range_max'],
            unknown_0x3be0a66b=json_data['unknown_0x3be0a66b'],
            unknown_0xf586836f=json_data['unknown_0xf586836f'],
            unknown_0x7312f1c1=json_data['unknown_0x7312f1c1'],
            unknown_0x775362cf=json_data['unknown_0x775362cf'],
            unknown_0xf1c71061=json_data['unknown_0xf1c71061'],
            missile_freeze_distance=json_data['missile_freeze_distance'],
            surfing_projectile_damage=DamageInfo.from_json(json_data['surfing_projectile_damage']),
            unknown_0xca04d756=json_data['unknown_0xca04d756'],
            unknown_0xd94131fd=json_data['unknown_0xd94131fd'],
            unknown_0x821b0c82=json_data['unknown_0x821b0c82'],
            unknown_0xe4fe6af6=json_data['unknown_0xe4fe6af6'],
            unknown_0x7ef4effe=json_data['unknown_0x7ef4effe'],
            unknown_0x3fe3d078=json_data['unknown_0x3fe3d078'],
            surf_height_min=json_data['surf_height_min'],
            surf_height_max=json_data['surf_height_max'],
            elevation_timer=json_data['elevation_timer'],
            shard_storm_timer=json_data['shard_storm_timer'],
            ice_summon_timer=json_data['ice_summon_timer'],
            rush_timer=json_data['rush_timer'],
            unknown_0xc758f52e=json_data['unknown_0xc758f52e'],
            surf_timer=json_data['surf_timer'],
            unknown_0xf80fcae2=json_data['unknown_0xf80fcae2'],
            is_gandrayda=json_data['is_gandrayda'],
            unknown_0x691746f2=json_data['unknown_0x691746f2'],
            unknown_0xcf197148=json_data['unknown_0xcf197148'],
            unknown_0x9ee0ca15=json_data['unknown_0x9ee0ca15'],
            unknown_0xfc629f72=json_data['unknown_0xfc629f72'],
            unknown_0xef2779d9=json_data['unknown_0xef2779d9'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0x1aeb498d': self.unknown_0x1aeb498d,
            'unknown_0x9c7f3b23': self.unknown_0x9c7f3b23,
            'unknown_0x706186d2': self.unknown_0x706186d2,
            'unknown_0x3f5d6545': self.unknown_0x3f5d6545,
            'unknown_0x59a93220': self.unknown_0x59a93220,
            'unknown_0x6cc73ec1': self.unknown_0x6cc73ec1,
            'grapple_struggle_time': self.grapple_struggle_time,
            'hypermode_vulnerability': self.hypermode_vulnerability.to_json(),
            'armor_vulnerability': self.armor_vulnerability.to_json(),
            'damage_info_0x8d4a2668': self.damage_info_0x8d4a2668.to_json(),
            'unknown_0xf41394f6': self.unknown_0xf41394f6,
            'ice_grenade_damage': self.ice_grenade_damage.to_json(),
            'damage_info_0x7fbc7e81': self.damage_info_0x7fbc7e81.to_json(),
            'unknown_0xff944885': self.unknown_0xff944885,
            'unknown_0x19f4e764': self.unknown_0x19f4e764,
            'unknown_0x050cb86e': self.unknown_0x050cb86e,
            'unknown_0xe36c178f': self.unknown_0xe36c178f,
            'damage_info_0x3063bbf1': self.damage_info_0x3063bbf1.to_json(),
            'damage_info_0x5997ebe1': self.damage_info_0x5997ebe1.to_json(),
            'rush_range_min': self.rush_range_min,
            'rush_range_max': self.rush_range_max,
            'unknown_0x3be0a66b': self.unknown_0x3be0a66b,
            'unknown_0xf586836f': self.unknown_0xf586836f,
            'unknown_0x7312f1c1': self.unknown_0x7312f1c1,
            'unknown_0x775362cf': self.unknown_0x775362cf,
            'unknown_0xf1c71061': self.unknown_0xf1c71061,
            'missile_freeze_distance': self.missile_freeze_distance,
            'surfing_projectile_damage': self.surfing_projectile_damage.to_json(),
            'unknown_0xca04d756': self.unknown_0xca04d756,
            'unknown_0xd94131fd': self.unknown_0xd94131fd,
            'unknown_0x821b0c82': self.unknown_0x821b0c82,
            'unknown_0xe4fe6af6': self.unknown_0xe4fe6af6,
            'unknown_0x7ef4effe': self.unknown_0x7ef4effe,
            'unknown_0x3fe3d078': self.unknown_0x3fe3d078,
            'surf_height_min': self.surf_height_min,
            'surf_height_max': self.surf_height_max,
            'elevation_timer': self.elevation_timer,
            'shard_storm_timer': self.shard_storm_timer,
            'ice_summon_timer': self.ice_summon_timer,
            'rush_timer': self.rush_timer,
            'unknown_0xc758f52e': self.unknown_0xc758f52e,
            'surf_timer': self.surf_timer,
            'unknown_0xf80fcae2': self.unknown_0xf80fcae2,
            'is_gandrayda': self.is_gandrayda,
            'unknown_0x691746f2': self.unknown_0x691746f2,
            'unknown_0xcf197148': self.unknown_0xcf197148,
            'unknown_0x9ee0ca15': self.unknown_0x9ee0ca15,
            'unknown_0xfc629f72': self.unknown_0xfc629f72,
            'unknown_0xef2779d9': self.unknown_0xef2779d9,
        }


def _decode_unknown_0x1aeb498d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9c7f3b23(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x706186d2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3f5d6545(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x59a93220(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6cc73ec1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_grapple_struggle_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf41394f6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xff944885(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x19f4e764(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x050cb86e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe36c178f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rush_range_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rush_range_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3be0a66b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf586836f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7312f1c1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x775362cf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf1c71061(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_missile_freeze_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xca04d756(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xd94131fd(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x821b0c82(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xe4fe6af6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7ef4effe(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3fe3d078(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_surf_height_min(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_surf_height_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_elevation_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_shard_storm_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ice_summon_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_rush_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc758f52e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_surf_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf80fcae2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_is_gandrayda(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x691746f2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcf197148(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9ee0ca15(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfc629f72(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xef2779d9(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1aeb498d: ('unknown_0x1aeb498d', _decode_unknown_0x1aeb498d),
    0x9c7f3b23: ('unknown_0x9c7f3b23', _decode_unknown_0x9c7f3b23),
    0x706186d2: ('unknown_0x706186d2', _decode_unknown_0x706186d2),
    0x3f5d6545: ('unknown_0x3f5d6545', _decode_unknown_0x3f5d6545),
    0x59a93220: ('unknown_0x59a93220', _decode_unknown_0x59a93220),
    0x6cc73ec1: ('unknown_0x6cc73ec1', _decode_unknown_0x6cc73ec1),
    0x57f0a2a7: ('grapple_struggle_time', _decode_grapple_struggle_time),
    0xd1522831: ('hypermode_vulnerability', DamageVulnerability.from_stream),
    0x896d5bd9: ('armor_vulnerability', DamageVulnerability.from_stream),
    0x8d4a2668: ('damage_info_0x8d4a2668', DamageInfo.from_stream),
    0xf41394f6: ('unknown_0xf41394f6', _decode_unknown_0xf41394f6),
    0xb1b44917: ('ice_grenade_damage', DamageInfo.from_stream),
    0x7fbc7e81: ('damage_info_0x7fbc7e81', DamageInfo.from_stream),
    0xff944885: ('unknown_0xff944885', _decode_unknown_0xff944885),
    0x19f4e764: ('unknown_0x19f4e764', _decode_unknown_0x19f4e764),
    0x50cb86e: ('unknown_0x050cb86e', _decode_unknown_0x050cb86e),
    0xe36c178f: ('unknown_0xe36c178f', _decode_unknown_0xe36c178f),
    0x3063bbf1: ('damage_info_0x3063bbf1', DamageInfo.from_stream),
    0x5997ebe1: ('damage_info_0x5997ebe1', DamageInfo.from_stream),
    0xc922f0e0: ('rush_range_min', _decode_rush_range_min),
    0x2f425f01: ('rush_range_max', _decode_rush_range_max),
    0x3be0a66b: ('unknown_0x3be0a66b', _decode_unknown_0x3be0a66b),
    0xf586836f: ('unknown_0xf586836f', _decode_unknown_0xf586836f),
    0x7312f1c1: ('unknown_0x7312f1c1', _decode_unknown_0x7312f1c1),
    0x775362cf: ('unknown_0x775362cf', _decode_unknown_0x775362cf),
    0xf1c71061: ('unknown_0xf1c71061', _decode_unknown_0xf1c71061),
    0x3f196c78: ('missile_freeze_distance', _decode_missile_freeze_distance),
    0x78df0b7d: ('surfing_projectile_damage', DamageInfo.from_stream),
    0xca04d756: ('unknown_0xca04d756', _decode_unknown_0xca04d756),
    0xd94131fd: ('unknown_0xd94131fd', _decode_unknown_0xd94131fd),
    0x821b0c82: ('unknown_0x821b0c82', _decode_unknown_0x821b0c82),
    0xe4fe6af6: ('unknown_0xe4fe6af6', _decode_unknown_0xe4fe6af6),
    0x7ef4effe: ('unknown_0x7ef4effe', _decode_unknown_0x7ef4effe),
    0x3fe3d078: ('unknown_0x3fe3d078', _decode_unknown_0x3fe3d078),
    0x1dcc7e61: ('surf_height_min', _decode_surf_height_min),
    0xfbacd180: ('surf_height_max', _decode_surf_height_max),
    0xe4cd7924: ('elevation_timer', _decode_elevation_timer),
    0x3056ffba: ('shard_storm_timer', _decode_shard_storm_timer),
    0x595e38d6: ('ice_summon_timer', _decode_ice_summon_timer),
    0x6d0ba041: ('rush_timer', _decode_rush_timer),
    0xc758f52e: ('unknown_0xc758f52e', _decode_unknown_0xc758f52e),
    0x39d7265e: ('surf_timer', _decode_surf_timer),
    0xf80fcae2: ('unknown_0xf80fcae2', _decode_unknown_0xf80fcae2),
    0x531a8c85: ('is_gandrayda', _decode_is_gandrayda),
    0x691746f2: ('unknown_0x691746f2', _decode_unknown_0x691746f2),
    0xcf197148: ('unknown_0xcf197148', _decode_unknown_0xcf197148),
    0x9ee0ca15: ('unknown_0x9ee0ca15', _decode_unknown_0x9ee0ca15),
    0xfc629f72: ('unknown_0xfc629f72', _decode_unknown_0xfc629f72),
    0xef2779d9: ('unknown_0xef2779d9', _decode_unknown_0xef2779d9),
}
