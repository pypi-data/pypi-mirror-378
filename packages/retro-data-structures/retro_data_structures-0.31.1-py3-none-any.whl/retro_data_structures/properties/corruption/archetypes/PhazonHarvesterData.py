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
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.corruption.archetypes.FlyerMovementMode import FlyerMovementMode
from retro_data_structures.properties.corruption.archetypes.LaunchProjectileData import LaunchProjectileData
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class PhazonHarvesterDataJson(typing_extensions.TypedDict):
        starts_flying: bool
        weapon_projectile: json_util.JsonObject
        weapon_vulnerability: json_util.JsonObject
        weapon_stun_damage: float
        unknown_0x6b554a8d: float
        unknown_0x08772297: float
        unknown_0xee178d76: float
        weapon_max_pitch: float
        weapon_min_pitch: float
        max_weapon_rotation: float
        weapon_rotation_speed: float
        hatch_open_time: float
        hatch_close_time: float
        flight_normal: json_util.JsonObject
        flight_attack: json_util.JsonObject
        weapon_model: int
        left_front_hatch_model: int
        left_back_hatch_model: int
        right_fron_hatch_model: int
        right_back_hatch_model: int
    

@dataclasses.dataclass()
class PhazonHarvesterData(BaseProperty):
    starts_flying: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1ce8f439, original_name='StartsFlying'
        ),
    })
    weapon_projectile: LaunchProjectileData = dataclasses.field(default_factory=LaunchProjectileData, metadata={
        'reflection': FieldReflection[LaunchProjectileData](
            LaunchProjectileData, id=0x2036077f, original_name='WeaponProjectile', from_json=LaunchProjectileData.from_json, to_json=LaunchProjectileData.to_json
        ),
    })
    weapon_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xae22e0dc, original_name='WeaponVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    weapon_stun_damage: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4fdc1683, original_name='WeaponStunDamage'
        ),
    })
    unknown_0x6b554a8d: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6b554a8d, original_name='Unknown'
        ),
    })
    unknown_0x08772297: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08772297, original_name='Unknown'
        ),
    })
    unknown_0xee178d76: float = dataclasses.field(default=6.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xee178d76, original_name='Unknown'
        ),
    })
    weapon_max_pitch: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x75608ed3, original_name='WeaponMaxPitch'
        ),
    })
    weapon_min_pitch: float = dataclasses.field(default=-90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x352ff6a5, original_name='WeaponMinPitch'
        ),
    })
    max_weapon_rotation: float = dataclasses.field(default=70.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcd8ab1e3, original_name='MaxWeaponRotation'
        ),
    })
    weapon_rotation_speed: float = dataclasses.field(default=90.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf0e64d85, original_name='WeaponRotationSpeed'
        ),
    })
    hatch_open_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b3449f5, original_name='HatchOpenTime'
        ),
    })
    hatch_close_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x1dd9e8bf, original_name='HatchCloseTime'
        ),
    })
    flight_normal: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0x130cf1a1, original_name='FlightNormal', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    flight_attack: FlyerMovementMode = dataclasses.field(default_factory=FlyerMovementMode, metadata={
        'reflection': FieldReflection[FlyerMovementMode](
            FlyerMovementMode, id=0xfc51df90, original_name='FlightAttack', from_json=FlyerMovementMode.from_json, to_json=FlyerMovementMode.to_json
        ),
    })
    weapon_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x7a154e49, original_name='WeaponModel'
        ),
    })
    left_front_hatch_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc7426b90, original_name='LeftFrontHatchModel'
        ),
    })
    left_back_hatch_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe2efee98, original_name='LeftBackHatchModel'
        ),
    })
    right_fron_hatch_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x155bf24b, original_name='RightFronHatchModel'
        ),
    })
    right_back_hatch_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd757cb94, original_name='RightBackHatchModel'
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
        if property_count != 20:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1ce8f439
        starts_flying = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2036077f
        weapon_projectile = LaunchProjectileData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae22e0dc
        weapon_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4fdc1683
        weapon_stun_damage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6b554a8d
        unknown_0x6b554a8d = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08772297
        unknown_0x08772297 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xee178d76
        unknown_0xee178d76 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x75608ed3
        weapon_max_pitch = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x352ff6a5
        weapon_min_pitch = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcd8ab1e3
        max_weapon_rotation = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf0e64d85
        weapon_rotation_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b3449f5
        hatch_open_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1dd9e8bf
        hatch_close_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x130cf1a1
        flight_normal = FlyerMovementMode.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc51df90
        flight_attack = FlyerMovementMode.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a154e49
        weapon_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc7426b90
        left_front_hatch_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe2efee98
        left_back_hatch_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x155bf24b
        right_fron_hatch_model = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd757cb94
        right_back_hatch_model = struct.unpack(">Q", data.read(8))[0]
    
        return cls(starts_flying, weapon_projectile, weapon_vulnerability, weapon_stun_damage, unknown_0x6b554a8d, unknown_0x08772297, unknown_0xee178d76, weapon_max_pitch, weapon_min_pitch, max_weapon_rotation, weapon_rotation_speed, hatch_open_time, hatch_close_time, flight_normal, flight_attack, weapon_model, left_front_hatch_model, left_back_hatch_model, right_fron_hatch_model, right_back_hatch_model)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x14')  # 20 properties

        data.write(b'\x1c\xe8\xf49')  # 0x1ce8f439
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.starts_flying))

        data.write(b' 6\x07\x7f')  # 0x2036077f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weapon_projectile.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xae"\xe0\xdc')  # 0xae22e0dc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weapon_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'O\xdc\x16\x83')  # 0x4fdc1683
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.weapon_stun_damage))

        data.write(b'kUJ\x8d')  # 0x6b554a8d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6b554a8d))

        data.write(b'\x08w"\x97')  # 0x8772297
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x08772297))

        data.write(b'\xee\x17\x8dv')  # 0xee178d76
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xee178d76))

        data.write(b'u`\x8e\xd3')  # 0x75608ed3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.weapon_max_pitch))

        data.write(b'5/\xf6\xa5')  # 0x352ff6a5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.weapon_min_pitch))

        data.write(b'\xcd\x8a\xb1\xe3')  # 0xcd8ab1e3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_weapon_rotation))

        data.write(b'\xf0\xe6M\x85')  # 0xf0e64d85
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.weapon_rotation_speed))

        data.write(b'+4I\xf5')  # 0x2b3449f5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hatch_open_time))

        data.write(b'\x1d\xd9\xe8\xbf')  # 0x1dd9e8bf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hatch_close_time))

        data.write(b'\x13\x0c\xf1\xa1')  # 0x130cf1a1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flight_normal.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfcQ\xdf\x90')  # 0xfc51df90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flight_attack.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'z\x15NI')  # 0x7a154e49
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.weapon_model))

        data.write(b'\xc7Bk\x90')  # 0xc7426b90
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.left_front_hatch_model))

        data.write(b'\xe2\xef\xee\x98')  # 0xe2efee98
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.left_back_hatch_model))

        data.write(b'\x15[\xf2K')  # 0x155bf24b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.right_fron_hatch_model))

        data.write(b'\xd7W\xcb\x94')  # 0xd757cb94
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.right_back_hatch_model))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PhazonHarvesterDataJson", data)
        return cls(
            starts_flying=json_data['starts_flying'],
            weapon_projectile=LaunchProjectileData.from_json(json_data['weapon_projectile']),
            weapon_vulnerability=DamageVulnerability.from_json(json_data['weapon_vulnerability']),
            weapon_stun_damage=json_data['weapon_stun_damage'],
            unknown_0x6b554a8d=json_data['unknown_0x6b554a8d'],
            unknown_0x08772297=json_data['unknown_0x08772297'],
            unknown_0xee178d76=json_data['unknown_0xee178d76'],
            weapon_max_pitch=json_data['weapon_max_pitch'],
            weapon_min_pitch=json_data['weapon_min_pitch'],
            max_weapon_rotation=json_data['max_weapon_rotation'],
            weapon_rotation_speed=json_data['weapon_rotation_speed'],
            hatch_open_time=json_data['hatch_open_time'],
            hatch_close_time=json_data['hatch_close_time'],
            flight_normal=FlyerMovementMode.from_json(json_data['flight_normal']),
            flight_attack=FlyerMovementMode.from_json(json_data['flight_attack']),
            weapon_model=json_data['weapon_model'],
            left_front_hatch_model=json_data['left_front_hatch_model'],
            left_back_hatch_model=json_data['left_back_hatch_model'],
            right_fron_hatch_model=json_data['right_fron_hatch_model'],
            right_back_hatch_model=json_data['right_back_hatch_model'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'starts_flying': self.starts_flying,
            'weapon_projectile': self.weapon_projectile.to_json(),
            'weapon_vulnerability': self.weapon_vulnerability.to_json(),
            'weapon_stun_damage': self.weapon_stun_damage,
            'unknown_0x6b554a8d': self.unknown_0x6b554a8d,
            'unknown_0x08772297': self.unknown_0x08772297,
            'unknown_0xee178d76': self.unknown_0xee178d76,
            'weapon_max_pitch': self.weapon_max_pitch,
            'weapon_min_pitch': self.weapon_min_pitch,
            'max_weapon_rotation': self.max_weapon_rotation,
            'weapon_rotation_speed': self.weapon_rotation_speed,
            'hatch_open_time': self.hatch_open_time,
            'hatch_close_time': self.hatch_close_time,
            'flight_normal': self.flight_normal.to_json(),
            'flight_attack': self.flight_attack.to_json(),
            'weapon_model': self.weapon_model,
            'left_front_hatch_model': self.left_front_hatch_model,
            'left_back_hatch_model': self.left_back_hatch_model,
            'right_fron_hatch_model': self.right_fron_hatch_model,
            'right_back_hatch_model': self.right_back_hatch_model,
        }


def _decode_starts_flying(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_weapon_stun_damage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x6b554a8d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x08772297(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xee178d76(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_weapon_max_pitch(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_weapon_min_pitch(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_weapon_rotation(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_weapon_rotation_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hatch_open_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hatch_close_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_weapon_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_left_front_hatch_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_left_back_hatch_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_right_fron_hatch_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_right_back_hatch_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1ce8f439: ('starts_flying', _decode_starts_flying),
    0x2036077f: ('weapon_projectile', LaunchProjectileData.from_stream),
    0xae22e0dc: ('weapon_vulnerability', DamageVulnerability.from_stream),
    0x4fdc1683: ('weapon_stun_damage', _decode_weapon_stun_damage),
    0x6b554a8d: ('unknown_0x6b554a8d', _decode_unknown_0x6b554a8d),
    0x8772297: ('unknown_0x08772297', _decode_unknown_0x08772297),
    0xee178d76: ('unknown_0xee178d76', _decode_unknown_0xee178d76),
    0x75608ed3: ('weapon_max_pitch', _decode_weapon_max_pitch),
    0x352ff6a5: ('weapon_min_pitch', _decode_weapon_min_pitch),
    0xcd8ab1e3: ('max_weapon_rotation', _decode_max_weapon_rotation),
    0xf0e64d85: ('weapon_rotation_speed', _decode_weapon_rotation_speed),
    0x2b3449f5: ('hatch_open_time', _decode_hatch_open_time),
    0x1dd9e8bf: ('hatch_close_time', _decode_hatch_close_time),
    0x130cf1a1: ('flight_normal', FlyerMovementMode.from_stream),
    0xfc51df90: ('flight_attack', FlyerMovementMode.from_stream),
    0x7a154e49: ('weapon_model', _decode_weapon_model),
    0xc7426b90: ('left_front_hatch_model', _decode_left_front_hatch_model),
    0xe2efee98: ('left_back_hatch_model', _decode_left_back_hatch_model),
    0x155bf24b: ('right_fron_hatch_model', _decode_right_fron_hatch_model),
    0xd757cb94: ('right_back_hatch_model', _decode_right_back_hatch_model),
}
