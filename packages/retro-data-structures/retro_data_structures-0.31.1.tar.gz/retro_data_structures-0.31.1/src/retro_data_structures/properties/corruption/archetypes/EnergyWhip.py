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
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class EnergyWhipJson(typing_extensions.TypedDict):
        animation_info: json_util.JsonObject
        damage: json_util.JsonObject
        hyper_damage: json_util.JsonObject
        unknown_0x894c2b5d: float
        max_attack_dist: float
        world_impact_effect: int
        player_impact_sound: int
        unknown_0xde12b1d5: bool
    

@dataclasses.dataclass()
class EnergyWhip(BaseProperty):
    animation_info: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x5c1ffc8d, original_name='AnimationInfo', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    hyper_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xb3dabf84, original_name='HyperDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_0x894c2b5d: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x894c2b5d, original_name='Unknown'
        ),
    })
    max_attack_dist: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2ed25f50, original_name='MaxAttackDist'
        ),
    })
    world_impact_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb154f3fd, original_name='WorldImpactEffect'
        ),
    })
    player_impact_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe33a996d, original_name='PlayerImpactSound'
        ),
    })
    unknown_0xde12b1d5: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xde12b1d5, original_name='Unknown'
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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5c1ffc8d
        animation_info = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3dabf84
        hyper_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x894c2b5d
        unknown_0x894c2b5d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2ed25f50
        max_attack_dist = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb154f3fd
        world_impact_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe33a996d
        player_impact_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde12b1d5
        unknown_0xde12b1d5 = struct.unpack('>?', data.read(1))[0]
    
        return cls(animation_info, damage, hyper_damage, unknown_0x894c2b5d, max_attack_dist, world_impact_effect, player_impact_sound, unknown_0xde12b1d5)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\\\x1f\xfc\x8d')  # 0x5c1ffc8d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.animation_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3\xda\xbf\x84')  # 0xb3dabf84
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x89L+]')  # 0x894c2b5d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x894c2b5d))

        data.write(b'.\xd2_P')  # 0x2ed25f50
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_dist))

        data.write(b'\xb1T\xf3\xfd')  # 0xb154f3fd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.world_impact_effect))

        data.write(b'\xe3:\x99m')  # 0xe33a996d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.player_impact_sound))

        data.write(b'\xde\x12\xb1\xd5')  # 0xde12b1d5
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xde12b1d5))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("EnergyWhipJson", data)
        return cls(
            animation_info=AnimationParameters.from_json(json_data['animation_info']),
            damage=DamageInfo.from_json(json_data['damage']),
            hyper_damage=DamageInfo.from_json(json_data['hyper_damage']),
            unknown_0x894c2b5d=json_data['unknown_0x894c2b5d'],
            max_attack_dist=json_data['max_attack_dist'],
            world_impact_effect=json_data['world_impact_effect'],
            player_impact_sound=json_data['player_impact_sound'],
            unknown_0xde12b1d5=json_data['unknown_0xde12b1d5'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'animation_info': self.animation_info.to_json(),
            'damage': self.damage.to_json(),
            'hyper_damage': self.hyper_damage.to_json(),
            'unknown_0x894c2b5d': self.unknown_0x894c2b5d,
            'max_attack_dist': self.max_attack_dist,
            'world_impact_effect': self.world_impact_effect,
            'player_impact_sound': self.player_impact_sound,
            'unknown_0xde12b1d5': self.unknown_0xde12b1d5,
        }


def _decode_unknown_0x894c2b5d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_dist(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_world_impact_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_player_impact_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xde12b1d5(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x5c1ffc8d: ('animation_info', AnimationParameters.from_stream),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0xb3dabf84: ('hyper_damage', DamageInfo.from_stream),
    0x894c2b5d: ('unknown_0x894c2b5d', _decode_unknown_0x894c2b5d),
    0x2ed25f50: ('max_attack_dist', _decode_max_attack_dist),
    0xb154f3fd: ('world_impact_effect', _decode_world_impact_effect),
    0xe33a996d: ('player_impact_sound', _decode_player_impact_sound),
    0xde12b1d5: ('unknown_0xde12b1d5', _decode_unknown_0xde12b1d5),
}
