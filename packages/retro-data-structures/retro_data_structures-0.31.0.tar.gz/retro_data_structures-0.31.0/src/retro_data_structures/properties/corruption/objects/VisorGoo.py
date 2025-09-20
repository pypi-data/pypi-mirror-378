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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class VisorGooJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        particle: int
        electric: int
        min_range: float
        max_range: float
        unknown_0x4538fdc7: float
        unknown_0x057785b1: float
        color: json_util.JsonValue
        sound_hit_sound: int
        no_view_check: bool
        persistent: bool
        unknown_0xcb9a3009: bool
    

@dataclasses.dataclass()
class VisorGoo(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    particle: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6d1ce525, original_name='Particle'
        ),
    })
    electric: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x71dbe2f2, original_name='Electric'
        ),
    })
    min_range: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9744971e, original_name='MinRange'
        ),
    })
    max_range: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd70bef68, original_name='MaxRange'
        ),
    })
    unknown_0x4538fdc7: float = dataclasses.field(default=40.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4538fdc7, original_name='Unknown'
        ),
    })
    unknown_0x057785b1: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x057785b1, original_name='Unknown'
        ),
    })
    color: Color = dataclasses.field(default_factory=lambda: Color(r=1.0, g=1.0, b=1.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x37c7d09d, original_name='Color', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    sound_hit_sound: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CAUD'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x5cfd034a, original_name='Sound_HitSound'
        ),
    })
    no_view_check: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xd5b78bc9, original_name='NoViewCheck'
        ),
    })
    persistent: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xea03e258, original_name='Persistent'
        ),
    })
    unknown_0xcb9a3009: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcb9a3009, original_name='Unknown'
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
        return 'VGOO'

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
        assert property_id == 0x6d1ce525
        particle = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x71dbe2f2
        electric = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9744971e
        min_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd70bef68
        max_range = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4538fdc7
        unknown_0x4538fdc7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x057785b1
        unknown_0x057785b1 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37c7d09d
        color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5cfd034a
        sound_hit_sound = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd5b78bc9
        no_view_check = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xea03e258
        persistent = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb9a3009
        unknown_0xcb9a3009 = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, particle, electric, min_range, max_range, unknown_0x4538fdc7, unknown_0x057785b1, color, sound_hit_sound, no_view_check, persistent, unknown_0xcb9a3009)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'm\x1c\xe5%')  # 0x6d1ce525
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.particle))

        data.write(b'q\xdb\xe2\xf2')  # 0x71dbe2f2
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.electric))

        data.write(b'\x97D\x97\x1e')  # 0x9744971e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_range))

        data.write(b'\xd7\x0b\xefh')  # 0xd70bef68
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_range))

        data.write(b'E8\xfd\xc7')  # 0x4538fdc7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x4538fdc7))

        data.write(b'\x05w\x85\xb1')  # 0x57785b1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x057785b1))

        data.write(b'7\xc7\xd0\x9d')  # 0x37c7d09d
        data.write(b'\x00\x10')  # size
        self.color.to_stream(data)

        data.write(b'\\\xfd\x03J')  # 0x5cfd034a
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.sound_hit_sound))

        data.write(b'\xd5\xb7\x8b\xc9')  # 0xd5b78bc9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.no_view_check))

        data.write(b'\xea\x03\xe2X')  # 0xea03e258
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.persistent))

        data.write(b'\xcb\x9a0\t')  # 0xcb9a3009
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xcb9a3009))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("VisorGooJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            particle=json_data['particle'],
            electric=json_data['electric'],
            min_range=json_data['min_range'],
            max_range=json_data['max_range'],
            unknown_0x4538fdc7=json_data['unknown_0x4538fdc7'],
            unknown_0x057785b1=json_data['unknown_0x057785b1'],
            color=Color.from_json(json_data['color']),
            sound_hit_sound=json_data['sound_hit_sound'],
            no_view_check=json_data['no_view_check'],
            persistent=json_data['persistent'],
            unknown_0xcb9a3009=json_data['unknown_0xcb9a3009'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'particle': self.particle,
            'electric': self.electric,
            'min_range': self.min_range,
            'max_range': self.max_range,
            'unknown_0x4538fdc7': self.unknown_0x4538fdc7,
            'unknown_0x057785b1': self.unknown_0x057785b1,
            'color': self.color.to_json(),
            'sound_hit_sound': self.sound_hit_sound,
            'no_view_check': self.no_view_check,
            'persistent': self.persistent,
            'unknown_0xcb9a3009': self.unknown_0xcb9a3009,
        }


def _decode_particle(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_electric(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_min_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_range(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x4538fdc7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x057785b1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_sound_hit_sound(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_no_view_check(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_persistent(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xcb9a3009(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x6d1ce525: ('particle', _decode_particle),
    0x71dbe2f2: ('electric', _decode_electric),
    0x9744971e: ('min_range', _decode_min_range),
    0xd70bef68: ('max_range', _decode_max_range),
    0x4538fdc7: ('unknown_0x4538fdc7', _decode_unknown_0x4538fdc7),
    0x57785b1: ('unknown_0x057785b1', _decode_unknown_0x057785b1),
    0x37c7d09d: ('color', _decode_color),
    0x5cfd034a: ('sound_hit_sound', _decode_sound_hit_sound),
    0xd5b78bc9: ('no_view_check', _decode_no_view_check),
    0xea03e258: ('persistent', _decode_persistent),
    0xcb9a3009: ('unknown_0xcb9a3009', _decode_unknown_0xcb9a3009),
}
