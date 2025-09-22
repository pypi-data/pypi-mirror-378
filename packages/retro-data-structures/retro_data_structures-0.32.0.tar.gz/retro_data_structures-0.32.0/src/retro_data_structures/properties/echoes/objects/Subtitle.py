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
from retro_data_structures.properties.echoes.archetypes.TextProperties import TextProperties
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SubtitleJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        text_properties: json_util.JsonObject
        text_position_x: int
        text_position_y: int
        japan_text_properties: json_util.JsonObject
        japan_text_position_x: int
        japan_text_position_y: int
        string_table: int
        initial_string_index: int
        fade_in_time: float
        fade_out_time: float
    

@dataclasses.dataclass()
class Subtitle(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    text_properties: TextProperties = dataclasses.field(default_factory=TextProperties, metadata={
        'reflection': FieldReflection[TextProperties](
            TextProperties, id=0xe0543e66, original_name='TextProperties', from_json=TextProperties.from_json, to_json=TextProperties.to_json
        ),
    })
    text_position_x: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc33a87c7, original_name='TextPositionX'
        ),
    })
    text_position_y: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7b86e0a2, original_name='TextPositionY'
        ),
    })
    japan_text_properties: TextProperties = dataclasses.field(default_factory=TextProperties, metadata={
        'reflection': FieldReflection[TextProperties](
            TextProperties, id=0xc8e441fa, original_name='JapanTextProperties', from_json=TextProperties.from_json, to_json=TextProperties.to_json
        ),
    })
    japan_text_position_x: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x53a7f7a7, original_name='JapanTextPositionX'
        ),
    })
    japan_text_position_y: int = dataclasses.field(default=100, metadata={
        'reflection': FieldReflection[int](
            int, id=0xeb1b90c2, original_name='JapanTextPositionY'
        ),
    })
    string_table: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['STRG'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xfd95ed2a, original_name='StringTable'
        ),
    })
    initial_string_index: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6ce46689, original_name='InitialStringIndex'
        ),
    })
    fade_in_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x90aa341f, original_name='FadeInTime'
        ),
    })
    fade_out_time: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c269ebc, original_name='FadeOutTime'
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
        return 'SUBT'

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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe0543e66
        text_properties = TextProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc33a87c7
        text_position_x = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b86e0a2
        text_position_y = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8e441fa
        japan_text_properties = TextProperties.from_stream(data, property_size, default_override={'text_bounding_width': 640, 'text_bounding_height': 448})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x53a7f7a7
        japan_text_position_x = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeb1b90c2
        japan_text_position_y = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfd95ed2a
        string_table = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6ce46689
        initial_string_index = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90aa341f
        fade_in_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c269ebc
        fade_out_time = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, text_properties, text_position_x, text_position_y, japan_text_properties, japan_text_position_x, japan_text_position_y, string_table, initial_string_index, fade_in_time, fade_out_time)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x08')  # 8 properties
        num_properties_written = 8

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe0T>f')  # 0xe0543e66
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.text_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc3:\x87\xc7')  # 0xc33a87c7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.text_position_x))

        data.write(b'{\x86\xe0\xa2')  # 0x7b86e0a2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.text_position_y))

        if self.japan_text_properties != default_override.get('japan_text_properties', TextProperties()):
            num_properties_written += 1
            data.write(b'\xc8\xe4A\xfa')  # 0xc8e441fa
            before = data.tell()
            data.write(b'\x00\x00')  # size placeholder
            self.japan_text_properties.to_stream(data, default_override={'text_bounding_width': 640, 'text_bounding_height': 448})
            after = data.tell()
            data.seek(before)
            data.write(struct.pack(">H", after - before - 2))
            data.seek(after)

        if self.japan_text_position_x != default_override.get('japan_text_position_x', 0):
            num_properties_written += 1
            data.write(b'S\xa7\xf7\xa7')  # 0x53a7f7a7
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>l', self.japan_text_position_x))

        if self.japan_text_position_y != default_override.get('japan_text_position_y', 100):
            num_properties_written += 1
            data.write(b'\xeb\x1b\x90\xc2')  # 0xeb1b90c2
            data.write(b'\x00\x04')  # size
            data.write(struct.pack('>l', self.japan_text_position_y))

        data.write(b'\xfd\x95\xed*')  # 0xfd95ed2a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.string_table))

        data.write(b'l\xe4f\x89')  # 0x6ce46689
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.initial_string_index))

        data.write(b'\x90\xaa4\x1f')  # 0x90aa341f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_in_time))

        data.write(b'|&\x9e\xbc')  # 0x7c269ebc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_time))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.write(struct.pack(">H", num_properties_written))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SubtitleJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            text_properties=TextProperties.from_json(json_data['text_properties']),
            text_position_x=json_data['text_position_x'],
            text_position_y=json_data['text_position_y'],
            japan_text_properties=TextProperties.from_json(json_data['japan_text_properties']),
            japan_text_position_x=json_data['japan_text_position_x'],
            japan_text_position_y=json_data['japan_text_position_y'],
            string_table=json_data['string_table'],
            initial_string_index=json_data['initial_string_index'],
            fade_in_time=json_data['fade_in_time'],
            fade_out_time=json_data['fade_out_time'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'text_properties': self.text_properties.to_json(),
            'text_position_x': self.text_position_x,
            'text_position_y': self.text_position_y,
            'japan_text_properties': self.japan_text_properties.to_json(),
            'japan_text_position_x': self.japan_text_position_x,
            'japan_text_position_y': self.japan_text_position_y,
            'string_table': self.string_table,
            'initial_string_index': self.initial_string_index,
            'fade_in_time': self.fade_in_time,
            'fade_out_time': self.fade_out_time,
        }

    def _dependencies_for_string_table(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.string_table)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.text_properties.dependencies_for, "text_properties", "TextProperties"),
            (self.japan_text_properties.dependencies_for, "japan_text_properties", "TextProperties"),
            (self._dependencies_for_string_table, "string_table", "AssetId"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Subtitle.{field_name} ({field_type}): {e}"
                )


def _decode_text_position_x(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_text_position_y(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_japan_text_properties(data: typing.BinaryIO, property_size: int) -> TextProperties:
    return TextProperties.from_stream(data, property_size, default_override={'text_bounding_width': 640, 'text_bounding_height': 448})


def _decode_japan_text_position_x(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_japan_text_position_y(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_string_table(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_initial_string_index(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_fade_in_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xe0543e66: ('text_properties', TextProperties.from_stream),
    0xc33a87c7: ('text_position_x', _decode_text_position_x),
    0x7b86e0a2: ('text_position_y', _decode_text_position_y),
    0xc8e441fa: ('japan_text_properties', _decode_japan_text_properties),
    0x53a7f7a7: ('japan_text_position_x', _decode_japan_text_position_x),
    0xeb1b90c2: ('japan_text_position_y', _decode_japan_text_position_y),
    0xfd95ed2a: ('string_table', _decode_string_table),
    0x6ce46689: ('initial_string_index', _decode_initial_string_index),
    0x90aa341f: ('fade_in_time', _decode_fade_in_time),
    0x7c269ebc: ('fade_out_time', _decode_fade_out_time),
}
