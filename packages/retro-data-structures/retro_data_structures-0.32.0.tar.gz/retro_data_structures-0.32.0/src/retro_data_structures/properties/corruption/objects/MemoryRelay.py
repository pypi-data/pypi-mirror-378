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
from retro_data_structures.properties.corruption.archetypes.SavedStateID import SavedStateID

if typing.TYPE_CHECKING:
    class MemoryRelayJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        object_id: json_util.JsonObject
        one_shot: bool
        delayed_action: bool
    

@dataclasses.dataclass()
class MemoryRelay(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    object_id: SavedStateID = dataclasses.field(default_factory=SavedStateID, metadata={
        'reflection': FieldReflection[SavedStateID](
            SavedStateID, id=0x16d9a75d, original_name='ObjectId', from_json=SavedStateID.from_json, to_json=SavedStateID.to_json
        ),
    })
    one_shot: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xead7b7bb, original_name='OneShot'
        ),
    })
    delayed_action: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xa905ccf0, original_name='DelayedAction'
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
        return 'MRLY'

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
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x16d9a75d
        object_id = SavedStateID.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xead7b7bb
        one_shot = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa905ccf0
        delayed_action = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, object_id, one_shot, delayed_action)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x04')  # 4 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x16\xd9\xa7]')  # 0x16d9a75d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.object_id.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xea\xd7\xb7\xbb')  # 0xead7b7bb
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.one_shot))

        data.write(b'\xa9\x05\xcc\xf0')  # 0xa905ccf0
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.delayed_action))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MemoryRelayJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            object_id=SavedStateID.from_json(json_data['object_id']),
            one_shot=json_data['one_shot'],
            delayed_action=json_data['delayed_action'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'object_id': self.object_id.to_json(),
            'one_shot': self.one_shot,
            'delayed_action': self.delayed_action,
        }


def _decode_one_shot(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_delayed_action(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x16d9a75d: ('object_id', SavedStateID.from_stream),
    0xead7b7bb: ('one_shot', _decode_one_shot),
    0xa905ccf0: ('delayed_action', _decode_delayed_action),
}
