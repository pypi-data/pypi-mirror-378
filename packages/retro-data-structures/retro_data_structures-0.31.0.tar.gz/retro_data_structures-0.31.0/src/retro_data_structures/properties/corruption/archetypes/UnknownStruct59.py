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
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class UnknownStruct59Json(typing_extensions.TypedDict):
        initial_swarm_size: int
        unknown_0xb3f4ee57: float
        chase_player_speed: float
        char: json_util.JsonObject
        swarm_bot_vulnerability: json_util.JsonObject
        part_0xb64ed093: int
        unknown_0x8fe03c41: float
        ring_idle_effect: int
        part_0x4d9ed8e1: int
        ring_projectile: int
        ring_projectile_damage: json_util.JsonObject
        bot_contact_damage: json_util.JsonObject
        visor_effect: int
        visor_impact_sound: int
    

@dataclasses.dataclass()
class UnknownStruct59(BaseProperty):
    initial_swarm_size: int = dataclasses.field(default=30, metadata={
        'reflection': FieldReflection[int](
            int, id=0xbea74138, original_name='InitialSwarmSize'
        ),
    })
    unknown_0xb3f4ee57: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb3f4ee57, original_name='Unknown'
        ),
    })
    chase_player_speed: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x116920b8, original_name='ChasePlayerSpeed'
        ),
    })
    char: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x4c64d3a6, original_name='CHAR', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    swarm_bot_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x00dd06cc, original_name='SwarmBotVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    part_0xb64ed093: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb64ed093, original_name='PART'
        ),
    })
    unknown_0x8fe03c41: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8fe03c41, original_name='Unknown'
        ),
    })
    ring_idle_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc90cda8c, original_name='RingIdleEffect'
        ),
    })
    part_0x4d9ed8e1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4d9ed8e1, original_name='PART'
        ),
    })
    ring_projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x21dc4c35, original_name='RingProjectile'
        ),
    })
    ring_projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x18f91880, original_name='RingProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    bot_contact_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xfcb5a8c3, original_name='BotContactDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe9c8e2bd, original_name='VisorEffect'
        ),
    })
    visor_impact_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x86ffb3f6, original_name='VisorImpactSound'
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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbea74138
        initial_swarm_size = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3f4ee57
        unknown_0xb3f4ee57 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x116920b8
        chase_player_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4c64d3a6
        char = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x00dd06cc
        swarm_bot_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb64ed093
        part_0xb64ed093 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8fe03c41
        unknown_0x8fe03c41 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc90cda8c
        ring_idle_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d9ed8e1
        part_0x4d9ed8e1 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21dc4c35
        ring_projectile = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x18f91880
        ring_projectile_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfcb5a8c3
        bot_contact_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9c8e2bd
        visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86ffb3f6
        visor_impact_sound = struct.unpack(">Q", data.read(8))[0]
    
        return cls(initial_swarm_size, unknown_0xb3f4ee57, chase_player_speed, char, swarm_bot_vulnerability, part_0xb64ed093, unknown_0x8fe03c41, ring_idle_effect, part_0x4d9ed8e1, ring_projectile, ring_projectile_damage, bot_contact_damage, visor_effect, visor_impact_sound)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'\xbe\xa7A8')  # 0xbea74138
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.initial_swarm_size))

        data.write(b'\xb3\xf4\xeeW')  # 0xb3f4ee57
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb3f4ee57))

        data.write(b'\x11i \xb8')  # 0x116920b8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.chase_player_speed))

        data.write(b'Ld\xd3\xa6')  # 0x4c64d3a6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.char.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x00\xdd\x06\xcc')  # 0xdd06cc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.swarm_bot_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb6N\xd0\x93')  # 0xb64ed093
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0xb64ed093))

        data.write(b'\x8f\xe0<A')  # 0x8fe03c41
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x8fe03c41))

        data.write(b'\xc9\x0c\xda\x8c')  # 0xc90cda8c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ring_idle_effect))

        data.write(b'M\x9e\xd8\xe1')  # 0x4d9ed8e1
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.part_0x4d9ed8e1))

        data.write(b'!\xdcL5')  # 0x21dc4c35
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.ring_projectile))

        data.write(b'\x18\xf9\x18\x80')  # 0x18f91880
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ring_projectile_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfc\xb5\xa8\xc3')  # 0xfcb5a8c3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bot_contact_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe9\xc8\xe2\xbd')  # 0xe9c8e2bd
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_effect))

        data.write(b'\x86\xff\xb3\xf6')  # 0x86ffb3f6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.visor_impact_sound))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct59Json", data)
        return cls(
            initial_swarm_size=json_data['initial_swarm_size'],
            unknown_0xb3f4ee57=json_data['unknown_0xb3f4ee57'],
            chase_player_speed=json_data['chase_player_speed'],
            char=AnimationParameters.from_json(json_data['char']),
            swarm_bot_vulnerability=DamageVulnerability.from_json(json_data['swarm_bot_vulnerability']),
            part_0xb64ed093=json_data['part_0xb64ed093'],
            unknown_0x8fe03c41=json_data['unknown_0x8fe03c41'],
            ring_idle_effect=json_data['ring_idle_effect'],
            part_0x4d9ed8e1=json_data['part_0x4d9ed8e1'],
            ring_projectile=json_data['ring_projectile'],
            ring_projectile_damage=DamageInfo.from_json(json_data['ring_projectile_damage']),
            bot_contact_damage=DamageInfo.from_json(json_data['bot_contact_damage']),
            visor_effect=json_data['visor_effect'],
            visor_impact_sound=json_data['visor_impact_sound'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'initial_swarm_size': self.initial_swarm_size,
            'unknown_0xb3f4ee57': self.unknown_0xb3f4ee57,
            'chase_player_speed': self.chase_player_speed,
            'char': self.char.to_json(),
            'swarm_bot_vulnerability': self.swarm_bot_vulnerability.to_json(),
            'part_0xb64ed093': self.part_0xb64ed093,
            'unknown_0x8fe03c41': self.unknown_0x8fe03c41,
            'ring_idle_effect': self.ring_idle_effect,
            'part_0x4d9ed8e1': self.part_0x4d9ed8e1,
            'ring_projectile': self.ring_projectile,
            'ring_projectile_damage': self.ring_projectile_damage.to_json(),
            'bot_contact_damage': self.bot_contact_damage.to_json(),
            'visor_effect': self.visor_effect,
            'visor_impact_sound': self.visor_impact_sound,
        }


def _decode_initial_swarm_size(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0xb3f4ee57(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_chase_player_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_part_0xb64ed093(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0x8fe03c41(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_ring_idle_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_part_0x4d9ed8e1(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_ring_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_visor_impact_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xbea74138: ('initial_swarm_size', _decode_initial_swarm_size),
    0xb3f4ee57: ('unknown_0xb3f4ee57', _decode_unknown_0xb3f4ee57),
    0x116920b8: ('chase_player_speed', _decode_chase_player_speed),
    0x4c64d3a6: ('char', AnimationParameters.from_stream),
    0xdd06cc: ('swarm_bot_vulnerability', DamageVulnerability.from_stream),
    0xb64ed093: ('part_0xb64ed093', _decode_part_0xb64ed093),
    0x8fe03c41: ('unknown_0x8fe03c41', _decode_unknown_0x8fe03c41),
    0xc90cda8c: ('ring_idle_effect', _decode_ring_idle_effect),
    0x4d9ed8e1: ('part_0x4d9ed8e1', _decode_part_0x4d9ed8e1),
    0x21dc4c35: ('ring_projectile', _decode_ring_projectile),
    0x18f91880: ('ring_projectile_damage', DamageInfo.from_stream),
    0xfcb5a8c3: ('bot_contact_damage', DamageInfo.from_stream),
    0xe9c8e2bd: ('visor_effect', _decode_visor_effect),
    0x86ffb3f6: ('visor_impact_sound', _decode_visor_impact_sound),
}
