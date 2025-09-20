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
from retro_data_structures.properties.corruption.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.corruption.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.corruption.core.AnimationParameters import AnimationParameters
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class SeedBoss1HandDataJson(typing_extensions.TypedDict):
        health: json_util.JsonObject
        vulnerability: json_util.JsonObject
        character_animation_set: json_util.JsonObject
        state_machine: int
        hand_actor_parameters: json_util.JsonObject
        explosion: int
        explosion_sound: int
        damage: json_util.JsonObject
        stop_homing_range: float
    

@dataclasses.dataclass()
class SeedBoss1HandData(BaseProperty):
    health: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0xcf90d15e, original_name='Health', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x7b71ae90, original_name='Vulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    character_animation_set: AnimationParameters = dataclasses.field(default_factory=AnimationParameters, metadata={
        'reflection': FieldReflection[AnimationParameters](
            AnimationParameters, id=0x71a5a198, original_name='CharacterAnimationSet', from_json=AnimationParameters.from_json, to_json=AnimationParameters.to_json
        ),
    })
    state_machine: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['FSM2'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x55744160, original_name='StateMachine'
        ),
    })
    hand_actor_parameters: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0xa30ee999, original_name='HandActorParameters', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    explosion: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd8c6d15c, original_name='Explosion'
        ),
    })
    explosion_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9a094814, original_name='ExplosionSound'
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    stop_homing_range: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x053ae4a7, original_name='StopHomingRange'
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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcf90d15e
        health = HealthInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b71ae90
        vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71a5a198
        character_animation_set = AnimationParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x55744160
        state_machine = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa30ee999
        hand_actor_parameters = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd8c6d15c
        explosion = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a094814
        explosion_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x053ae4a7
        stop_homing_range = struct.unpack('>f', data.read(4))[0]
    
        return cls(health, vulnerability, character_animation_set, state_machine, hand_actor_parameters, explosion, explosion_sound, damage, stop_homing_range)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\t')  # 9 properties

        data.write(b'\xcf\x90\xd1^')  # 0xcf90d15e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.health.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{q\xae\x90')  # 0x7b71ae90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'q\xa5\xa1\x98')  # 0x71a5a198
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.character_animation_set.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'UtA`')  # 0x55744160
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.state_machine))

        data.write(b'\xa3\x0e\xe9\x99')  # 0xa30ee999
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hand_actor_parameters.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd8\xc6\xd1\\')  # 0xd8c6d15c
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.explosion))

        data.write(b'\x9a\tH\x14')  # 0x9a094814
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.explosion_sound))

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x05:\xe4\xa7')  # 0x53ae4a7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.stop_homing_range))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SeedBoss1HandDataJson", data)
        return cls(
            health=HealthInfo.from_json(json_data['health']),
            vulnerability=DamageVulnerability.from_json(json_data['vulnerability']),
            character_animation_set=AnimationParameters.from_json(json_data['character_animation_set']),
            state_machine=json_data['state_machine'],
            hand_actor_parameters=ActorParameters.from_json(json_data['hand_actor_parameters']),
            explosion=json_data['explosion'],
            explosion_sound=json_data['explosion_sound'],
            damage=DamageInfo.from_json(json_data['damage']),
            stop_homing_range=json_data['stop_homing_range'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'health': self.health.to_json(),
            'vulnerability': self.vulnerability.to_json(),
            'character_animation_set': self.character_animation_set.to_json(),
            'state_machine': self.state_machine,
            'hand_actor_parameters': self.hand_actor_parameters.to_json(),
            'explosion': self.explosion,
            'explosion_sound': self.explosion_sound,
            'damage': self.damage.to_json(),
            'stop_homing_range': self.stop_homing_range,
        }


def _decode_state_machine(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_explosion(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_explosion_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_stop_homing_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xcf90d15e: ('health', HealthInfo.from_stream),
    0x7b71ae90: ('vulnerability', DamageVulnerability.from_stream),
    0x71a5a198: ('character_animation_set', AnimationParameters.from_stream),
    0x55744160: ('state_machine', _decode_state_machine),
    0xa30ee999: ('hand_actor_parameters', ActorParameters.from_stream),
    0xd8c6d15c: ('explosion', _decode_explosion),
    0x9a094814: ('explosion_sound', _decode_explosion_sound),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0x53ae4a7: ('stop_homing_range', _decode_stop_homing_range),
}
