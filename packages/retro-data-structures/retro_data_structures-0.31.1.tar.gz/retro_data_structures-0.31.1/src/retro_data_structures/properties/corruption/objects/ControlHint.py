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
from retro_data_structures.properties.corruption.archetypes.CommandData import CommandData
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties

if typing.TYPE_CHECKING:
    class ControlHintJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        priority: int
        timer: float
        cancel_method: int
        cancel_press_count: int
        cancel_press_time: float
        cancel_timer: float
        cancel_velocity: float
        unknown: int
        command1: json_util.JsonObject
        command2: json_util.JsonObject
        command3: json_util.JsonObject
        command4: json_util.JsonObject
        command5: json_util.JsonObject
        command6: json_util.JsonObject
        command7: json_util.JsonObject
        command8: json_util.JsonObject
    

@dataclasses.dataclass()
class ControlHint(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    priority: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x42087650, original_name='Priority'
        ),
    })
    timer: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8747552e, original_name='Timer'
        ),
    })
    cancel_method: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7b167c40, original_name='CancelMethod'
        ),
    })
    cancel_press_count: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xaa8d1afe, original_name='CancelPressCount'
        ),
    })
    cancel_press_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x26765b82, original_name='CancelPressTime'
        ),
    })
    cancel_timer: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6a45d9d0, original_name='CancelTimer'
        ),
    })
    cancel_velocity: float = dataclasses.field(default=0.009999999776482582, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc492fedf, original_name='CancelVelocity'
        ),
    })
    unknown: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9a78a8bb, original_name='Unknown'
        ),
    })
    command1: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0xa0840dd7, original_name='Command1', from_json=CommandData.from_json, to_json=CommandData.to_json
        ),
    })
    command2: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0xd71adf27, original_name='Command2', from_json=CommandData.from_json, to_json=CommandData.to_json
        ),
    })
    command3: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0x4cbf9348, original_name='Command3', from_json=CommandData.from_json, to_json=CommandData.to_json
        ),
    })
    command4: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0x38277ac7, original_name='Command4', from_json=CommandData.from_json, to_json=CommandData.to_json
        ),
    })
    command5: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0xa38236a8, original_name='Command5', from_json=CommandData.from_json, to_json=CommandData.to_json
        ),
    })
    command6: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0xd41ce458, original_name='Command6', from_json=CommandData.from_json, to_json=CommandData.to_json
        ),
    })
    command7: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0x4fb9a837, original_name='Command7', from_json=CommandData.from_json, to_json=CommandData.to_json
        ),
    })
    command8: CommandData = dataclasses.field(default_factory=CommandData, metadata={
        'reflection': FieldReflection[CommandData](
            CommandData, id=0x3d2d3746, original_name='Command8', from_json=CommandData.from_json, to_json=CommandData.to_json
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
        return 'CTLH'

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
        if property_count != 17:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42087650
        priority = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8747552e
        timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b167c40
        cancel_method = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa8d1afe
        cancel_press_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x26765b82
        cancel_press_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6a45d9d0
        cancel_timer = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc492fedf
        cancel_velocity = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a78a8bb
        unknown = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa0840dd7
        command1 = CommandData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd71adf27
        command2 = CommandData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4cbf9348
        command3 = CommandData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x38277ac7
        command4 = CommandData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa38236a8
        command5 = CommandData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd41ce458
        command6 = CommandData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4fb9a837
        command7 = CommandData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3d2d3746
        command8 = CommandData.from_stream(data, property_size)
    
        return cls(editor_properties, priority, timer, cancel_method, cancel_press_count, cancel_press_time, cancel_timer, cancel_velocity, unknown, command1, command2, command3, command4, command5, command6, command7, command8)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x11')  # 17 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'B\x08vP')  # 0x42087650
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.priority))

        data.write(b'\x87GU.')  # 0x8747552e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.timer))

        data.write(b'{\x16|@')  # 0x7b167c40
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.cancel_method))

        data.write(b'\xaa\x8d\x1a\xfe')  # 0xaa8d1afe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.cancel_press_count))

        data.write(b'&v[\x82')  # 0x26765b82
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cancel_press_time))

        data.write(b'jE\xd9\xd0')  # 0x6a45d9d0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cancel_timer))

        data.write(b'\xc4\x92\xfe\xdf')  # 0xc492fedf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cancel_velocity))

        data.write(b'\x9ax\xa8\xbb')  # 0x9a78a8bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown))

        data.write(b'\xa0\x84\r\xd7')  # 0xa0840dd7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command1.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"\xd7\x1a\xdf'")  # 0xd71adf27
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'L\xbf\x93H')  # 0x4cbf9348
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command3.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"8'z\xc7")  # 0x38277ac7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command4.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa3\x826\xa8')  # 0xa38236a8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command5.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd4\x1c\xe4X')  # 0xd41ce458
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'O\xb9\xa87')  # 0x4fb9a837
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'=-7F')  # 0x3d2d3746
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command8.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ControlHintJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            priority=json_data['priority'],
            timer=json_data['timer'],
            cancel_method=json_data['cancel_method'],
            cancel_press_count=json_data['cancel_press_count'],
            cancel_press_time=json_data['cancel_press_time'],
            cancel_timer=json_data['cancel_timer'],
            cancel_velocity=json_data['cancel_velocity'],
            unknown=json_data['unknown'],
            command1=CommandData.from_json(json_data['command1']),
            command2=CommandData.from_json(json_data['command2']),
            command3=CommandData.from_json(json_data['command3']),
            command4=CommandData.from_json(json_data['command4']),
            command5=CommandData.from_json(json_data['command5']),
            command6=CommandData.from_json(json_data['command6']),
            command7=CommandData.from_json(json_data['command7']),
            command8=CommandData.from_json(json_data['command8']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'priority': self.priority,
            'timer': self.timer,
            'cancel_method': self.cancel_method,
            'cancel_press_count': self.cancel_press_count,
            'cancel_press_time': self.cancel_press_time,
            'cancel_timer': self.cancel_timer,
            'cancel_velocity': self.cancel_velocity,
            'unknown': self.unknown,
            'command1': self.command1.to_json(),
            'command2': self.command2.to_json(),
            'command3': self.command3.to_json(),
            'command4': self.command4.to_json(),
            'command5': self.command5.to_json(),
            'command6': self.command6.to_json(),
            'command7': self.command7.to_json(),
            'command8': self.command8.to_json(),
        }


def _decode_priority(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cancel_method(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cancel_press_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_cancel_press_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cancel_timer(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_cancel_velocity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x42087650: ('priority', _decode_priority),
    0x8747552e: ('timer', _decode_timer),
    0x7b167c40: ('cancel_method', _decode_cancel_method),
    0xaa8d1afe: ('cancel_press_count', _decode_cancel_press_count),
    0x26765b82: ('cancel_press_time', _decode_cancel_press_time),
    0x6a45d9d0: ('cancel_timer', _decode_cancel_timer),
    0xc492fedf: ('cancel_velocity', _decode_cancel_velocity),
    0x9a78a8bb: ('unknown', _decode_unknown),
    0xa0840dd7: ('command1', CommandData.from_stream),
    0xd71adf27: ('command2', CommandData.from_stream),
    0x4cbf9348: ('command3', CommandData.from_stream),
    0x38277ac7: ('command4', CommandData.from_stream),
    0xa38236a8: ('command5', CommandData.from_stream),
    0xd41ce458: ('command6', CommandData.from_stream),
    0x4fb9a837: ('command7', CommandData.from_stream),
    0x3d2d3746: ('command8', CommandData.from_stream),
}
