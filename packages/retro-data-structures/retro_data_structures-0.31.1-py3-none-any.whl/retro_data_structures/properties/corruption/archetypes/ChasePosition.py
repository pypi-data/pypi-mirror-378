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
from retro_data_structures.properties.corruption.archetypes.Convergence import Convergence

if typing.TYPE_CHECKING:
    class ChasePositionJson(typing_extensions.TypedDict):
        angle: float
        distance: float
        z_offset: float
        angular_convergence: json_util.JsonObject
    

@dataclasses.dataclass()
class ChasePosition(BaseProperty):
    angle: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x382a1973, original_name='Angle'
        ),
    })
    distance: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc3bf43be, original_name='Distance'
        ),
    })
    z_offset: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8033f9a3, original_name='ZOffset'
        ),
    })
    angular_convergence: Convergence = dataclasses.field(default_factory=Convergence, metadata={
        'reflection': FieldReflection[Convergence](
            Convergence, id=0x69114952, original_name='AngularConvergence', from_json=Convergence.from_json, to_json=Convergence.to_json
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
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x382a1973
        angle = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc3bf43be
        distance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8033f9a3
        z_offset = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69114952
        angular_convergence = Convergence.from_stream(data, property_size)
    
        return cls(angle, distance, z_offset, angular_convergence)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'8*\x19s')  # 0x382a1973
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.angle))

        data.write(b'\xc3\xbfC\xbe')  # 0xc3bf43be
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.distance))

        data.write(b'\x803\xf9\xa3')  # 0x8033f9a3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.z_offset))

        data.write(b'i\x11IR')  # 0x69114952
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.angular_convergence.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ChasePositionJson", data)
        return cls(
            angle=json_data['angle'],
            distance=json_data['distance'],
            z_offset=json_data['z_offset'],
            angular_convergence=Convergence.from_json(json_data['angular_convergence']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'angle': self.angle,
            'distance': self.distance,
            'z_offset': self.z_offset,
            'angular_convergence': self.angular_convergence.to_json(),
        }


def _decode_angle(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_z_offset(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x382a1973: ('angle', _decode_angle),
    0xc3bf43be: ('distance', _decode_distance),
    0x8033f9a3: ('z_offset', _decode_z_offset),
    0x69114952: ('angular_convergence', Convergence.from_stream),
}
