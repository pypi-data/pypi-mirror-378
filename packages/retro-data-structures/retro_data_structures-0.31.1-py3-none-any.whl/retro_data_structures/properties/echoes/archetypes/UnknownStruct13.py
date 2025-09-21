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
from retro_data_structures.properties.echoes.archetypes.AudioPlaybackParms import AudioPlaybackParms
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class UnknownStruct13Json(typing_extensions.TypedDict):
        unknown: float
        min_attack_range: float
        max_attack_range: float
        damage: json_util.JsonObject
        projectile: int
        mold_effect: int
        mold_damage: json_util.JsonObject
        sound_mold: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct13(BaseProperty):
    unknown: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd258ec09, original_name='Unknown'
        ),
    })
    min_attack_range: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x58434916, original_name='MinAttackRange'
        ),
    })
    max_attack_range: float = dataclasses.field(default=35.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xff77c96f, original_name='MaxAttackRange'
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    projectile: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xef485db9, original_name='Projectile'
        ),
    })
    mold_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5979d9e1, original_name='MoldEffect'
        ),
    })
    mold_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x80742e2e, original_name='MoldDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    sound_mold: AudioPlaybackParms = dataclasses.field(default_factory=AudioPlaybackParms, metadata={
        'reflection': FieldReflection[AudioPlaybackParms](
            AudioPlaybackParms, id=0xf5cfb8af, original_name='Sound_Mold', from_json=AudioPlaybackParms.from_json, to_json=AudioPlaybackParms.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        assert property_id == 0xd258ec09
        unknown = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58434916
        min_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xff77c96f
        max_attack_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 40.0, 'di_knock_back_power': 10.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef485db9
        projectile = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5979d9e1
        mold_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80742e2e
        mold_damage = DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 0.08332999795675278})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf5cfb8af
        sound_mold = AudioPlaybackParms.from_stream(data, property_size)
    
        return cls(unknown, min_attack_range, max_attack_range, damage, projectile, mold_effect, mold_damage, sound_mold)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\xd2X\xec\t')  # 0xd258ec09
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown))

        data.write(b'XCI\x16')  # 0x58434916
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_attack_range))

        data.write(b'\xffw\xc9o')  # 0xff77c96f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_attack_range))

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 40.0, 'di_knock_back_power': 10.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xefH]\xb9')  # 0xef485db9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.projectile))

        data.write(b'Yy\xd9\xe1')  # 0x5979d9e1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.mold_effect))

        data.write(b'\x80t..')  # 0x80742e2e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.mold_damage.to_stream(data, default_override={'di_weapon_type': 11, 'di_damage': 0.08332999795675278})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf5\xcf\xb8\xaf')  # 0xf5cfb8af
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.sound_mold.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct13Json", data)
        return cls(
            unknown=json_data['unknown'],
            min_attack_range=json_data['min_attack_range'],
            max_attack_range=json_data['max_attack_range'],
            damage=DamageInfo.from_json(json_data['damage']),
            projectile=json_data['projectile'],
            mold_effect=json_data['mold_effect'],
            mold_damage=DamageInfo.from_json(json_data['mold_damage']),
            sound_mold=AudioPlaybackParms.from_json(json_data['sound_mold']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown': self.unknown,
            'min_attack_range': self.min_attack_range,
            'max_attack_range': self.max_attack_range,
            'damage': self.damage.to_json(),
            'projectile': self.projectile,
            'mold_effect': self.mold_effect,
            'mold_damage': self.mold_damage.to_json(),
            'sound_mold': self.sound_mold.to_json(),
        }

    def _dependencies_for_projectile(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.projectile)

    def _dependencies_for_mold_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.mold_effect)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.damage.dependencies_for, "damage", "DamageInfo"),
            (self._dependencies_for_projectile, "projectile", "AssetId"),
            (self._dependencies_for_mold_effect, "mold_effect", "AssetId"),
            (self.mold_damage.dependencies_for, "mold_damage", "DamageInfo"),
            (self.sound_mold.dependencies_for, "sound_mold", "AudioPlaybackParms"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for UnknownStruct13.{field_name} ({field_type}): {e}"
                )


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_attack_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 40.0, 'di_knock_back_power': 10.0})


def _decode_projectile(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_mold_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_mold_damage(data: typing.BinaryIO, property_size: int) -> DamageInfo:
    return DamageInfo.from_stream(data, property_size, default_override={'di_weapon_type': 11, 'di_damage': 0.08332999795675278})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd258ec09: ('unknown', _decode_unknown),
    0x58434916: ('min_attack_range', _decode_min_attack_range),
    0xff77c96f: ('max_attack_range', _decode_max_attack_range),
    0x337f9524: ('damage', _decode_damage),
    0xef485db9: ('projectile', _decode_projectile),
    0x5979d9e1: ('mold_effect', _decode_mold_effect),
    0x80742e2e: ('mold_damage', _decode_mold_damage),
    0xf5cfb8af: ('sound_mold', AudioPlaybackParms.from_stream),
}
