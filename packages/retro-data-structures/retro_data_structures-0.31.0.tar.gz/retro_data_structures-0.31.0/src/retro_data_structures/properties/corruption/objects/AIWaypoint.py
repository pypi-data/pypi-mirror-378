# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseObjectType
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties

if typing.TYPE_CHECKING:
    class AIWaypointJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        speed: float
        pause: float
        unknown_0xc6705a00: int
        locator_index: int
        unknown_0x166979d4: int
    

@dataclasses.dataclass()
class AIWaypoint(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    speed: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6392404e, original_name='Speed'
        ),
    })
    pause: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x80f7e605, original_name='Pause'
        ),
    })
    unknown_0xc6705a00: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc6705a00, original_name='Unknown'
        ),
    })
    locator_index: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xa790c6a9, original_name='LocatorIndex'
        ),
    })
    unknown_0x166979d4: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x166979d4, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'AIWP'

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 6:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6392404e
        speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80f7e605
        pause = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6705a00
        unknown_0xc6705a00 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa790c6a9
        locator_index = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x166979d4
        unknown_0x166979d4 = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, speed, pause, unknown_0xc6705a00, locator_index, unknown_0x166979d4)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'c\x92@N')  # 0x6392404e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed))

        data.write(b'\x80\xf7\xe6\x05')  # 0x80f7e605
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.pause))

        data.write(b'\xc6pZ\x00')  # 0xc6705a00
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xc6705a00))

        data.write(b'\xa7\x90\xc6\xa9')  # 0xa790c6a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.locator_index))

        data.write(b'\x16iy\xd4')  # 0x166979d4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0x166979d4))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AIWaypointJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            speed=json_data['speed'],
            pause=json_data['pause'],
            unknown_0xc6705a00=json_data['unknown_0xc6705a00'],
            locator_index=json_data['locator_index'],
            unknown_0x166979d4=json_data['unknown_0x166979d4'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'speed': self.speed,
            'pause': self.pause,
            'unknown_0xc6705a00': self.unknown_0xc6705a00,
            'locator_index': self.locator_index,
            'unknown_0x166979d4': self.unknown_0x166979d4,
        }


def _decode_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_pause(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc6705a00(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_locator_index(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_unknown_0x166979d4(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x6392404e: ('speed', _decode_speed),
    0x80f7e605: ('pause', _decode_pause),
    0xc6705a00: ('unknown_0xc6705a00', _decode_unknown_0xc6705a00),
    0xa790c6a9: ('locator_index', _decode_locator_index),
    0x166979d4: ('unknown_0x166979d4', _decode_unknown_0x166979d4),
}
