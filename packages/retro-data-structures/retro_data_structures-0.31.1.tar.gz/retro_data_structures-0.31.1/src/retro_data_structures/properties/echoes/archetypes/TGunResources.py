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

    class TGunResourcesJson(typing_extensions.TypedDict):
        power_beam: str
        ice_beam: str
        wave_beam: str
        plasma_beam: str
        phazon_beam: str
    

@dataclasses.dataclass()
class TGunResources(BaseProperty):
    power_beam: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x2705318d, original_name='Power_Beam'
        ),
    })
    ice_beam: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x7cc2879f, original_name='Ice_Beam'
        ),
    })
    wave_beam: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x382765b0, original_name='Wave_Beam'
        ),
    })
    plasma_beam: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xcb269ac8, original_name='Plasma_Beam'
        ),
    })
    phazon_beam: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xa3890335, original_name='Phazon_Beam'
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
        if property_count != 5:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2705318d
        power_beam = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7cc2879f
        ice_beam = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x382765b0
        wave_beam = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb269ac8
        plasma_beam = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa3890335
        phazon_beam = data.read(property_size)[:-1].decode("utf-8")
    
        return cls(power_beam, ice_beam, wave_beam, plasma_beam, phazon_beam)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b"'\x051\x8d")  # 0x2705318d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.power_beam.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'|\xc2\x87\x9f')  # 0x7cc2879f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.ice_beam.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b"8'e\xb0")  # 0x382765b0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.wave_beam.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcb&\x9a\xc8')  # 0xcb269ac8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.plasma_beam.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa3\x89\x035')  # 0xa3890335
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.phazon_beam.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TGunResourcesJson", data)
        return cls(
            power_beam=json_data['power_beam'],
            ice_beam=json_data['ice_beam'],
            wave_beam=json_data['wave_beam'],
            plasma_beam=json_data['plasma_beam'],
            phazon_beam=json_data['phazon_beam'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'power_beam': self.power_beam,
            'ice_beam': self.ice_beam,
            'wave_beam': self.wave_beam,
            'plasma_beam': self.plasma_beam,
            'phazon_beam': self.phazon_beam,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_power_beam(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_ice_beam(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_wave_beam(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_plasma_beam(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_phazon_beam(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x2705318d: ('power_beam', _decode_power_beam),
    0x7cc2879f: ('ice_beam', _decode_ice_beam),
    0x382765b0: ('wave_beam', _decode_wave_beam),
    0xcb269ac8: ('plasma_beam', _decode_plasma_beam),
    0xa3890335: ('phazon_beam', _decode_phazon_beam),
}
