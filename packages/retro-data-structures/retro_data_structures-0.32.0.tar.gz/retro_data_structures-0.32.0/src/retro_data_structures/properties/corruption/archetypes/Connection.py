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
from retro_data_structures.properties.corruption.archetypes.ActivationTime import ActivationTime

if typing.TYPE_CHECKING:
    class ConnectionJson(typing_extensions.TypedDict):
        connection_index: int
        activation_times: list[json_util.JsonObject]
    

def _from_json_activation_times(data: json_util.JsonValue) -> list[ActivationTime]:
    json_data = typing.cast(list[json_util.JsonObject], data)
    return [ActivationTime.from_json(item) for item in json_data]


def _to_json_activation_times(obj: list[ActivationTime]) -> json_util.JsonValue:
    return [item.to_json() for item in obj]


@dataclasses.dataclass()
class Connection(BaseProperty):
    connection_index: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000000, original_name='Connection Index'
        ),
    })
    activation_times: list[ActivationTime] = dataclasses.field(default_factory=list, metadata={
        'reflection': FieldReflection[list[ActivationTime]](
            list[ActivationTime], id=0x00000001, original_name='Activation Times', from_json=_from_json_activation_times, to_json=_to_json_activation_times
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        connection_index = struct.unpack('>h', data.read(2))[0]
        activation_times = [ActivationTime.from_stream(data, property_size) for _ in range(struct.unpack(">L", data.read(4))[0])]
        return cls(connection_index, activation_times)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>h', self.connection_index))
        array = self.activation_times
        data.write(struct.pack(">L", len(array)))
        for item in array:
            item.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ConnectionJson", data)
        return cls(
            connection_index=json_data['connection_index'],
            activation_times=[ActivationTime.from_json(item) for item in json_data['activation_times']],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'connection_index': self.connection_index,
            'activation_times': [item.to_json() for item in self.activation_times],
        }
