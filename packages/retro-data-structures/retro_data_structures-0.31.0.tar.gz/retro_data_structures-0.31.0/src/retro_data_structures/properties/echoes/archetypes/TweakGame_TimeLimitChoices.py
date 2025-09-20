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

    class TweakGame_TimeLimitChoicesJson(typing_extensions.TypedDict):
        time_limit0: float
        time_limit1: float
        time_limit2: float
        time_limit3: float
        time_limit4: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x779e8ff4, 0xbcc25c51, 0x3a562eff, 0xf10afd5a, 0xec0fcde2)


@dataclasses.dataclass()
class TweakGame_TimeLimitChoices(BaseProperty):
    time_limit0: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x779e8ff4, original_name='TimeLimit0'
        ),
    })
    time_limit1: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbcc25c51, original_name='TimeLimit1'
        ),
    })
    time_limit2: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3a562eff, original_name='TimeLimit2'
        ),
    })
    time_limit3: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf10afd5a, original_name='TimeLimit3'
        ),
    })
    time_limit4: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xec0fcde2, original_name='TimeLimit4'
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
        if property_count != 5:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(50))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'w\x9e\x8f\xf4')  # 0x779e8ff4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_limit0))

        data.write(b'\xbc\xc2\\Q')  # 0xbcc25c51
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_limit1))

        data.write(b':V.\xff')  # 0x3a562eff
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_limit2))

        data.write(b'\xf1\n\xfdZ')  # 0xf10afd5a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_limit3))

        data.write(b'\xec\x0f\xcd\xe2')  # 0xec0fcde2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.time_limit4))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGame_TimeLimitChoicesJson", data)
        return cls(
            time_limit0=json_data['time_limit0'],
            time_limit1=json_data['time_limit1'],
            time_limit2=json_data['time_limit2'],
            time_limit3=json_data['time_limit3'],
            time_limit4=json_data['time_limit4'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'time_limit0': self.time_limit0,
            'time_limit1': self.time_limit1,
            'time_limit2': self.time_limit2,
            'time_limit3': self.time_limit3,
            'time_limit4': self.time_limit4,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_time_limit0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_time_limit1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_time_limit2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_time_limit3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_time_limit4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x779e8ff4: ('time_limit0', _decode_time_limit0),
    0xbcc25c51: ('time_limit1', _decode_time_limit1),
    0x3a562eff: ('time_limit2', _decode_time_limit2),
    0xf10afd5a: ('time_limit3', _decode_time_limit3),
    0xec0fcde2: ('time_limit4', _decode_time_limit4),
}
