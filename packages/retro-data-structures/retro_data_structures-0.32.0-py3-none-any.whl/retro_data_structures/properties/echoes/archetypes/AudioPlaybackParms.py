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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class AudioPlaybackParmsJson(typing_extensions.TypedDict):
        maximum_distance: float
        fall_off: float
        sound_id: int
        max_volume: int
        min_volume: int
        use_room_acoustics: bool
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xe449f72, 0x72531867, 0xaf85a374, 0xc712847c, 0x57619496, 0x85707354)


@dataclasses.dataclass()
class AudioPlaybackParms(BaseProperty):
    maximum_distance: float = dataclasses.field(default=100.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0e449f72, original_name='MaximumDistance'
        ),
    })
    fall_off: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0x72531867, original_name='FallOff'
        ),
    })
    sound_id: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0xaf85a374, original_name='Sound_Id'
        ),
    })
    max_volume: int = dataclasses.field(default=127, metadata={
        'reflection': FieldReflection[int](
            int, id=0xc712847c, original_name='MaxVolume'
        ),
    })
    min_volume: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x57619496, original_name='MinVolume'
        ),
    })
    use_room_acoustics: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x85707354, original_name='UseRoomAcoustics'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHfLHfLHlLHlLHlLH?')
    
        dec = _FAST_FORMAT.unpack(data.read(57))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x06')  # 6 properties

        data.write(b'\x0eD\x9fr')  # 0xe449f72
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.maximum_distance))

        data.write(b'rS\x18g')  # 0x72531867
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.fall_off))

        data.write(b'\xaf\x85\xa3t')  # 0xaf85a374
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_id))

        data.write(b'\xc7\x12\x84|')  # 0xc712847c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.max_volume))

        data.write(b'Wa\x94\x96')  # 0x57619496
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.min_volume))

        data.write(b'\x85psT')  # 0x85707354
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.use_room_acoustics))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AudioPlaybackParmsJson", data)
        return cls(
            maximum_distance=json_data['maximum_distance'],
            fall_off=json_data['fall_off'],
            sound_id=json_data['sound_id'],
            max_volume=json_data['max_volume'],
            min_volume=json_data['min_volume'],
            use_room_acoustics=json_data['use_room_acoustics'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'maximum_distance': self.maximum_distance,
            'fall_off': self.fall_off,
            'sound_id': self.sound_id,
            'max_volume': self.max_volume,
            'min_volume': self.min_volume,
            'use_room_acoustics': self.use_room_acoustics,
        }

    def _dependencies_for_sound_id(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_id)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self._dependencies_for_sound_id, "sound_id", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for AudioPlaybackParms.{field_name} ({field_type}): {e}"
                )


def _decode_maximum_distance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_fall_off(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_id(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_max_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_min_volume(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_use_room_acoustics(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xe449f72: ('maximum_distance', _decode_maximum_distance),
    0x72531867: ('fall_off', _decode_fall_off),
    0xaf85a374: ('sound_id', _decode_sound_id),
    0xc712847c: ('max_volume', _decode_max_volume),
    0x57619496: ('min_volume', _decode_min_volume),
    0x85707354: ('use_room_acoustics', _decode_use_room_acoustics),
}
