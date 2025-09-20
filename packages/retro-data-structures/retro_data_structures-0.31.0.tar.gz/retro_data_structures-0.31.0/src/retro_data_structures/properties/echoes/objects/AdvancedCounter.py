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
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class AdvancedCounterJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        initial_count: int
        max_count: int
        auto_reset: bool
        counter_condition1: int
        counter_condition2: int
        counter_condition3: int
        counter_condition4: int
        counter_condition5: int
        counter_condition6: int
        counter_condition7: int
        counter_condition8: int
        counter_condition9: int
        counter_condition10: int
    

@dataclasses.dataclass()
class AdvancedCounter(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    initial_count: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xfd179a6f, original_name='Initial_Count'
        ),
    })
    max_count: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x5b851589, original_name='Max_Count'
        ),
    })
    auto_reset: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7bef45ca, original_name='AutoReset'
        ),
    })
    counter_condition1: int = dataclasses.field(default=1, metadata={
        'reflection': FieldReflection[int](
            int, id=0x1628f23a, original_name='CounterCondition1'
        ),
    })
    counter_condition2: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x049d5dd4, original_name='CounterCondition2'
        ),
    })
    counter_condition3: int = dataclasses.field(default=3, metadata={
        'reflection': FieldReflection[int](
            int, id=0xbc213ab1, original_name='CounterCondition3'
        ),
    })
    counter_condition4: int = dataclasses.field(default=4, metadata={
        'reflection': FieldReflection[int](
            int, id=0x21f60208, original_name='CounterCondition4'
        ),
    })
    counter_condition5: int = dataclasses.field(default=5, metadata={
        'reflection': FieldReflection[int](
            int, id=0x994a656d, original_name='CounterCondition5'
        ),
    })
    counter_condition6: int = dataclasses.field(default=6, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8bffca83, original_name='CounterCondition6'
        ),
    })
    counter_condition7: int = dataclasses.field(default=7, metadata={
        'reflection': FieldReflection[int](
            int, id=0x3343ade6, original_name='CounterCondition7'
        ),
    })
    counter_condition8: int = dataclasses.field(default=8, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6b20bdb0, original_name='CounterCondition8'
        ),
    })
    counter_condition9: int = dataclasses.field(default=9, metadata={
        'reflection': FieldReflection[int](
            int, id=0xd39cdad5, original_name='CounterCondition9'
        ),
    })
    counter_condition10: int = dataclasses.field(default=10, metadata={
        'reflection': FieldReflection[int](
            int, id=0x9215e813, original_name='CounterCondition10'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'ACNT'

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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd179a6f
        initial_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5b851589
        max_count = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7bef45ca
        auto_reset = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1628f23a
        counter_condition1 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x049d5dd4
        counter_condition2 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc213ab1
        counter_condition3 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x21f60208
        counter_condition4 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x994a656d
        counter_condition5 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8bffca83
        counter_condition6 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3343ade6
        counter_condition7 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6b20bdb0
        counter_condition8 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd39cdad5
        counter_condition9 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9215e813
        counter_condition10 = struct.unpack('>l', data.read(4))[0]
    
        return cls(editor_properties, initial_count, max_count, auto_reset, counter_condition1, counter_condition2, counter_condition3, counter_condition4, counter_condition5, counter_condition6, counter_condition7, counter_condition8, counter_condition9, counter_condition10)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfd\x17\x9ao')  # 0xfd179a6f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.initial_count))

        data.write(b'[\x85\x15\x89')  # 0x5b851589
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_count))

        data.write(b'{\xefE\xca')  # 0x7bef45ca
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.auto_reset))

        data.write(b'\x16(\xf2:')  # 0x1628f23a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition1))

        data.write(b'\x04\x9d]\xd4')  # 0x49d5dd4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition2))

        data.write(b'\xbc!:\xb1')  # 0xbc213ab1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition3))

        data.write(b'!\xf6\x02\x08')  # 0x21f60208
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition4))

        data.write(b'\x99Jem')  # 0x994a656d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition5))

        data.write(b'\x8b\xff\xca\x83')  # 0x8bffca83
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition6))

        data.write(b'3C\xad\xe6')  # 0x3343ade6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition7))

        data.write(b'k \xbd\xb0')  # 0x6b20bdb0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition8))

        data.write(b'\xd3\x9c\xda\xd5')  # 0xd39cdad5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition9))

        data.write(b'\x92\x15\xe8\x13')  # 0x9215e813
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.counter_condition10))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AdvancedCounterJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            initial_count=json_data['initial_count'],
            max_count=json_data['max_count'],
            auto_reset=json_data['auto_reset'],
            counter_condition1=json_data['counter_condition1'],
            counter_condition2=json_data['counter_condition2'],
            counter_condition3=json_data['counter_condition3'],
            counter_condition4=json_data['counter_condition4'],
            counter_condition5=json_data['counter_condition5'],
            counter_condition6=json_data['counter_condition6'],
            counter_condition7=json_data['counter_condition7'],
            counter_condition8=json_data['counter_condition8'],
            counter_condition9=json_data['counter_condition9'],
            counter_condition10=json_data['counter_condition10'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'initial_count': self.initial_count,
            'max_count': self.max_count,
            'auto_reset': self.auto_reset,
            'counter_condition1': self.counter_condition1,
            'counter_condition2': self.counter_condition2,
            'counter_condition3': self.counter_condition3,
            'counter_condition4': self.counter_condition4,
            'counter_condition5': self.counter_condition5,
            'counter_condition6': self.counter_condition6,
            'counter_condition7': self.counter_condition7,
            'counter_condition8': self.counter_condition8,
            'counter_condition9': self.counter_condition9,
            'counter_condition10': self.counter_condition10,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for AdvancedCounter.{field_name} ({field_type}): {e}"
                )


def _decode_initial_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_count(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_auto_reset(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_counter_condition1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition3(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition4(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition5(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition6(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition7(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition8(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition9(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_counter_condition10(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xfd179a6f: ('initial_count', _decode_initial_count),
    0x5b851589: ('max_count', _decode_max_count),
    0x7bef45ca: ('auto_reset', _decode_auto_reset),
    0x1628f23a: ('counter_condition1', _decode_counter_condition1),
    0x49d5dd4: ('counter_condition2', _decode_counter_condition2),
    0xbc213ab1: ('counter_condition3', _decode_counter_condition3),
    0x21f60208: ('counter_condition4', _decode_counter_condition4),
    0x994a656d: ('counter_condition5', _decode_counter_condition5),
    0x8bffca83: ('counter_condition6', _decode_counter_condition6),
    0x3343ade6: ('counter_condition7', _decode_counter_condition7),
    0x6b20bdb0: ('counter_condition8', _decode_counter_condition8),
    0xd39cdad5: ('counter_condition9', _decode_counter_condition9),
    0x9215e813: ('counter_condition10', _decode_counter_condition10),
}
