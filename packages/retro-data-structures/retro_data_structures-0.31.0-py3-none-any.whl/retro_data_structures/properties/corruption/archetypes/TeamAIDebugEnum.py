# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection

if typing.TYPE_CHECKING:
    class TeamAIDebugEnumJson(typing_extensions.TypedDict):
        team_ai_state: int
    

class TeamAIState(enum.IntEnum):
    Unknown1 = 4229634895
    Unknown2 = 2906748314
    Unknown3 = 210580899
    Unknown4 = 3276372239

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x94d97b5a)


@dataclasses.dataclass()
class TeamAIDebugEnum(BaseProperty):
    team_ai_state: TeamAIState = dataclasses.field(default=TeamAIState.Unknown1, metadata={
        'reflection': FieldReflection[TeamAIState](
            TeamAIState, id=0x94d97b5a, original_name='TeamAIState', from_json=TeamAIState.from_json, to_json=TeamAIState.to_json
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
        if property_count != 1:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHL')
    
        dec = _FAST_FORMAT.unpack(data.read(10))
        assert (dec[0]) == _FAST_IDS
        return cls(
            TeamAIState(dec[2]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x01')  # 1 properties

        data.write(b'\x94\xd9{Z')  # 0x94d97b5a
        data.write(b'\x00\x04')  # size
        self.team_ai_state.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TeamAIDebugEnumJson", data)
        return cls(
            team_ai_state=TeamAIState.from_json(json_data['team_ai_state']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'team_ai_state': self.team_ai_state.to_json(),
        }


def _decode_team_ai_state(data: typing.BinaryIO, property_size: int) -> TeamAIState:
    return TeamAIState.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x94d97b5a: ('team_ai_state', _decode_team_ai_state),
}
