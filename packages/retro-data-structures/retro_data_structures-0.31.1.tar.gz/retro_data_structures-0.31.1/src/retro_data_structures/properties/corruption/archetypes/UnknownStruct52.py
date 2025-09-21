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
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability

if typing.TYPE_CHECKING:
    class UnknownStruct52Json(typing_extensions.TypedDict):
        unknown_0xde7e9f94: int
        damage_vulnerability: json_util.JsonObject
        wander_vulnerability: json_util.JsonObject
        crawl_radius: float
        roll_radius: float
        unknown_0xa265383c: float
        forward_priority: float
        unknown_0x2f798cdd: float
    

@dataclasses.dataclass()
class UnknownStruct52(BaseProperty):
    unknown_0xde7e9f94: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0xde7e9f94, original_name='Unknown'
        ),
    })
    damage_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x5d84ed71, original_name='DamageVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    wander_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xf382dff7, original_name='WanderVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    crawl_radius: float = dataclasses.field(default=0.3499999940395355, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad98e16d, original_name='CrawlRadius'
        ),
    })
    roll_radius: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x81d699b0, original_name='RollRadius'
        ),
    })
    unknown_0xa265383c: float = dataclasses.field(default=0.019999999552965164, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa265383c, original_name='Unknown'
        ),
    })
    forward_priority: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad08e189, original_name='ForwardPriority'
        ),
    })
    unknown_0x2f798cdd: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2f798cdd, original_name='Unknown'
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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xde7e9f94
        unknown_0xde7e9f94 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5d84ed71
        damage_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf382dff7
        wander_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad98e16d
        crawl_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x81d699b0
        roll_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa265383c
        unknown_0xa265383c = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xad08e189
        forward_priority = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2f798cdd
        unknown_0x2f798cdd = struct.unpack('>f', data.read(4))[0]
    
        return cls(unknown_0xde7e9f94, damage_vulnerability, wander_vulnerability, crawl_radius, roll_radius, unknown_0xa265383c, forward_priority, unknown_0x2f798cdd)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\xde~\x9f\x94')  # 0xde7e9f94
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.unknown_0xde7e9f94))

        data.write(b']\x84\xedq')  # 0x5d84ed71
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf3\x82\xdf\xf7')  # 0xf382dff7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.wander_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xad\x98\xe1m')  # 0xad98e16d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.crawl_radius))

        data.write(b'\x81\xd6\x99\xb0')  # 0x81d699b0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.roll_radius))

        data.write(b'\xa2e8<')  # 0xa265383c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa265383c))

        data.write(b'\xad\x08\xe1\x89')  # 0xad08e189
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.forward_priority))

        data.write(b'/y\x8c\xdd')  # 0x2f798cdd
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2f798cdd))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct52Json", data)
        return cls(
            unknown_0xde7e9f94=json_data['unknown_0xde7e9f94'],
            damage_vulnerability=DamageVulnerability.from_json(json_data['damage_vulnerability']),
            wander_vulnerability=DamageVulnerability.from_json(json_data['wander_vulnerability']),
            crawl_radius=json_data['crawl_radius'],
            roll_radius=json_data['roll_radius'],
            unknown_0xa265383c=json_data['unknown_0xa265383c'],
            forward_priority=json_data['forward_priority'],
            unknown_0x2f798cdd=json_data['unknown_0x2f798cdd'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xde7e9f94': self.unknown_0xde7e9f94,
            'damage_vulnerability': self.damage_vulnerability.to_json(),
            'wander_vulnerability': self.wander_vulnerability.to_json(),
            'crawl_radius': self.crawl_radius,
            'roll_radius': self.roll_radius,
            'unknown_0xa265383c': self.unknown_0xa265383c,
            'forward_priority': self.forward_priority,
            'unknown_0x2f798cdd': self.unknown_0x2f798cdd,
        }


def _decode_unknown_0xde7e9f94(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_crawl_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_roll_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa265383c(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_forward_priority(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2f798cdd(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xde7e9f94: ('unknown_0xde7e9f94', _decode_unknown_0xde7e9f94),
    0x5d84ed71: ('damage_vulnerability', DamageVulnerability.from_stream),
    0xf382dff7: ('wander_vulnerability', DamageVulnerability.from_stream),
    0xad98e16d: ('crawl_radius', _decode_crawl_radius),
    0x81d699b0: ('roll_radius', _decode_roll_radius),
    0xa265383c: ('unknown_0xa265383c', _decode_unknown_0xa265383c),
    0xad08e189: ('forward_priority', _decode_forward_priority),
    0x2f798cdd: ('unknown_0x2f798cdd', _decode_unknown_0x2f798cdd),
}
