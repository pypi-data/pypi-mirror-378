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
import retro_data_structures.enums.prime as enums

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class DamageInfoJson(typing_extensions.TypedDict):
        weapon_type: int
        damage: float
        radius: float
        knockback_power: float
    

@dataclasses.dataclass()
class DamageInfo(BaseProperty):
    weapon_type: enums.WeaponTypeEnum = dataclasses.field(default=enums.WeaponTypeEnum.Power, metadata={
        'reflection': FieldReflection[enums.WeaponTypeEnum](
            enums.WeaponTypeEnum, id=0x00000000, original_name='Weapon Type', from_json=enums.WeaponTypeEnum.from_json, to_json=enums.WeaponTypeEnum.to_json
        ),
    })
    damage: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='Damage'
        ),
    })
    radius: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000002, original_name='Radius'
        ),
    })
    knockback_power: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000003, original_name='Knockback Power'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        weapon_type = enums.WeaponTypeEnum.from_stream(data)
        damage = struct.unpack('>f', data.read(4))[0]
        radius = struct.unpack('>f', data.read(4))[0]
        knockback_power = struct.unpack('>f', data.read(4))[0]
        return cls(weapon_type, damage, radius, knockback_power)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        self.weapon_type.to_stream(data)
        data.write(struct.pack('>f', self.damage))
        data.write(struct.pack('>f', self.radius))
        data.write(struct.pack('>f', self.knockback_power))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("DamageInfoJson", data)
        return cls(
            weapon_type=enums.WeaponTypeEnum.from_json(json_data['weapon_type']),
            damage=json_data['damage'],
            radius=json_data['radius'],
            knockback_power=json_data['knockback_power'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'weapon_type': self.weapon_type.to_json(),
            'damage': self.damage,
            'radius': self.radius,
            'knockback_power': self.knockback_power,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
