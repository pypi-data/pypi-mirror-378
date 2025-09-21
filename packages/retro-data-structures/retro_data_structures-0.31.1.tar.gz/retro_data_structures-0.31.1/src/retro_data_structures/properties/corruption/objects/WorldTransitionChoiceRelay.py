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
from retro_data_structures.properties.corruption.archetypes.UnknownStruct66 import UnknownStruct66

if typing.TYPE_CHECKING:
    class WorldTransitionChoiceRelayJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        num_choices: int
        unknown_struct66: json_util.JsonObject
        unknown_0x6bb71e37: json_util.JsonObject
        unknown_0xfec7caa2: json_util.JsonObject
        unknown_0xa277e9cb: json_util.JsonObject
        unknown_0x37073d5e: json_util.JsonObject
        unknown_0x53e746a0: json_util.JsonObject
        unknown_0xc6979235: json_util.JsonObject
        unknown_0xea870072: json_util.JsonObject
        unknown_0x7ff7d4e7: json_util.JsonObject
        unknown_0x7db5008c: json_util.JsonObject
    

@dataclasses.dataclass()
class WorldTransitionChoiceRelay(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    num_choices: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x58b2a49b, original_name='NumChoices'
        ),
    })
    unknown_struct66: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0x0f5765c9, original_name='UnknownStruct66', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0x6bb71e37: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0x6bb71e37, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0xfec7caa2: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0xfec7caa2, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0xa277e9cb: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0xa277e9cb, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0x37073d5e: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0x37073d5e, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0x53e746a0: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0x53e746a0, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0xc6979235: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0xc6979235, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0xea870072: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0xea870072, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0x7ff7d4e7: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0x7ff7d4e7, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
        ),
    })
    unknown_0x7db5008c: UnknownStruct66 = dataclasses.field(default_factory=UnknownStruct66, metadata={
        'reflection': FieldReflection[UnknownStruct66](
            UnknownStruct66, id=0x7db5008c, original_name='Unknown', from_json=UnknownStruct66.from_json, to_json=UnknownStruct66.to_json
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
        return 'WTCR'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_ScriptWorldTeleporter.rso']

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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x58b2a49b
        num_choices = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0f5765c9
        unknown_struct66 = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6bb71e37
        unknown_0x6bb71e37 = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfec7caa2
        unknown_0xfec7caa2 = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa277e9cb
        unknown_0xa277e9cb = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37073d5e
        unknown_0x37073d5e = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x53e746a0
        unknown_0x53e746a0 = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc6979235
        unknown_0xc6979235 = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea870072
        unknown_0xea870072 = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7ff7d4e7
        unknown_0x7ff7d4e7 = UnknownStruct66.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7db5008c
        unknown_0x7db5008c = UnknownStruct66.from_stream(data, property_size)
    
        return cls(editor_properties, num_choices, unknown_struct66, unknown_0x6bb71e37, unknown_0xfec7caa2, unknown_0xa277e9cb, unknown_0x37073d5e, unknown_0x53e746a0, unknown_0xc6979235, unknown_0xea870072, unknown_0x7ff7d4e7, unknown_0x7db5008c)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x03')  # 3 properties
        num_properties_written = 3

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'X\xb2\xa4\x9b')  # 0x58b2a49b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.num_choices))

        data.write(b'\x0fWe\xc9')  # 0xf5765c9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct66.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        if self.unknown_0x6bb71e37 != default_override.get('unknown_0x6bb71e37', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'k\xb7\x1e7')  # 0x6bb71e37
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x6bb71e37.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0xfec7caa2 != default_override.get('unknown_0xfec7caa2', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'\xfe\xc7\xca\xa2')  # 0xfec7caa2
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0xfec7caa2.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0xa277e9cb != default_override.get('unknown_0xa277e9cb', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'\xa2w\xe9\xcb')  # 0xa277e9cb
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0xa277e9cb.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x37073d5e != default_override.get('unknown_0x37073d5e', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'7\x07=^')  # 0x37073d5e
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x37073d5e.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x53e746a0 != default_override.get('unknown_0x53e746a0', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'S\xe7F\xa0')  # 0x53e746a0
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x53e746a0.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0xc6979235 != default_override.get('unknown_0xc6979235', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'\xc6\x97\x925')  # 0xc6979235
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0xc6979235.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0xea870072 != default_override.get('unknown_0xea870072', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'\xea\x87\x00r')  # 0xea870072
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0xea870072.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x7ff7d4e7 != default_override.get('unknown_0x7ff7d4e7', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'\x7f\xf7\xd4\xe7')  # 0x7ff7d4e7
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x7ff7d4e7.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.unknown_0x7db5008c != default_override.get('unknown_0x7db5008c', UnknownStruct66()):
            num_properties_written += 1
            data.write(b'}\xb5\x00\x8c')  # 0x7db5008c
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.unknown_0x7db5008c.to_stream(data)
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.write(struct.pack(">H", num_properties_written))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("WorldTransitionChoiceRelayJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            num_choices=json_data['num_choices'],
            unknown_struct66=UnknownStruct66.from_json(json_data['unknown_struct66']),
            unknown_0x6bb71e37=UnknownStruct66.from_json(json_data['unknown_0x6bb71e37']),
            unknown_0xfec7caa2=UnknownStruct66.from_json(json_data['unknown_0xfec7caa2']),
            unknown_0xa277e9cb=UnknownStruct66.from_json(json_data['unknown_0xa277e9cb']),
            unknown_0x37073d5e=UnknownStruct66.from_json(json_data['unknown_0x37073d5e']),
            unknown_0x53e746a0=UnknownStruct66.from_json(json_data['unknown_0x53e746a0']),
            unknown_0xc6979235=UnknownStruct66.from_json(json_data['unknown_0xc6979235']),
            unknown_0xea870072=UnknownStruct66.from_json(json_data['unknown_0xea870072']),
            unknown_0x7ff7d4e7=UnknownStruct66.from_json(json_data['unknown_0x7ff7d4e7']),
            unknown_0x7db5008c=UnknownStruct66.from_json(json_data['unknown_0x7db5008c']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'num_choices': self.num_choices,
            'unknown_struct66': self.unknown_struct66.to_json(),
            'unknown_0x6bb71e37': self.unknown_0x6bb71e37.to_json(),
            'unknown_0xfec7caa2': self.unknown_0xfec7caa2.to_json(),
            'unknown_0xa277e9cb': self.unknown_0xa277e9cb.to_json(),
            'unknown_0x37073d5e': self.unknown_0x37073d5e.to_json(),
            'unknown_0x53e746a0': self.unknown_0x53e746a0.to_json(),
            'unknown_0xc6979235': self.unknown_0xc6979235.to_json(),
            'unknown_0xea870072': self.unknown_0xea870072.to_json(),
            'unknown_0x7ff7d4e7': self.unknown_0x7ff7d4e7.to_json(),
            'unknown_0x7db5008c': self.unknown_0x7db5008c.to_json(),
        }


def _decode_num_choices(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x58b2a49b: ('num_choices', _decode_num_choices),
    0xf5765c9: ('unknown_struct66', UnknownStruct66.from_stream),
    0x6bb71e37: ('unknown_0x6bb71e37', UnknownStruct66.from_stream),
    0xfec7caa2: ('unknown_0xfec7caa2', UnknownStruct66.from_stream),
    0xa277e9cb: ('unknown_0xa277e9cb', UnknownStruct66.from_stream),
    0x37073d5e: ('unknown_0x37073d5e', UnknownStruct66.from_stream),
    0x53e746a0: ('unknown_0x53e746a0', UnknownStruct66.from_stream),
    0xc6979235: ('unknown_0xc6979235', UnknownStruct66.from_stream),
    0xea870072: ('unknown_0xea870072', UnknownStruct66.from_stream),
    0x7ff7d4e7: ('unknown_0x7ff7d4e7', UnknownStruct66.from_stream),
    0x7db5008c: ('unknown_0x7db5008c', UnknownStruct66.from_stream),
}
