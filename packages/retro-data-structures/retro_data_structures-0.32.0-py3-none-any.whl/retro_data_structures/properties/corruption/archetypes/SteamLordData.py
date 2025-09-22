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
from retro_data_structures.properties.corruption.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    class SteamLordDataJson(typing_extensions.TypedDict):
        unknown_0xe9553ffa: bool
        is_initially_cloaked: bool
        cloak_time: float
        decloak_time: float
        re_cloak_time: float
        dodge_damage_threshold: float
        dodge_chance: float
        flight_max_speed: float
        flight_acceleration: float
        target_hover_height: float
        repair_hover_height: float
        unknown_0xb35f3997: float
        abort_repair_damage: float
        repair_effect: int
        contact_visor_effect: int
        elsc_0xbe36e228: int
        elsc_0x24a4fc9e: int
        unknown_0xe1f030d5: float
        unknown_0xfb72f91e: float
        damage_info_0xfe138b07: json_util.JsonObject
        damage_info_0xaa19d1dc: json_util.JsonObject
    

@dataclasses.dataclass()
class SteamLordData(BaseProperty):
    unknown_0xe9553ffa: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xe9553ffa, original_name='Unknown'
        ),
    })
    is_initially_cloaked: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x1c893f54, original_name='IsInitiallyCloaked'
        ),
    })
    cloak_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x388bc31f, original_name='CloakTime'
        ),
    })
    decloak_time: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x4319c840, original_name='DecloakTime'
        ),
    })
    re_cloak_time: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3bcbe7e2, original_name='ReCloakTime'
        ),
    })
    dodge_damage_threshold: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x91c8ba81, original_name='DodgeDamageThreshold'
        ),
    })
    dodge_chance: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47be3298, original_name='DodgeChance'
        ),
    })
    flight_max_speed: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xd4dec629, original_name='FlightMaxSpeed'
        ),
    })
    flight_acceleration: float = dataclasses.field(default=2.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a2bb377, original_name='FlightAcceleration'
        ),
    })
    target_hover_height: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x70130fe6, original_name='TargetHoverHeight'
        ),
    })
    repair_hover_height: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfcc4e240, original_name='RepairHoverHeight'
        ),
    })
    unknown_0xb35f3997: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb35f3997, original_name='Unknown'
        ),
    })
    abort_repair_damage: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeba0c5f7, original_name='AbortRepairDamage'
        ),
    })
    repair_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x9f4e6a36, original_name='RepairEffect'
        ),
    })
    contact_visor_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x0de136f7, original_name='ContactVisorEffect'
        ),
    })
    elsc_0xbe36e228: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xbe36e228, original_name='ELSC'
        ),
    })
    elsc_0x24a4fc9e: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x24a4fc9e, original_name='ELSC'
        ),
    })
    unknown_0xe1f030d5: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xe1f030d5, original_name='Unknown'
        ),
    })
    unknown_0xfb72f91e: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfb72f91e, original_name='Unknown'
        ),
    })
    damage_info_0xfe138b07: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xfe138b07, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    damage_info_0xaa19d1dc: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xaa19d1dc, original_name='DamageInfo', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
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
        if property_count != 21:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9553ffa
        unknown_0xe9553ffa = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1c893f54
        is_initially_cloaked = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x388bc31f
        cloak_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4319c840
        decloak_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3bcbe7e2
        re_cloak_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x91c8ba81
        dodge_damage_threshold = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x47be3298
        dodge_chance = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd4dec629
        flight_max_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7a2bb377
        flight_acceleration = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x70130fe6
        target_hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfcc4e240
        repair_hover_height = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb35f3997
        unknown_0xb35f3997 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xeba0c5f7
        abort_repair_damage = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9f4e6a36
        repair_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0de136f7
        contact_visor_effect = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbe36e228
        elsc_0xbe36e228 = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24a4fc9e
        elsc_0x24a4fc9e = struct.unpack(">Q", data.read(8))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe1f030d5
        unknown_0xe1f030d5 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfb72f91e
        unknown_0xfb72f91e = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfe138b07
        damage_info_0xfe138b07 = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaa19d1dc
        damage_info_0xaa19d1dc = DamageInfo.from_stream(data, property_size)
    
        return cls(unknown_0xe9553ffa, is_initially_cloaked, cloak_time, decloak_time, re_cloak_time, dodge_damage_threshold, dodge_chance, flight_max_speed, flight_acceleration, target_hover_height, repair_hover_height, unknown_0xb35f3997, abort_repair_damage, repair_effect, contact_visor_effect, elsc_0xbe36e228, elsc_0x24a4fc9e, unknown_0xe1f030d5, unknown_0xfb72f91e, damage_info_0xfe138b07, damage_info_0xaa19d1dc)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x15')  # 21 properties

        data.write(b'\xe9U?\xfa')  # 0xe9553ffa
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xe9553ffa))

        data.write(b'\x1c\x89?T')  # 0x1c893f54
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.is_initially_cloaked))

        data.write(b'8\x8b\xc3\x1f')  # 0x388bc31f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.cloak_time))

        data.write(b'C\x19\xc8@')  # 0x4319c840
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.decloak_time))

        data.write(b';\xcb\xe7\xe2')  # 0x3bcbe7e2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.re_cloak_time))

        data.write(b'\x91\xc8\xba\x81')  # 0x91c8ba81
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_damage_threshold))

        data.write(b'G\xbe2\x98')  # 0x47be3298
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.dodge_chance))

        data.write(b'\xd4\xde\xc6)')  # 0xd4dec629
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_max_speed))

        data.write(b'z+\xb3w')  # 0x7a2bb377
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.flight_acceleration))

        data.write(b'p\x13\x0f\xe6')  # 0x70130fe6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.target_hover_height))

        data.write(b'\xfc\xc4\xe2@')  # 0xfcc4e240
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.repair_hover_height))

        data.write(b'\xb3_9\x97')  # 0xb35f3997
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb35f3997))

        data.write(b'\xeb\xa0\xc5\xf7')  # 0xeba0c5f7
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.abort_repair_damage))

        data.write(b'\x9fNj6')  # 0x9f4e6a36
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.repair_effect))

        data.write(b'\r\xe16\xf7')  # 0xde136f7
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.contact_visor_effect))

        data.write(b'\xbe6\xe2(')  # 0xbe36e228
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.elsc_0xbe36e228))

        data.write(b'$\xa4\xfc\x9e')  # 0x24a4fc9e
        data.write(b'\x00\x08')  # size
        data.write(struct.pack(">Q", self.elsc_0x24a4fc9e))

        data.write(b'\xe1\xf00\xd5')  # 0xe1f030d5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xe1f030d5))

        data.write(b'\xfbr\xf9\x1e')  # 0xfb72f91e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xfb72f91e))

        data.write(b'\xfe\x13\x8b\x07')  # 0xfe138b07
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0xfe138b07.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xaa\x19\xd1\xdc')  # 0xaa19d1dc
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.damage_info_0xaa19d1dc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SteamLordDataJson", data)
        return cls(
            unknown_0xe9553ffa=json_data['unknown_0xe9553ffa'],
            is_initially_cloaked=json_data['is_initially_cloaked'],
            cloak_time=json_data['cloak_time'],
            decloak_time=json_data['decloak_time'],
            re_cloak_time=json_data['re_cloak_time'],
            dodge_damage_threshold=json_data['dodge_damage_threshold'],
            dodge_chance=json_data['dodge_chance'],
            flight_max_speed=json_data['flight_max_speed'],
            flight_acceleration=json_data['flight_acceleration'],
            target_hover_height=json_data['target_hover_height'],
            repair_hover_height=json_data['repair_hover_height'],
            unknown_0xb35f3997=json_data['unknown_0xb35f3997'],
            abort_repair_damage=json_data['abort_repair_damage'],
            repair_effect=json_data['repair_effect'],
            contact_visor_effect=json_data['contact_visor_effect'],
            elsc_0xbe36e228=json_data['elsc_0xbe36e228'],
            elsc_0x24a4fc9e=json_data['elsc_0x24a4fc9e'],
            unknown_0xe1f030d5=json_data['unknown_0xe1f030d5'],
            unknown_0xfb72f91e=json_data['unknown_0xfb72f91e'],
            damage_info_0xfe138b07=DamageInfo.from_json(json_data['damage_info_0xfe138b07']),
            damage_info_0xaa19d1dc=DamageInfo.from_json(json_data['damage_info_0xaa19d1dc']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xe9553ffa': self.unknown_0xe9553ffa,
            'is_initially_cloaked': self.is_initially_cloaked,
            'cloak_time': self.cloak_time,
            'decloak_time': self.decloak_time,
            're_cloak_time': self.re_cloak_time,
            'dodge_damage_threshold': self.dodge_damage_threshold,
            'dodge_chance': self.dodge_chance,
            'flight_max_speed': self.flight_max_speed,
            'flight_acceleration': self.flight_acceleration,
            'target_hover_height': self.target_hover_height,
            'repair_hover_height': self.repair_hover_height,
            'unknown_0xb35f3997': self.unknown_0xb35f3997,
            'abort_repair_damage': self.abort_repair_damage,
            'repair_effect': self.repair_effect,
            'contact_visor_effect': self.contact_visor_effect,
            'elsc_0xbe36e228': self.elsc_0xbe36e228,
            'elsc_0x24a4fc9e': self.elsc_0x24a4fc9e,
            'unknown_0xe1f030d5': self.unknown_0xe1f030d5,
            'unknown_0xfb72f91e': self.unknown_0xfb72f91e,
            'damage_info_0xfe138b07': self.damage_info_0xfe138b07.to_json(),
            'damage_info_0xaa19d1dc': self.damage_info_0xaa19d1dc.to_json(),
        }


def _decode_unknown_0xe9553ffa(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_is_initially_cloaked(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_cloak_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_decloak_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_re_cloak_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_damage_threshold(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_dodge_chance(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_max_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_flight_acceleration(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_target_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_repair_hover_height(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb35f3997(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_abort_repair_damage(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_repair_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_contact_visor_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_elsc_0xbe36e228(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_elsc_0x24a4fc9e(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">Q", data.read(8))[0]


def _decode_unknown_0xe1f030d5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xfb72f91e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xe9553ffa: ('unknown_0xe9553ffa', _decode_unknown_0xe9553ffa),
    0x1c893f54: ('is_initially_cloaked', _decode_is_initially_cloaked),
    0x388bc31f: ('cloak_time', _decode_cloak_time),
    0x4319c840: ('decloak_time', _decode_decloak_time),
    0x3bcbe7e2: ('re_cloak_time', _decode_re_cloak_time),
    0x91c8ba81: ('dodge_damage_threshold', _decode_dodge_damage_threshold),
    0x47be3298: ('dodge_chance', _decode_dodge_chance),
    0xd4dec629: ('flight_max_speed', _decode_flight_max_speed),
    0x7a2bb377: ('flight_acceleration', _decode_flight_acceleration),
    0x70130fe6: ('target_hover_height', _decode_target_hover_height),
    0xfcc4e240: ('repair_hover_height', _decode_repair_hover_height),
    0xb35f3997: ('unknown_0xb35f3997', _decode_unknown_0xb35f3997),
    0xeba0c5f7: ('abort_repair_damage', _decode_abort_repair_damage),
    0x9f4e6a36: ('repair_effect', _decode_repair_effect),
    0xde136f7: ('contact_visor_effect', _decode_contact_visor_effect),
    0xbe36e228: ('elsc_0xbe36e228', _decode_elsc_0xbe36e228),
    0x24a4fc9e: ('elsc_0x24a4fc9e', _decode_elsc_0x24a4fc9e),
    0xe1f030d5: ('unknown_0xe1f030d5', _decode_unknown_0xe1f030d5),
    0xfb72f91e: ('unknown_0xfb72f91e', _decode_unknown_0xfb72f91e),
    0xfe138b07: ('damage_info_0xfe138b07', DamageInfo.from_stream),
    0xaa19d1dc: ('damage_info_0xaa19d1dc', DamageInfo.from_stream),
}
