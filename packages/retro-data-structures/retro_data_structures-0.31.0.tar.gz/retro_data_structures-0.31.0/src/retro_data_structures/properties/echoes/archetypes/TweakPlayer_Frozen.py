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

    class TweakPlayer_FrozenJson(typing_extensions.TypedDict):
        frozen_timer: float
        frozen_jump_counter: int
        frozen_damage_threshold: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xb3f20575, 0xb851d54f, 0x33b040bf)


@dataclasses.dataclass()
class TweakPlayer_Frozen(BaseProperty):
    frozen_timer: float = dataclasses.field(default=18.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb3f20575, original_name='FrozenTimer'
        ),
    })
    frozen_jump_counter: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0xb851d54f, original_name='FrozenJumpCounter'
        ),
    })
    frozen_damage_threshold: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x33b040bf, original_name='FrozenDamageThreshold'
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
        if property_count != 3:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHlLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(30))
        assert (dec[0], dec[3], dec[6]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\xb3\xf2\x05u')  # 0xb3f20575
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.frozen_timer))

        data.write(b'\xb8Q\xd5O')  # 0xb851d54f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.frozen_jump_counter))

        data.write(b'3\xb0@\xbf')  # 0x33b040bf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.frozen_damage_threshold))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakPlayer_FrozenJson", data)
        return cls(
            frozen_timer=json_data['frozen_timer'],
            frozen_jump_counter=json_data['frozen_jump_counter'],
            frozen_damage_threshold=json_data['frozen_damage_threshold'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'frozen_timer': self.frozen_timer,
            'frozen_jump_counter': self.frozen_jump_counter,
            'frozen_damage_threshold': self.frozen_damage_threshold,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_frozen_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_frozen_jump_counter(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_frozen_damage_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb3f20575: ('frozen_timer', _decode_frozen_timer),
    0xb851d54f: ('frozen_jump_counter', _decode_frozen_jump_counter),
    0x33b040bf: ('frozen_damage_threshold', _decode_frozen_damage_threshold),
}
