# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.RevolutionControl import RevolutionControl
from retro_data_structures.properties.corruption.core.Spline import Spline

if typing.TYPE_CHECKING:
    class BallMiscControlsJson(typing_extensions.TypedDict):
        bomb: json_util.JsonObject
        hyper_ball: json_util.JsonObject
        morph_into_ball: json_util.JsonObject
        morph_out_of_ball: json_util.JsonObject
        horiz_aim_control: json_util.JsonObject
        vert_aim_control: json_util.JsonObject
    

@dataclasses.dataclass()
class BallMiscControls(BaseProperty):
    bomb: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xd239fb95, original_name='Bomb', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    hyper_ball: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x5e96f52f, original_name='HyperBall', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    morph_into_ball: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0x5880ba62, original_name='MorphIntoBall', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    morph_out_of_ball: RevolutionControl = dataclasses.field(default_factory=RevolutionControl, metadata={
        'reflection': FieldReflection[RevolutionControl](
            RevolutionControl, id=0xa14f91f1, original_name='MorphOutOfBall', from_json=RevolutionControl.from_json, to_json=RevolutionControl.to_json
        ),
    })
    horiz_aim_control: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x4e194f55, original_name='HorizAimControl', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })
    vert_aim_control: Spline = dataclasses.field(default_factory=Spline, metadata={
        'reflection': FieldReflection[Spline](
            Spline, id=0x187124af, original_name='VertAimControl', from_json=Spline.from_json, to_json=Spline.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
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

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 6:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd239fb95
        bomb = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e96f52f
        hyper_ball = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5880ba62
        morph_into_ball = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa14f91f1
        morph_out_of_ball = RevolutionControl.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4e194f55
        horiz_aim_control = Spline.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x187124af
        vert_aim_control = Spline.from_stream(data, property_size)
    
        return cls(bomb, hyper_ball, morph_into_ball, morph_out_of_ball, horiz_aim_control, vert_aim_control)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'\xd29\xfb\x95')  # 0xd239fb95
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bomb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'^\x96\xf5/')  # 0x5e96f52f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_ball.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'X\x80\xbab')  # 0x5880ba62
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.morph_into_ball.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa1O\x91\xf1')  # 0xa14f91f1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.morph_out_of_ball.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'N\x19OU')  # 0x4e194f55
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.horiz_aim_control.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x18q$\xaf')  # 0x187124af
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vert_aim_control.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("BallMiscControlsJson", data)
        return cls(
            bomb=RevolutionControl.from_json(json_data['bomb']),
            hyper_ball=RevolutionControl.from_json(json_data['hyper_ball']),
            morph_into_ball=RevolutionControl.from_json(json_data['morph_into_ball']),
            morph_out_of_ball=RevolutionControl.from_json(json_data['morph_out_of_ball']),
            horiz_aim_control=Spline.from_json(json_data['horiz_aim_control']),
            vert_aim_control=Spline.from_json(json_data['vert_aim_control']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'bomb': self.bomb.to_json(),
            'hyper_ball': self.hyper_ball.to_json(),
            'morph_into_ball': self.morph_into_ball.to_json(),
            'morph_out_of_ball': self.morph_out_of_ball.to_json(),
            'horiz_aim_control': self.horiz_aim_control.to_json(),
            'vert_aim_control': self.vert_aim_control.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xd239fb95: ('bomb', RevolutionControl.from_stream),
    0x5e96f52f: ('hyper_ball', RevolutionControl.from_stream),
    0x5880ba62: ('morph_into_ball', RevolutionControl.from_stream),
    0xa14f91f1: ('morph_out_of_ball', RevolutionControl.from_stream),
    0x4e194f55: ('horiz_aim_control', Spline.from_stream),
    0x187124af: ('vert_aim_control', Spline.from_stream),
}
