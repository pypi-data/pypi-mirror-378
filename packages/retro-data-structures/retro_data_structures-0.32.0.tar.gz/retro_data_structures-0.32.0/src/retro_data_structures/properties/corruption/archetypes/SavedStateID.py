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
    class SavedStateIDJson(typing_extensions.TypedDict):
        state_id_1: int
        state_id_2: int
        state_id_3: int
        state_id_4: int
    

@dataclasses.dataclass()
class SavedStateID(BaseProperty):
    state_id_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000000, original_name='State ID 1'
        ),
    })
    state_id_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000001, original_name='State ID 2'
        ),
    })
    state_id_3: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000002, original_name='State ID 3'
        ),
    })
    state_id_4: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000003, original_name='State ID 4'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        state_id_1 = struct.unpack('>l', data.read(4))[0]
        state_id_2 = struct.unpack('>l', data.read(4))[0]
        state_id_3 = struct.unpack('>l', data.read(4))[0]
        state_id_4 = struct.unpack('>l', data.read(4))[0]
        return cls(state_id_1, state_id_2, state_id_3, state_id_4)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>l', self.state_id_1))
        data.write(struct.pack('>l', self.state_id_2))
        data.write(struct.pack('>l', self.state_id_3))
        data.write(struct.pack('>l', self.state_id_4))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SavedStateIDJson", data)
        return cls(
            state_id_1=json_data['state_id_1'],
            state_id_2=json_data['state_id_2'],
            state_id_3=json_data['state_id_3'],
            state_id_4=json_data['state_id_4'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'state_id_1': self.state_id_1,
            'state_id_2': self.state_id_2,
            'state_id_3': self.state_id_3,
            'state_id_4': self.state_id_4,
        }
