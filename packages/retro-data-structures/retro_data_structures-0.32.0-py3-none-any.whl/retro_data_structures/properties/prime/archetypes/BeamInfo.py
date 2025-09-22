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
from retro_data_structures.properties.prime.archetypes.ShotParam import ShotParam

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class BeamInfoJson(typing_extensions.TypedDict):
        cooldown: float
        normal_damage: json_util.JsonObject
        charged_damage: json_util.JsonObject
    

@dataclasses.dataclass()
class BeamInfo(BaseProperty):
    cooldown: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000000, original_name='Cooldown'
        ),
    })
    normal_damage: ShotParam = dataclasses.field(default_factory=ShotParam, metadata={
        'reflection': FieldReflection[ShotParam](
            ShotParam, id=0x00000001, original_name='NormalDamage', from_json=ShotParam.from_json, to_json=ShotParam.to_json
        ),
    })
    charged_damage: ShotParam = dataclasses.field(default_factory=ShotParam, metadata={
        'reflection': FieldReflection[ShotParam](
            ShotParam, id=0x00000002, original_name='ChargedDamage', from_json=ShotParam.from_json, to_json=ShotParam.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        cooldown = struct.unpack('>f', data.read(4))[0]
        normal_damage = ShotParam.from_stream(data, property_size)
        charged_damage = ShotParam.from_stream(data, property_size)
        return cls(cooldown, normal_damage, charged_damage)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>f', self.cooldown))
        self.normal_damage.to_stream(data)
        self.charged_damage.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BeamInfoJson", data)
        return cls(
            cooldown=json_data['cooldown'],
            normal_damage=ShotParam.from_json(json_data['normal_damage']),
            charged_damage=ShotParam.from_json(json_data['charged_damage']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'cooldown': self.cooldown,
            'normal_damage': self.normal_damage.to_json(),
            'charged_damage': self.charged_damage.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.normal_damage.dependencies_for, "normal_damage", "ShotParam"),
            (self.charged_damage.dependencies_for, "charged_damage", "ShotParam"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for BeamInfo.{field_name} ({field_type}): {e}"
                )
