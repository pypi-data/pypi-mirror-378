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
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakSlideShowJson(typing_extensions.TypedDict):
        instance_name: str
        pak_file: str
        font: str
        font_color: json_util.JsonValue
        font_outline_color: json_util.JsonValue
        unknown_0xd398dac2: float
        unknown_0x03757d08: float
        translation_multiplier: float
        scale_multiplier: float
        slide_show_delay: float
        help_frame_color: json_util.JsonValue
        help_transition_time: float
        slide_blend_time: float
        unknown_0x029d2082: float
        unknown_0xb187cd9b: float
        fade_in_time: float
        fade_out_time: float
        unknown_0xc0544bc1: str
    

@dataclasses.dataclass()
class TweakSlideShow(BaseObjectType):
    instance_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x7fda1466, original_name='InstanceName'
        ),
    })
    pak_file: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x2bd13ab3, original_name='PakFile'
        ),
    })
    font: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xfe31fba0, original_name='Font'
        ),
    })
    font_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1a96ec67, original_name='FontColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    font_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x844ab6b0, original_name='FontOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xd398dac2: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd398dac2, original_name='Unknown'
        ),
    })
    unknown_0x03757d08: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x03757d08, original_name='Unknown'
        ),
    })
    translation_multiplier: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x59276e14, original_name='TranslationMultiplier'
        ),
    })
    scale_multiplier: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3ce7a013, original_name='ScaleMultiplier'
        ),
    })
    slide_show_delay: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x278c0893, original_name='SlideShowDelay'
        ),
    })
    help_frame_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd75d29f8, original_name='HelpFrameColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    help_transition_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x27515c7b, original_name='HelpTransitionTime'
        ),
    })
    slide_blend_time: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xae47dc81, original_name='SlideBlendTime'
        ),
    })
    unknown_0x029d2082: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x029d2082, original_name='Unknown'
        ),
    })
    unknown_0xb187cd9b: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb187cd9b, original_name='Unknown'
        ),
    })
    fade_in_time: float = dataclasses.field(default=0.0010000000474974513, metadata={
        'reflection': FieldReflection[float](
            float, id=0x90aa341f, original_name='FadeInTime'
        ),
    })
    fade_out_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7c269ebc, original_name='FadeOutTime'
        ),
    })
    unknown_0xc0544bc1: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xc0544bc1, original_name='Unknown'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return None

    def set_name(self, name: str) -> None:
        raise RuntimeError(f"{self.__class__.__name__} does not have name")

    @classmethod
    def object_type(cls) -> str:
        return 'TWSS'

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
        if property_count != 18:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fda1466
        instance_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2bd13ab3
        pak_file = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe31fba0
        font = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1a96ec67
        font_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x844ab6b0
        font_outline_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd398dac2
        unknown_0xd398dac2 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x03757d08
        unknown_0x03757d08 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x59276e14
        translation_multiplier = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3ce7a013
        scale_multiplier = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x278c0893
        slide_show_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd75d29f8
        help_frame_color = Color.from_stream(data)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x27515c7b
        help_transition_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xae47dc81
        slide_blend_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x029d2082
        unknown_0x029d2082 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb187cd9b
        unknown_0xb187cd9b = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x90aa341f
        fade_in_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7c269ebc
        fade_out_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc0544bc1
        unknown_0xc0544bc1 = data.read(property_size)[:-1].decode("utf-8")
    
        return cls(instance_name, pak_file, font, font_color, font_outline_color, unknown_0xd398dac2, unknown_0x03757d08, translation_multiplier, scale_multiplier, slide_show_delay, help_frame_color, help_transition_time, slide_blend_time, unknown_0x029d2082, unknown_0xb187cd9b, fade_in_time, fade_out_time, unknown_0xc0544bc1)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x12')  # 18 properties

        data.write(b'\x7f\xda\x14f')  # 0x7fda1466
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.instance_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'+\xd1:\xb3')  # 0x2bd13ab3
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.pak_file.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xfe1\xfb\xa0')  # 0xfe31fba0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.font.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x1a\x96\xecg')  # 0x1a96ec67
        data.write(b'\x00\x10')  # size
        self.font_color.to_stream(data)

        data.write(b'\x84J\xb6\xb0')  # 0x844ab6b0
        data.write(b'\x00\x10')  # size
        self.font_outline_color.to_stream(data)

        data.write(b'\xd3\x98\xda\xc2')  # 0xd398dac2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xd398dac2))

        data.write(b'\x03u}\x08')  # 0x3757d08
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x03757d08))

        data.write(b"Y'n\x14")  # 0x59276e14
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.translation_multiplier))

        data.write(b'<\xe7\xa0\x13')  # 0x3ce7a013
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.scale_multiplier))

        data.write(b"'\x8c\x08\x93")  # 0x278c0893
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.slide_show_delay))

        data.write(b'\xd7])\xf8')  # 0xd75d29f8
        data.write(b'\x00\x10')  # size
        self.help_frame_color.to_stream(data)

        data.write(b"'Q\\{")  # 0x27515c7b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.help_transition_time))

        data.write(b'\xaeG\xdc\x81')  # 0xae47dc81
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.slide_blend_time))

        data.write(b'\x02\x9d \x82')  # 0x29d2082
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x029d2082))

        data.write(b'\xb1\x87\xcd\x9b')  # 0xb187cd9b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb187cd9b))

        data.write(b'\x90\xaa4\x1f')  # 0x90aa341f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_in_time))

        data.write(b'|&\x9e\xbc')  # 0x7c269ebc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fade_out_time))

        data.write(b'\xc0TK\xc1')  # 0xc0544bc1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.unknown_0xc0544bc1.encode("utf-8"))
        data.write(b'\x00')
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
        json_data = typing.cast("TweakSlideShowJson", data)
        return cls(
            instance_name=json_data['instance_name'],
            pak_file=json_data['pak_file'],
            font=json_data['font'],
            font_color=Color.from_json(json_data['font_color']),
            font_outline_color=Color.from_json(json_data['font_outline_color']),
            unknown_0xd398dac2=json_data['unknown_0xd398dac2'],
            unknown_0x03757d08=json_data['unknown_0x03757d08'],
            translation_multiplier=json_data['translation_multiplier'],
            scale_multiplier=json_data['scale_multiplier'],
            slide_show_delay=json_data['slide_show_delay'],
            help_frame_color=Color.from_json(json_data['help_frame_color']),
            help_transition_time=json_data['help_transition_time'],
            slide_blend_time=json_data['slide_blend_time'],
            unknown_0x029d2082=json_data['unknown_0x029d2082'],
            unknown_0xb187cd9b=json_data['unknown_0xb187cd9b'],
            fade_in_time=json_data['fade_in_time'],
            fade_out_time=json_data['fade_out_time'],
            unknown_0xc0544bc1=json_data['unknown_0xc0544bc1'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'instance_name': self.instance_name,
            'pak_file': self.pak_file,
            'font': self.font,
            'font_color': self.font_color.to_json(),
            'font_outline_color': self.font_outline_color.to_json(),
            'unknown_0xd398dac2': self.unknown_0xd398dac2,
            'unknown_0x03757d08': self.unknown_0x03757d08,
            'translation_multiplier': self.translation_multiplier,
            'scale_multiplier': self.scale_multiplier,
            'slide_show_delay': self.slide_show_delay,
            'help_frame_color': self.help_frame_color.to_json(),
            'help_transition_time': self.help_transition_time,
            'slide_blend_time': self.slide_blend_time,
            'unknown_0x029d2082': self.unknown_0x029d2082,
            'unknown_0xb187cd9b': self.unknown_0xb187cd9b,
            'fade_in_time': self.fade_in_time,
            'fade_out_time': self.fade_out_time,
            'unknown_0xc0544bc1': self.unknown_0xc0544bc1,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_instance_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_pak_file(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_font(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_font_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_font_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xd398dac2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x03757d08(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_translation_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_scale_multiplier(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_slide_show_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_help_frame_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_help_transition_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_slide_blend_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x029d2082(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb187cd9b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_in_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fade_out_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xc0544bc1(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7fda1466: ('instance_name', _decode_instance_name),
    0x2bd13ab3: ('pak_file', _decode_pak_file),
    0xfe31fba0: ('font', _decode_font),
    0x1a96ec67: ('font_color', _decode_font_color),
    0x844ab6b0: ('font_outline_color', _decode_font_outline_color),
    0xd398dac2: ('unknown_0xd398dac2', _decode_unknown_0xd398dac2),
    0x3757d08: ('unknown_0x03757d08', _decode_unknown_0x03757d08),
    0x59276e14: ('translation_multiplier', _decode_translation_multiplier),
    0x3ce7a013: ('scale_multiplier', _decode_scale_multiplier),
    0x278c0893: ('slide_show_delay', _decode_slide_show_delay),
    0xd75d29f8: ('help_frame_color', _decode_help_frame_color),
    0x27515c7b: ('help_transition_time', _decode_help_transition_time),
    0xae47dc81: ('slide_blend_time', _decode_slide_blend_time),
    0x29d2082: ('unknown_0x029d2082', _decode_unknown_0x029d2082),
    0xb187cd9b: ('unknown_0xb187cd9b', _decode_unknown_0xb187cd9b),
    0x90aa341f: ('fade_in_time', _decode_fade_in_time),
    0x7c269ebc: ('fade_out_time', _decode_fade_out_time),
    0xc0544bc1: ('unknown_0xc0544bc1', _decode_unknown_0xc0544bc1),
}
