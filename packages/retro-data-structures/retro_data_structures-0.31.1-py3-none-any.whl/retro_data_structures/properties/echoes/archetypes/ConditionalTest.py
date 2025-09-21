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
import retro_data_structures.enums.echoes as enums

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class ConditionalTestJson(typing_extensions.TypedDict):
        boolean: int
        player_item: int
        amount_or_capacity: int
        condition: int
        value: int
    

class Boolean(enum.IntEnum):
    Unknown = 0
    And = 1
    Or = 2

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


class AmountOrCapacity(enum.IntEnum):
    Amount = 0
    Capacity = 1

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


class Condition(enum.IntEnum):
    EqualTo = 0
    NotEqualTo = 1
    GreaterThan = 2
    LessThan = 3
    GreaterThanorEqualTo = 4
    LessThanorEqualTo = 5
    Unknown = 6

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None) -> typing_extensions.Self:
        return cls(struct.unpack(">L", data.read(4))[0])

    def to_stream(self, data: typing.BinaryIO) -> None:
        data.write(struct.pack(">L", self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        assert isinstance(data, (int))
        return cls(data)

    def to_json(self) -> int:
        return self.value


_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xde3e40a3, 0xd3af8d72, 0x3bdea98, 0x70729364, 0x8db9398a)


@dataclasses.dataclass()
class ConditionalTest(BaseProperty):
    boolean: Boolean = dataclasses.field(default=Boolean.And, metadata={
        'reflection': FieldReflection[Boolean](
            Boolean, id=0xde3e40a3, original_name='Boolean', from_json=Boolean.from_json, to_json=Boolean.to_json
        ),
    })
    player_item: enums.PlayerItemEnum = dataclasses.field(default=enums.PlayerItemEnum.PowerBeam, metadata={
        'reflection': FieldReflection[enums.PlayerItemEnum](
            enums.PlayerItemEnum, id=0xd3af8d72, original_name='PlayerItem', from_json=enums.PlayerItemEnum.from_json, to_json=enums.PlayerItemEnum.to_json
        ),
    })
    amount_or_capacity: AmountOrCapacity = dataclasses.field(default=AmountOrCapacity.Amount, metadata={
        'reflection': FieldReflection[AmountOrCapacity](
            AmountOrCapacity, id=0x03bdea98, original_name='AmountOrCapacity', from_json=AmountOrCapacity.from_json, to_json=AmountOrCapacity.to_json
        ),
    })
    condition: Condition = dataclasses.field(default=Condition.EqualTo, metadata={
        'reflection': FieldReflection[Condition](
            Condition, id=0x70729364, original_name='Condition', from_json=Condition.from_json, to_json=Condition.to_json
        ),
    })
    value: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x8db9398a, original_name='Value'
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
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHLLHLLHLLHLLHl')
    
        dec = _FAST_FORMAT.unpack(data.read(50))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12]) == _FAST_IDS
        return cls(
            Boolean(dec[2]),
            enums.PlayerItemEnum(dec[5]),
            AmountOrCapacity(dec[8]),
            Condition(dec[11]),
            dec[14],
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'\xde>@\xa3')  # 0xde3e40a3
        data.write(b'\x00\x04')  # size
        self.boolean.to_stream(data)

        data.write(b'\xd3\xaf\x8dr')  # 0xd3af8d72
        data.write(b'\x00\x04')  # size
        self.player_item.to_stream(data)

        data.write(b'\x03\xbd\xea\x98')  # 0x3bdea98
        data.write(b'\x00\x04')  # size
        self.amount_or_capacity.to_stream(data)

        data.write(b'pr\x93d')  # 0x70729364
        data.write(b'\x00\x04')  # size
        self.condition.to_stream(data)

        data.write(b'\x8d\xb99\x8a')  # 0x8db9398a
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.value))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("ConditionalTestJson", data)
        return cls(
            boolean=Boolean.from_json(json_data['boolean']),
            player_item=enums.PlayerItemEnum.from_json(json_data['player_item']),
            amount_or_capacity=AmountOrCapacity.from_json(json_data['amount_or_capacity']),
            condition=Condition.from_json(json_data['condition']),
            value=json_data['value'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'boolean': self.boolean.to_json(),
            'player_item': self.player_item.to_json(),
            'amount_or_capacity': self.amount_or_capacity.to_json(),
            'condition': self.condition.to_json(),
            'value': self.value,
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_boolean(data: typing.BinaryIO, property_size: int) -> Boolean:
    return Boolean.from_stream(data)


def _decode_player_item(data: typing.BinaryIO, property_size: int) -> enums.PlayerItemEnum:
    return enums.PlayerItemEnum.from_stream(data)


def _decode_amount_or_capacity(data: typing.BinaryIO, property_size: int) -> AmountOrCapacity:
    return AmountOrCapacity.from_stream(data)


def _decode_condition(data: typing.BinaryIO, property_size: int) -> Condition:
    return Condition.from_stream(data)


def _decode_value(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xde3e40a3: ('boolean', _decode_boolean),
    0xd3af8d72: ('player_item', _decode_player_item),
    0x3bdea98: ('amount_or_capacity', _decode_amount_or_capacity),
    0x70729364: ('condition', _decode_condition),
    0x8db9398a: ('value', _decode_value),
}
