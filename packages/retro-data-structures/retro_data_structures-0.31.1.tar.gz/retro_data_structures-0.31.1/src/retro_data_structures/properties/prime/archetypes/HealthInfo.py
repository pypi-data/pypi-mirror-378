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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class HealthInfoJson(typing_extensions.TypedDict):
        health: float
        knockback_resistance: float
    

@dataclasses.dataclass()
class HealthInfo(BaseProperty):
    health: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000000, original_name='Health'
        ),
    })
    knockback_resistance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='Knockback Resistance'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        health = struct.unpack('>f', data.read(4))[0]
        knockback_resistance = struct.unpack('>f', data.read(4))[0]
        return cls(health, knockback_resistance)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>f', self.health))
        data.write(struct.pack('>f', self.knockback_resistance))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("HealthInfoJson", data)
        return cls(
            health=json_data['health'],
            knockback_resistance=json_data['knockback_resistance'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'health': self.health,
            'knockback_resistance': self.knockback_resistance,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
