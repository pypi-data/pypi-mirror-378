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

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakParticleJson(typing_extensions.TypedDict):
        instance_name: str
        pak_file: str
        primary_weapon: str
        secondary_weapon: str
    

@dataclasses.dataclass()
class TweakParticle(BaseObjectType):
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
    primary_weapon: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x5e15868a, original_name='Primary_Weapon'
        ),
    })
    secondary_weapon: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0xbc401445, original_name='Secondary_Weapon'
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
        return 'TWPA'

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
        if property_count != 4:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fda1466
        instance_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2bd13ab3
        pak_file = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5e15868a
        primary_weapon = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbc401445
        secondary_weapon = data.read(property_size)[:-1].decode("utf-8")
    
        return cls(instance_name, pak_file, primary_weapon, secondary_weapon)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x04')  # 4 properties

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

        data.write(b'^\x15\x86\x8a')  # 0x5e15868a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.primary_weapon.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbc@\x14E')  # 0xbc401445
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.secondary_weapon.encode("utf-8"))
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
        json_data = typing.cast("TweakParticleJson", data)
        return cls(
            instance_name=json_data['instance_name'],
            pak_file=json_data['pak_file'],
            primary_weapon=json_data['primary_weapon'],
            secondary_weapon=json_data['secondary_weapon'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'instance_name': self.instance_name,
            'pak_file': self.pak_file,
            'primary_weapon': self.primary_weapon,
            'secondary_weapon': self.secondary_weapon,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_instance_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_pak_file(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_primary_weapon(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_secondary_weapon(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7fda1466: ('instance_name', _decode_instance_name),
    0x2bd13ab3: ('pak_file', _decode_pak_file),
    0x5e15868a: ('primary_weapon', _decode_primary_weapon),
    0xbc401445: ('secondary_weapon', _decode_secondary_weapon),
}
