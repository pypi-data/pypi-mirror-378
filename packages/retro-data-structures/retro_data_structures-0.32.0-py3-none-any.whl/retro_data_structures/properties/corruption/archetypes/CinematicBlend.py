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
from retro_data_structures.properties.corruption.archetypes.FOVInterpolationMethod import FOVInterpolationMethod
from retro_data_structures.properties.corruption.archetypes.MotionInterpolationMethod import MotionInterpolationMethod
from retro_data_structures.properties.corruption.archetypes.OrientationInterpolationMethod import OrientationInterpolationMethod

if typing.TYPE_CHECKING:
    class CinematicBlendJson(typing_extensions.TypedDict):
        motion_blend: json_util.JsonObject
        orientation_blend: json_util.JsonObject
        fov_blend: json_util.JsonObject
    

@dataclasses.dataclass()
class CinematicBlend(BaseProperty):
    motion_blend: MotionInterpolationMethod = dataclasses.field(default_factory=MotionInterpolationMethod, metadata={
        'reflection': FieldReflection[MotionInterpolationMethod](
            MotionInterpolationMethod, id=0xb5c367e9, original_name='MotionBlend', from_json=MotionInterpolationMethod.from_json, to_json=MotionInterpolationMethod.to_json
        ),
    })
    orientation_blend: OrientationInterpolationMethod = dataclasses.field(default_factory=OrientationInterpolationMethod, metadata={
        'reflection': FieldReflection[OrientationInterpolationMethod](
            OrientationInterpolationMethod, id=0xf74f8c89, original_name='OrientationBlend', from_json=OrientationInterpolationMethod.from_json, to_json=OrientationInterpolationMethod.to_json
        ),
    })
    fov_blend: FOVInterpolationMethod = dataclasses.field(default_factory=FOVInterpolationMethod, metadata={
        'reflection': FieldReflection[FOVInterpolationMethod](
            FOVInterpolationMethod, id=0x18e6bed2, original_name='FOVBlend', from_json=FOVInterpolationMethod.from_json, to_json=FOVInterpolationMethod.to_json
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
        if property_count != 3:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb5c367e9
        motion_blend = MotionInterpolationMethod.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf74f8c89
        orientation_blend = OrientationInterpolationMethod.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x18e6bed2
        fov_blend = FOVInterpolationMethod.from_stream(data, property_size)
    
        return cls(motion_blend, orientation_blend, fov_blend)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x03')  # 3 properties

        data.write(b'\xb5\xc3g\xe9')  # 0xb5c367e9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion_blend.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf7O\x8c\x89')  # 0xf74f8c89
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.orientation_blend.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x18\xe6\xbe\xd2')  # 0x18e6bed2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.fov_blend.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CinematicBlendJson", data)
        return cls(
            motion_blend=MotionInterpolationMethod.from_json(json_data['motion_blend']),
            orientation_blend=OrientationInterpolationMethod.from_json(json_data['orientation_blend']),
            fov_blend=FOVInterpolationMethod.from_json(json_data['fov_blend']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'motion_blend': self.motion_blend.to_json(),
            'orientation_blend': self.orientation_blend.to_json(),
            'fov_blend': self.fov_blend.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xb5c367e9: ('motion_blend', MotionInterpolationMethod.from_stream),
    0xf74f8c89: ('orientation_blend', OrientationInterpolationMethod.from_stream),
    0x18e6bed2: ('fov_blend', FOVInterpolationMethod.from_stream),
}
