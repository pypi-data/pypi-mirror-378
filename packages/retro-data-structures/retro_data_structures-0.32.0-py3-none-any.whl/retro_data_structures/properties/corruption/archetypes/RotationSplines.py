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
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class RotationSplinesJson(typing_extensions.TypedDict):
        x_rotation: json_util.JsonObject
        y_rotation: json_util.JsonObject
        z_rotation: json_util.JsonObject
    

@dataclasses.dataclass()
class RotationSplines(BaseProperty):
    x_rotation: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x69d8447d, original_name='XRotation', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    y_rotation: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xd0239f95, original_name='YRotation', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    z_rotation: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0xc15ef5ec, original_name='ZRotation', from_json=Spline.from_json, to_json=Spline.to_json
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
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x69d8447d
        x_rotation = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0239f95
        y_rotation = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc15ef5ec
        z_rotation = Spline.from_stream(data, property_size)
    
        return cls(x_rotation, y_rotation, z_rotation)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'i\xd8D}')  # 0x69d8447d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.x_rotation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd0#\x9f\x95')  # 0xd0239f95
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.y_rotation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc1^\xf5\xec')  # 0xc15ef5ec
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.z_rotation.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RotationSplinesJson", data)
        return cls(
            x_rotation=Spline.from_json(json_data['x_rotation']),
            y_rotation=Spline.from_json(json_data['y_rotation']),
            z_rotation=Spline.from_json(json_data['z_rotation']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'x_rotation': self.x_rotation.to_json(),
            'y_rotation': self.y_rotation.to_json(),
            'z_rotation': self.z_rotation.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x69d8447d: ('x_rotation', Spline.from_stream),
    0xd0239f95: ('y_rotation', Spline.from_stream),
    0xc15ef5ec: ('z_rotation', Spline.from_stream),
}
