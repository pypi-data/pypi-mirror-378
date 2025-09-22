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
from retro_data_structures.properties.corruption.archetypes.GhorStructA import GhorStructA

if typing.TYPE_CHECKING:
    class CircleLineModeJson(typing_extensions.TypedDict):
        ghor_struct_a_0x17386c2c: json_util.JsonObject
        ghor_struct_a_0xd171838c: json_util.JsonObject
        ghor_struct_a_0x017549cb: json_util.JsonObject
        ghor_struct_a_0x08f6bdc5: json_util.JsonObject
        ghor_struct_a_0x7b589dd6: json_util.JsonObject
        collision_set: str
        vulnerability: json_util.JsonObject
    

@dataclasses.dataclass()
class CircleLineMode(BaseProperty):
    ghor_struct_a_0x17386c2c: GhorStructA = dataclasses.field(default_factory=GhorStructA, metadata={
        'reflection': FieldReflection[GhorStructA](
            GhorStructA, id=0x17386c2c, original_name='GhorStructA', from_json=GhorStructA.from_json, to_json=GhorStructA.to_json
        ),
    })
    ghor_struct_a_0xd171838c: GhorStructA = dataclasses.field(default_factory=GhorStructA, metadata={
        'reflection': FieldReflection[GhorStructA](
            GhorStructA, id=0xd171838c, original_name='GhorStructA', from_json=GhorStructA.from_json, to_json=GhorStructA.to_json
        ),
    })
    ghor_struct_a_0x017549cb: GhorStructA = dataclasses.field(default_factory=GhorStructA, metadata={
        'reflection': FieldReflection[GhorStructA](
            GhorStructA, id=0x017549cb, original_name='GhorStructA', from_json=GhorStructA.from_json, to_json=GhorStructA.to_json
        ),
    })
    ghor_struct_a_0x08f6bdc5: GhorStructA = dataclasses.field(default_factory=GhorStructA, metadata={
        'reflection': FieldReflection[GhorStructA](
            GhorStructA, id=0x08f6bdc5, original_name='GhorStructA', from_json=GhorStructA.from_json, to_json=GhorStructA.to_json
        ),
    })
    ghor_struct_a_0x7b589dd6: GhorStructA = dataclasses.field(default_factory=GhorStructA, metadata={
        'reflection': FieldReflection[GhorStructA](
            GhorStructA, id=0x7b589dd6, original_name='GhorStructA', from_json=GhorStructA.from_json, to_json=GhorStructA.to_json
        ),
    })
    collision_set: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x9ce31ffa, original_name='CollisionSet'
        ),
    })
    vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x7b71ae90, original_name='Vulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
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
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x17386c2c
        ghor_struct_a_0x17386c2c = GhorStructA.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd171838c
        ghor_struct_a_0xd171838c = GhorStructA.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x017549cb
        ghor_struct_a_0x017549cb = GhorStructA.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x08f6bdc5
        ghor_struct_a_0x08f6bdc5 = GhorStructA.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b589dd6
        ghor_struct_a_0x7b589dd6 = GhorStructA.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9ce31ffa
        collision_set = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7b71ae90
        vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        return cls(ghor_struct_a_0x17386c2c, ghor_struct_a_0xd171838c, ghor_struct_a_0x017549cb, ghor_struct_a_0x08f6bdc5, ghor_struct_a_0x7b589dd6, collision_set, vulnerability)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'\x178l,')  # 0x17386c2c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_a_0x17386c2c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd1q\x83\x8c')  # 0xd171838c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_a_0xd171838c.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x01uI\xcb')  # 0x17549cb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_a_0x017549cb.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x08\xf6\xbd\xc5')  # 0x8f6bdc5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_a_0x08f6bdc5.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{X\x9d\xd6')  # 0x7b589dd6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ghor_struct_a_0x7b589dd6.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9c\xe3\x1f\xfa')  # 0x9ce31ffa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.collision_set.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'{q\xae\x90')  # 0x7b71ae90
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("CircleLineModeJson", data)
        return cls(
            ghor_struct_a_0x17386c2c=GhorStructA.from_json(json_data['ghor_struct_a_0x17386c2c']),
            ghor_struct_a_0xd171838c=GhorStructA.from_json(json_data['ghor_struct_a_0xd171838c']),
            ghor_struct_a_0x017549cb=GhorStructA.from_json(json_data['ghor_struct_a_0x017549cb']),
            ghor_struct_a_0x08f6bdc5=GhorStructA.from_json(json_data['ghor_struct_a_0x08f6bdc5']),
            ghor_struct_a_0x7b589dd6=GhorStructA.from_json(json_data['ghor_struct_a_0x7b589dd6']),
            collision_set=json_data['collision_set'],
            vulnerability=DamageVulnerability.from_json(json_data['vulnerability']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'ghor_struct_a_0x17386c2c': self.ghor_struct_a_0x17386c2c.to_json(),
            'ghor_struct_a_0xd171838c': self.ghor_struct_a_0xd171838c.to_json(),
            'ghor_struct_a_0x017549cb': self.ghor_struct_a_0x017549cb.to_json(),
            'ghor_struct_a_0x08f6bdc5': self.ghor_struct_a_0x08f6bdc5.to_json(),
            'ghor_struct_a_0x7b589dd6': self.ghor_struct_a_0x7b589dd6.to_json(),
            'collision_set': self.collision_set,
            'vulnerability': self.vulnerability.to_json(),
        }


def _decode_collision_set(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x17386c2c: ('ghor_struct_a_0x17386c2c', GhorStructA.from_stream),
    0xd171838c: ('ghor_struct_a_0xd171838c', GhorStructA.from_stream),
    0x17549cb: ('ghor_struct_a_0x017549cb', GhorStructA.from_stream),
    0x8f6bdc5: ('ghor_struct_a_0x08f6bdc5', GhorStructA.from_stream),
    0x7b589dd6: ('ghor_struct_a_0x7b589dd6', GhorStructA.from_stream),
    0x9ce31ffa: ('collision_set', _decode_collision_set),
    0x7b71ae90: ('vulnerability', DamageVulnerability.from_stream),
}
