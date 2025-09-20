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
from retro_data_structures.properties.corruption.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.corruption.archetypes.PlasmaBeamInfo import PlasmaBeamInfo
from retro_data_structures.properties.corruption.archetypes.UnknownStruct7 import UnknownStruct7

if typing.TYPE_CHECKING:
    class UnknownStruct13Json(typing_extensions.TypedDict):
        beam_info: json_util.JsonObject
        damage: json_util.JsonObject
        attack_duration: float
        attack_duration_variance: float
        turn_speed: float
        movement_speed: float
        unknown_0x569e40ef: float
        unknown_0x682b8867: float
        unknown_0x0acbf084: float
        unknown_0xb638cfa7: float
        unknown_0x18505e36: float
        unknown_struct7: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct13(BaseProperty):
    beam_info: PlasmaBeamInfo = dataclasses.field(default_factory=PlasmaBeamInfo, metadata={
        'reflection': FieldReflection[PlasmaBeamInfo](
            PlasmaBeamInfo, id=0x1598012a, original_name='BeamInfo', from_json=PlasmaBeamInfo.from_json, to_json=PlasmaBeamInfo.to_json
        ),
    })
    damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x337f9524, original_name='Damage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    attack_duration: float = dataclasses.field(default=7.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x16342c18, original_name='AttackDuration'
        ),
    })
    attack_duration_variance: float = dataclasses.field(default=8.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf6bdafb8, original_name='AttackDurationVariance'
        ),
    })
    turn_speed: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x020c78bb, original_name='TurnSpeed'
        ),
    })
    movement_speed: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x416f15e8, original_name='MovementSpeed'
        ),
    })
    unknown_0x569e40ef: float = dataclasses.field(default=30.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x569e40ef, original_name='Unknown'
        ),
    })
    unknown_0x682b8867: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x682b8867, original_name='Unknown'
        ),
    })
    unknown_0x0acbf084: float = dataclasses.field(default=60.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0acbf084, original_name='Unknown'
        ),
    })
    unknown_0xb638cfa7: float = dataclasses.field(default=1.2999999523162842, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb638cfa7, original_name='Unknown'
        ),
    })
    unknown_0x18505e36: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x18505e36, original_name='Unknown'
        ),
    })
    unknown_struct7: UnknownStruct7 = dataclasses.field(default_factory=UnknownStruct7, metadata={
        'reflection': FieldReflection[UnknownStruct7](
            UnknownStruct7, id=0x659df76d, original_name='UnknownStruct7', from_json=UnknownStruct7.from_json, to_json=UnknownStruct7.to_json
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
        if property_count != 12:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1598012a
        beam_info = PlasmaBeamInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x337f9524
        damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x16342c18
        attack_duration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf6bdafb8
        attack_duration_variance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x020c78bb
        turn_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x416f15e8
        movement_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x569e40ef
        unknown_0x569e40ef = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x682b8867
        unknown_0x682b8867 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0acbf084
        unknown_0x0acbf084 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb638cfa7
        unknown_0xb638cfa7 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x18505e36
        unknown_0x18505e36 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x659df76d
        unknown_struct7 = UnknownStruct7.from_stream(data, property_size)
    
        return cls(beam_info, damage, attack_duration, attack_duration_variance, turn_speed, movement_speed, unknown_0x569e40ef, unknown_0x682b8867, unknown_0x0acbf084, unknown_0xb638cfa7, unknown_0x18505e36, unknown_struct7)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0c')  # 12 properties

        data.write(b'\x15\x98\x01*')  # 0x1598012a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'3\x7f\x95$')  # 0x337f9524
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x164,\x18')  # 0x16342c18
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_duration))

        data.write(b'\xf6\xbd\xaf\xb8')  # 0xf6bdafb8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.attack_duration_variance))

        data.write(b'\x02\x0cx\xbb')  # 0x20c78bb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.turn_speed))

        data.write(b'Ao\x15\xe8')  # 0x416f15e8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.movement_speed))

        data.write(b'V\x9e@\xef')  # 0x569e40ef
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x569e40ef))

        data.write(b'h+\x88g')  # 0x682b8867
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x682b8867))

        data.write(b'\n\xcb\xf0\x84')  # 0xacbf084
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0acbf084))

        data.write(b'\xb68\xcf\xa7')  # 0xb638cfa7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb638cfa7))

        data.write(b'\x18P^6')  # 0x18505e36
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x18505e36))

        data.write(b'e\x9d\xf7m')  # 0x659df76d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct7.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct13Json", data)
        return cls(
            beam_info=PlasmaBeamInfo.from_json(json_data['beam_info']),
            damage=DamageInfo.from_json(json_data['damage']),
            attack_duration=json_data['attack_duration'],
            attack_duration_variance=json_data['attack_duration_variance'],
            turn_speed=json_data['turn_speed'],
            movement_speed=json_data['movement_speed'],
            unknown_0x569e40ef=json_data['unknown_0x569e40ef'],
            unknown_0x682b8867=json_data['unknown_0x682b8867'],
            unknown_0x0acbf084=json_data['unknown_0x0acbf084'],
            unknown_0xb638cfa7=json_data['unknown_0xb638cfa7'],
            unknown_0x18505e36=json_data['unknown_0x18505e36'],
            unknown_struct7=UnknownStruct7.from_json(json_data['unknown_struct7']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'beam_info': self.beam_info.to_json(),
            'damage': self.damage.to_json(),
            'attack_duration': self.attack_duration,
            'attack_duration_variance': self.attack_duration_variance,
            'turn_speed': self.turn_speed,
            'movement_speed': self.movement_speed,
            'unknown_0x569e40ef': self.unknown_0x569e40ef,
            'unknown_0x682b8867': self.unknown_0x682b8867,
            'unknown_0x0acbf084': self.unknown_0x0acbf084,
            'unknown_0xb638cfa7': self.unknown_0xb638cfa7,
            'unknown_0x18505e36': self.unknown_0x18505e36,
            'unknown_struct7': self.unknown_struct7.to_json(),
        }


def _decode_attack_duration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_attack_duration_variance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_turn_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_movement_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x569e40ef(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x682b8867(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0acbf084(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb638cfa7(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x18505e36(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x1598012a: ('beam_info', PlasmaBeamInfo.from_stream),
    0x337f9524: ('damage', DamageInfo.from_stream),
    0x16342c18: ('attack_duration', _decode_attack_duration),
    0xf6bdafb8: ('attack_duration_variance', _decode_attack_duration_variance),
    0x20c78bb: ('turn_speed', _decode_turn_speed),
    0x416f15e8: ('movement_speed', _decode_movement_speed),
    0x569e40ef: ('unknown_0x569e40ef', _decode_unknown_0x569e40ef),
    0x682b8867: ('unknown_0x682b8867', _decode_unknown_0x682b8867),
    0xacbf084: ('unknown_0x0acbf084', _decode_unknown_0x0acbf084),
    0xb638cfa7: ('unknown_0xb638cfa7', _decode_unknown_0xb638cfa7),
    0x18505e36: ('unknown_0x18505e36', _decode_unknown_0x18505e36),
    0x659df76d: ('unknown_struct7', UnknownStruct7.from_stream),
}
