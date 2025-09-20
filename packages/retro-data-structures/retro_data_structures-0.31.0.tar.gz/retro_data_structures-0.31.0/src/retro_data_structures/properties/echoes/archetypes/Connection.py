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

    class ConnectionJson(typing_extensions.TypedDict):
        connection_index: int
        activation_times: list[float]
        unknown: bool
    

def _from_json_activation_times(data: json_util.JsonValue) -> list[float]:
    json_data = typing.cast(list[float], data)
    return [item for item in json_data]


def _to_json_activation_times(obj: list[float]) -> json_util.JsonValue:
    return [item for item in obj]


@dataclasses.dataclass()
class Connection(BaseProperty):
    connection_index: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000000, original_name='Connection Index'
        ),
    })
    activation_times: list[float] = dataclasses.field(default_factory=list, metadata={
        'reflection': FieldReflection[list[float]](
            list[float], id=0x00000001, original_name='Activation Times', from_json=_from_json_activation_times, to_json=_to_json_activation_times
        ),
    })
    unknown: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000002, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        connection_index = struct.unpack('>h', data.read(2))[0]
        activation_times = list(struct.unpack('>' + 'f' * (count := struct.unpack(">L", data.read(4))[0]), data.read(count * 4)))
        unknown = struct.unpack('>?', data.read(1))[0]
        return cls(connection_index, activation_times, unknown)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>h', self.connection_index))
        array = self.activation_times
        data.write(struct.pack(">L", len(array)))
        for item in array:
            data.write(struct.pack('>f', item))
        data.write(struct.pack('>?', self.unknown))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ConnectionJson", data)
        return cls(
            connection_index=json_data['connection_index'],
            activation_times=[item for item in json_data['activation_times']],
            unknown=json_data['unknown'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'connection_index': self.connection_index,
            'activation_times': [item for item in self.activation_times],
            'unknown': self.unknown,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []
