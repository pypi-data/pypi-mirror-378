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
from retro_data_structures.properties.corruption.archetypes.ControlCommands import ControlCommands
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties

if typing.TYPE_CHECKING:
    class ControllerActionJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        command: json_util.JsonObject
        one_shot: bool
        disable_during_cinematics: bool
        auto_press_during_cinematic_skip: bool
        decay_time: float
    

@dataclasses.dataclass()
class ControllerAction(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    command: ControlCommands = dataclasses.field(default_factory=ControlCommands, metadata={
        'reflection': FieldReflection[ControlCommands](
            ControlCommands, id=0x710fe5d7, original_name='Command', from_json=ControlCommands.from_json, to_json=ControlCommands.to_json
        ),
    })
    one_shot: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xead7b7bb, original_name='OneShot'
        ),
    })
    disable_during_cinematics: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x29f446fc, original_name='DisableDuringCinematics'
        ),
    })
    auto_press_during_cinematic_skip: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xc731ae61, original_name='AutoPressDuringCinematicSkip'
        ),
    })
    decay_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfc827f63, original_name='DecayTime'
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
        return 'CNTA'

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
        assert property_id == 0x710fe5d7
        command = ControlCommands.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xead7b7bb
        one_shot = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x29f446fc
        disable_during_cinematics = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc731ae61
        auto_press_during_cinematic_skip = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfc827f63
        decay_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, command, one_shot, disable_during_cinematics, auto_press_during_cinematic_skip, decay_time)

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

        data.write(b'q\x0f\xe5\xd7')  # 0x710fe5d7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.command.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xea\xd7\xb7\xbb')  # 0xead7b7bb
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.one_shot))

        data.write(b')\xf4F\xfc')  # 0x29f446fc
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.disable_during_cinematics))

        data.write(b'\xc71\xaea')  # 0xc731ae61
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.auto_press_during_cinematic_skip))

        data.write(b'\xfc\x82\x7fc')  # 0xfc827f63
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.decay_time))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ControllerActionJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            command=ControlCommands.from_json(json_data['command']),
            one_shot=json_data['one_shot'],
            disable_during_cinematics=json_data['disable_during_cinematics'],
            auto_press_during_cinematic_skip=json_data['auto_press_during_cinematic_skip'],
            decay_time=json_data['decay_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'command': self.command.to_json(),
            'one_shot': self.one_shot,
            'disable_during_cinematics': self.disable_during_cinematics,
            'auto_press_during_cinematic_skip': self.auto_press_during_cinematic_skip,
            'decay_time': self.decay_time,
        }


def _decode_one_shot(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_disable_during_cinematics(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_auto_press_during_cinematic_skip(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_decay_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x710fe5d7: ('command', ControlCommands.from_stream),
    0xead7b7bb: ('one_shot', _decode_one_shot),
    0x29f446fc: ('disable_during_cinematics', _decode_disable_during_cinematics),
    0xc731ae61: ('auto_press_during_cinematic_skip', _decode_auto_press_during_cinematic_skip),
    0xfc827f63: ('decay_time', _decode_decay_time),
}
