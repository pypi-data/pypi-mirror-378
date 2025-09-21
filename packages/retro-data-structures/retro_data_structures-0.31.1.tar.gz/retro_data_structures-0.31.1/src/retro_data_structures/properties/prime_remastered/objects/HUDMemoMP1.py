# Generated File
from __future__ import annotations

import dataclasses
import enum
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.prime_remastered.core.AssetId import AssetId, default_asset_id
import uuid

if typing.TYPE_CHECKING:
    class HUDMemoMP1Json(typing_extensions.TypedDict):
        unk_int_1: int
        memo_type: int
        guid_1: str
        unk_bool_1: bool
        unk_int_3: int
    

class MemoType(enum.IntEnum):
    StatusMessage = 0
    MessageBox = 1

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack("<L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack("<L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


def _from_json_guid_1(data: json_util.JsonValue) -> AssetId:
    json_data = typing.cast(str, data)
    return uuid.UUID(json_data)


def _to_json_guid_1(obj: AssetId) -> json_util.JsonValue:
    return str(obj)


@dataclasses.dataclass()
class HUDMemoMP1(BaseProperty):
    unk_int_1: int = dataclasses.field(default=1077936128, metadata={
        'reflection': FieldReflection[int](
            int, id=0xf429b4d0, original_name='Unk Int 1'
        ),
    })
    memo_type: MemoType = dataclasses.field(default=MemoType.StatusMessage, metadata={
        'reflection': FieldReflection[MemoType](
            MemoType, id=0x1e1f3dfd, original_name='Memo Type', from_json=MemoType.from_json, to_json=MemoType.to_json
        ),
    })
    guid_1: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': [], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xd786d118, original_name='GUID 1', from_json=_from_json_guid_1, to_json=_to_json_guid_1
        ),
    })
    unk_bool_1: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe73cc9cf, original_name='Unk Bool 1'
        ),
    })
    unk_int_3: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x56e17395, original_name='Unk Int 3'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME_REMASTER

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack("<H", data.read(2))[0]
        if (result := cls._fast_decode(data, property_count)) is not None:
            return result

        present_fields = default_override or {}
        for _ in range(property_count):
            property_id, property_size = struct.unpack("<LH", data.read(6))
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
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0xf429b4d0
        unk_int_1 = struct.unpack('<l', data.read(4))[0]
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0x1e1f3dfd
        memo_type = MemoType.from_stream(data)
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0xd786d118
        guid_1 = uuid.UUID(bytes_le=data.read(16))
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0xe73cc9cf
        unk_bool_1 = struct.unpack('<?', data.read(1))[0]
    
        property_id, property_size = struct.unpack("<LH", data.read(6))
        assert property_id == 0x56e17395
        unk_int_3 = struct.unpack('<l', data.read(4))[0]
    
        return cls(unk_int_1, memo_type, guid_1, unk_bool_1, unk_int_3)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        num_properties_offset = data.tell()
        data.write(b'\x00\x00')  # 0 properties
        num_properties_written = 0

        if self.unk_int_1 != default_override.get('unk_int_1', 1077936128):
            num_properties_written += 1
            data.write(b'\xd0\xb4)\xf4')  # 0xf429b4d0
            data.write(b'\x04\x00')  # size
            data.write(struct.pack('<l', self.unk_int_1))

        if self.memo_type != default_override.get('memo_type', MemoType.StatusMessage):
            num_properties_written += 1
            data.write(b'\xfd=\x1f\x1e')  # 0x1e1f3dfd
            data.write(b'\x04\x00')  # size
            self.memo_type.to_stream(data)

        if self.guid_1 != default_override.get('guid_1', default_asset_id):
            num_properties_written += 1
            data.write(b'\x18\xd1\x86\xd7')  # 0xd786d118
            data.write(b'\x10\x00')  # size
            data.write(self.guid_1.bytes_le)

        if self.unk_bool_1 != default_override.get('unk_bool_1', True):
            num_properties_written += 1
            data.write(b'\xcf\xc9<\xe7')  # 0xe73cc9cf
            data.write(b'\x01\x00')  # size
            data.write(struct.pack('<?', self.unk_bool_1))

        if self.unk_int_3 != default_override.get('unk_int_3', 0):
            num_properties_written += 1
            data.write(b'\x95s\xe1V')  # 0x56e17395
            data.write(b'\x04\x00')  # size
            data.write(struct.pack('<l', self.unk_int_3))

        if num_properties_written != 0:
            struct_end_offset = data.tell()
            data.seek(num_properties_offset)
            data.write(struct.pack("<H", num_properties_written))
            data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("HUDMemoMP1Json", data)
        return cls(
            unk_int_1=json_data['unk_int_1'],
            memo_type=MemoType.from_json(json_data['memo_type']),
            guid_1=uuid.UUID(json_data['guid_1']),
            unk_bool_1=json_data['unk_bool_1'],
            unk_int_3=json_data['unk_int_3'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unk_int_1': self.unk_int_1,
            'memo_type': self.memo_type.to_json(),
            'guid_1': str(self.guid_1),
            'unk_bool_1': self.unk_bool_1,
            'unk_int_3': self.unk_int_3,
        }


def _decode_unk_int_1(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('<l', data.read(4))[0]


def _decode_memo_type(data: typing.BinaryIO, property_size: int) -> MemoType:
    return MemoType.from_stream(data)


def _decode_guid_1(data: typing.BinaryIO, property_size: int) -> AssetId:
    return uuid.UUID(bytes_le=data.read(16))


def _decode_unk_bool_1(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('<?', data.read(1))[0]


def _decode_unk_int_3(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('<l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xf429b4d0: ('unk_int_1', _decode_unk_int_1),
    0x1e1f3dfd: ('memo_type', _decode_memo_type),
    0xd786d118: ('guid_1', _decode_guid_1),
    0xe73cc9cf: ('unk_bool_1', _decode_unk_bool_1),
    0x56e17395: ('unk_int_3', _decode_unk_int_3),
}
