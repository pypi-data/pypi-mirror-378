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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class SeedBoss1ShieldJson(typing_extensions.TypedDict):
        cmdl_0xdce1a940: int
        cmdl_0xf4c318b3: int
        cmdl_0xb3673269: int
        cmdl_0xb9196d9e: int
        important_moment: int
        cmdl_0x4d7984e6: int
        cmdl_0x8fbe621d: int
        cmdl_0x11ea2651: int
        cmdl_0x564e0c8b: int
        cmdl_0x807edcc5: int
        cmdl_0x708b0155: int
        cmdl_0xe46803dc: int
        cmdl_0x6a975cff: int
        cmdl_0x97e2b6c7: int
        cmdl_0x1176c469: int
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xdce1a940, 0xf4c318b3, 0xb3673269, 0xb9196d9e, 0x8c0bee98, 0x4d7984e6, 0x8fbe621d, 0x11ea2651, 0x564e0c8b, 0x807edcc5, 0x708b0155, 0xe46803dc, 0x6a975cff, 0x97e2b6c7, 0x1176c469)


@dataclasses.dataclass()
class SeedBoss1Shield(BaseProperty):
    cmdl_0xdce1a940: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xdce1a940, original_name='CMDL'
        ),
    })
    cmdl_0xf4c318b3: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xf4c318b3, original_name='CMDL'
        ),
    })
    cmdl_0xb3673269: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb3673269, original_name='CMDL'
        ),
    })
    cmdl_0xb9196d9e: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xb9196d9e, original_name='CMDL'
        ),
    })
    important_moment: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8c0bee98, original_name='ImportantMoment'
        ),
    })
    cmdl_0x4d7984e6: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x4d7984e6, original_name='CMDL'
        ),
    })
    cmdl_0x8fbe621d: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x8fbe621d, original_name='CMDL'
        ),
    })
    cmdl_0x11ea2651: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x11ea2651, original_name='CMDL'
        ),
    })
    cmdl_0x564e0c8b: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x564e0c8b, original_name='CMDL'
        ),
    })
    cmdl_0x807edcc5: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x807edcc5, original_name='CMDL'
        ),
    })
    cmdl_0x708b0155: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x708b0155, original_name='CMDL'
        ),
    })
    cmdl_0xe46803dc: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xe46803dc, original_name='CMDL'
        ),
    })
    cmdl_0x6a975cff: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x6a975cff, original_name='CMDL'
        ),
    })
    cmdl_0x97e2b6c7: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x97e2b6c7, original_name='CMDL'
        ),
    })
    cmdl_0x1176c469: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1176c469, original_name='CMDL'
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
        if property_count != 15:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHQLHQLHQLHQLHQLHQLHQLHQLHQLHQLHQLHQLHQLHQLHQ')
    
        dec = _FAST_FORMAT.unpack(data.read(210))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[33], dec[36], dec[39], dec[42]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
            dec[26],
            dec[29],
            dec[32],
            dec[35],
            dec[38],
            dec[41],
            dec[44],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'\xdc\xe1\xa9@')  # 0xdce1a940
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xdce1a940))

        data.write(b'\xf4\xc3\x18\xb3')  # 0xf4c318b3
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xf4c318b3))

        data.write(b'\xb3g2i')  # 0xb3673269
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xb3673269))

        data.write(b'\xb9\x19m\x9e')  # 0xb9196d9e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xb9196d9e))

        data.write(b'\x8c\x0b\xee\x98')  # 0x8c0bee98
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.important_moment))

        data.write(b'My\x84\xe6')  # 0x4d7984e6
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x4d7984e6))

        data.write(b'\x8f\xbeb\x1d')  # 0x8fbe621d
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x8fbe621d))

        data.write(b'\x11\xea&Q')  # 0x11ea2651
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x11ea2651))

        data.write(b'VN\x0c\x8b')  # 0x564e0c8b
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x564e0c8b))

        data.write(b'\x80~\xdc\xc5')  # 0x807edcc5
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x807edcc5))

        data.write(b'p\x8b\x01U')  # 0x708b0155
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x708b0155))

        data.write(b'\xe4h\x03\xdc')  # 0xe46803dc
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0xe46803dc))

        data.write(b'j\x97\\\xff')  # 0x6a975cff
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x6a975cff))

        data.write(b'\x97\xe2\xb6\xc7')  # 0x97e2b6c7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x97e2b6c7))

        data.write(b'\x11v\xc4i')  # 0x1176c469
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.cmdl_0x1176c469))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SeedBoss1ShieldJson", data)
        return cls(
            cmdl_0xdce1a940=json_data['cmdl_0xdce1a940'],
            cmdl_0xf4c318b3=json_data['cmdl_0xf4c318b3'],
            cmdl_0xb3673269=json_data['cmdl_0xb3673269'],
            cmdl_0xb9196d9e=json_data['cmdl_0xb9196d9e'],
            important_moment=json_data['important_moment'],
            cmdl_0x4d7984e6=json_data['cmdl_0x4d7984e6'],
            cmdl_0x8fbe621d=json_data['cmdl_0x8fbe621d'],
            cmdl_0x11ea2651=json_data['cmdl_0x11ea2651'],
            cmdl_0x564e0c8b=json_data['cmdl_0x564e0c8b'],
            cmdl_0x807edcc5=json_data['cmdl_0x807edcc5'],
            cmdl_0x708b0155=json_data['cmdl_0x708b0155'],
            cmdl_0xe46803dc=json_data['cmdl_0xe46803dc'],
            cmdl_0x6a975cff=json_data['cmdl_0x6a975cff'],
            cmdl_0x97e2b6c7=json_data['cmdl_0x97e2b6c7'],
            cmdl_0x1176c469=json_data['cmdl_0x1176c469'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'cmdl_0xdce1a940': self.cmdl_0xdce1a940,
            'cmdl_0xf4c318b3': self.cmdl_0xf4c318b3,
            'cmdl_0xb3673269': self.cmdl_0xb3673269,
            'cmdl_0xb9196d9e': self.cmdl_0xb9196d9e,
            'important_moment': self.important_moment,
            'cmdl_0x4d7984e6': self.cmdl_0x4d7984e6,
            'cmdl_0x8fbe621d': self.cmdl_0x8fbe621d,
            'cmdl_0x11ea2651': self.cmdl_0x11ea2651,
            'cmdl_0x564e0c8b': self.cmdl_0x564e0c8b,
            'cmdl_0x807edcc5': self.cmdl_0x807edcc5,
            'cmdl_0x708b0155': self.cmdl_0x708b0155,
            'cmdl_0xe46803dc': self.cmdl_0xe46803dc,
            'cmdl_0x6a975cff': self.cmdl_0x6a975cff,
            'cmdl_0x97e2b6c7': self.cmdl_0x97e2b6c7,
            'cmdl_0x1176c469': self.cmdl_0x1176c469,
        }


def _decode_cmdl_0xdce1a940(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0xf4c318b3(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0xb3673269(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0xb9196d9e(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_important_moment(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x4d7984e6(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x8fbe621d(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x11ea2651(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x564e0c8b(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x807edcc5(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x708b0155(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0xe46803dc(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x6a975cff(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x97e2b6c7(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_cmdl_0x1176c469(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xdce1a940: ('cmdl_0xdce1a940', _decode_cmdl_0xdce1a940),
    0xf4c318b3: ('cmdl_0xf4c318b3', _decode_cmdl_0xf4c318b3),
    0xb3673269: ('cmdl_0xb3673269', _decode_cmdl_0xb3673269),
    0xb9196d9e: ('cmdl_0xb9196d9e', _decode_cmdl_0xb9196d9e),
    0x8c0bee98: ('important_moment', _decode_important_moment),
    0x4d7984e6: ('cmdl_0x4d7984e6', _decode_cmdl_0x4d7984e6),
    0x8fbe621d: ('cmdl_0x8fbe621d', _decode_cmdl_0x8fbe621d),
    0x11ea2651: ('cmdl_0x11ea2651', _decode_cmdl_0x11ea2651),
    0x564e0c8b: ('cmdl_0x564e0c8b', _decode_cmdl_0x564e0c8b),
    0x807edcc5: ('cmdl_0x807edcc5', _decode_cmdl_0x807edcc5),
    0x708b0155: ('cmdl_0x708b0155', _decode_cmdl_0x708b0155),
    0xe46803dc: ('cmdl_0xe46803dc', _decode_cmdl_0xe46803dc),
    0x6a975cff: ('cmdl_0x6a975cff', _decode_cmdl_0x6a975cff),
    0x97e2b6c7: ('cmdl_0x97e2b6c7', _decode_cmdl_0x97e2b6c7),
    0x1176c469: ('cmdl_0x1176c469', _decode_cmdl_0x1176c469),
}
