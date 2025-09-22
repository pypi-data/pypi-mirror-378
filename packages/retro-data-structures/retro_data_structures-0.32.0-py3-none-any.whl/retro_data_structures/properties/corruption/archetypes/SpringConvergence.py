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
    class SpringConvergenceJson(typing_extensions.TypedDict):
        critically_dampened: bool
        spring_constant: float
        dampen_constant: float
        threshold: float
        spring_max: float
        tardis: float
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0x6fa2f8bc, 0xb3823863, 0xb122a18d, 0x8e1b83f9, 0xacb1cdcb, 0x74d11538)


@dataclasses.dataclass()
class SpringConvergence(BaseProperty):
    critically_dampened: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x6fa2f8bc, original_name='CriticallyDampened'
        ),
    })
    spring_constant: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb3823863, original_name='SpringConstant'
        ),
    })
    dampen_constant: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb122a18d, original_name='DampenConstant'
        ),
    })
    threshold: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8e1b83f9, original_name='Threshold'
        ),
    })
    spring_max: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xacb1cdcb, original_name='SpringMax'
        ),
    })
    tardis: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x74d11538, original_name='Tardis'
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
        if property_count != 6:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LH?LHfLHfLHfLHfLHf')
    
        dec = _FAST_FORMAT.unpack(data.read(57))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'o\xa2\xf8\xbc')  # 0x6fa2f8bc
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.critically_dampened))

        data.write(b'\xb3\x828c')  # 0xb3823863
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spring_constant))

        data.write(b'\xb1"\xa1\x8d')  # 0xb122a18d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dampen_constant))

        data.write(b'\x8e\x1b\x83\xf9')  # 0x8e1b83f9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.threshold))

        data.write(b'\xac\xb1\xcd\xcb')  # 0xacb1cdcb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.spring_max))

        data.write(b't\xd1\x158')  # 0x74d11538
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.tardis))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpringConvergenceJson", data)
        return cls(
            critically_dampened=json_data['critically_dampened'],
            spring_constant=json_data['spring_constant'],
            dampen_constant=json_data['dampen_constant'],
            threshold=json_data['threshold'],
            spring_max=json_data['spring_max'],
            tardis=json_data['tardis'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'critically_dampened': self.critically_dampened,
            'spring_constant': self.spring_constant,
            'dampen_constant': self.dampen_constant,
            'threshold': self.threshold,
            'spring_max': self.spring_max,
            'tardis': self.tardis,
        }


def _decode_critically_dampened(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_spring_constant(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dampen_constant(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_spring_max(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_tardis(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6fa2f8bc: ('critically_dampened', _decode_critically_dampened),
    0xb3823863: ('spring_constant', _decode_spring_constant),
    0xb122a18d: ('dampen_constant', _decode_dampen_constant),
    0x8e1b83f9: ('threshold', _decode_threshold),
    0xacb1cdcb: ('spring_max', _decode_spring_max),
    0x74d11538: ('tardis', _decode_tardis),
}
