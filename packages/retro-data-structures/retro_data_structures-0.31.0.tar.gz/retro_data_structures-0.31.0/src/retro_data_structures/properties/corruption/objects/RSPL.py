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
    class RSPLJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        splash_scale: float
        max_splashes: int
        generation_rate: int
        start_height: float
        alpha_factor: float
    

@dataclasses.dataclass()
class RSPL(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    splash_scale: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x08231ac9, original_name='SplashScale'
        ),
    })
    max_splashes: int = dataclasses.field(default=20, metadata={
        'reflection': FieldReflection[int](
            int, id=0x6248aa06, original_name='MaxSplashes'
        ),
    })
    generation_rate: int = dataclasses.field(default=2, metadata={
        'reflection': FieldReflection[int](
            int, id=0x7f5a86dd, original_name='GenerationRate'
        ),
    })
    start_height: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xc40527f6, original_name='StartHeight'
        ),
    })
    alpha_factor: float = dataclasses.field(default=0.125, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe04e0270, original_name='AlphaFactor'
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
        return 'RSPL'

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
        assert property_id == 0x08231ac9
        splash_scale = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6248aa06
        max_splashes = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7f5a86dd
        generation_rate = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc40527f6
        start_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe04e0270
        alpha_factor = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, splash_scale, max_splashes, generation_rate, start_height, alpha_factor)

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

        data.write(b'\x08#\x1a\xc9')  # 0x8231ac9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.splash_scale))

        data.write(b'bH\xaa\x06')  # 0x6248aa06
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_splashes))

        data.write(b'\x7fZ\x86\xdd')  # 0x7f5a86dd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.generation_rate))

        data.write(b"\xc4\x05'\xf6")  # 0xc40527f6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.start_height))

        data.write(b'\xe0N\x02p')  # 0xe04e0270
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.alpha_factor))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RSPLJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            splash_scale=json_data['splash_scale'],
            max_splashes=json_data['max_splashes'],
            generation_rate=json_data['generation_rate'],
            start_height=json_data['start_height'],
            alpha_factor=json_data['alpha_factor'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'splash_scale': self.splash_scale,
            'max_splashes': self.max_splashes,
            'generation_rate': self.generation_rate,
            'start_height': self.start_height,
            'alpha_factor': self.alpha_factor,
        }


def _decode_splash_scale(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_splashes(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_generation_rate(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_start_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_alpha_factor(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x8231ac9: ('splash_scale', _decode_splash_scale),
    0x6248aa06: ('max_splashes', _decode_max_splashes),
    0x7f5a86dd: ('generation_rate', _decode_generation_rate),
    0xc40527f6: ('start_height', _decode_start_height),
    0xe04e0270: ('alpha_factor', _decode_alpha_factor),
}
