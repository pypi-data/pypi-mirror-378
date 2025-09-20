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
from retro_data_structures.properties.corruption.archetypes.DamageVulnerability import DamageVulnerability

if typing.TYPE_CHECKING:
    class UnknownStruct34Json(typing_extensions.TypedDict):
        speed_increase: float
        hyper_mode_vulnerability: json_util.JsonObject
        min_hyper_mode_time: float
        max_hyper_mode_time: float
        min_cloaked_time: float
        max_cloaked_time: float
        unknown_0x587fa387: float
        unknown_0x3e9ac5f3: float
        melee_damage: json_util.JsonObject
        radial_melee_damage: json_util.JsonObject
        energy_wave_projectile_damage: json_util.JsonObject
    

@dataclasses.dataclass()
class UnknownStruct34(BaseProperty):
    speed_increase: float = dataclasses.field(default=1.2000000476837158, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6552bcc0, original_name='SpeedIncrease'
        ),
    })
    hyper_mode_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0xc8a1eac8, original_name='HyperModeVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    min_hyper_mode_time: float = dataclasses.field(default=20.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xede35a42, original_name='MinHyperModeTime'
        ),
    })
    max_hyper_mode_time: float = dataclasses.field(default=25.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xfea6bce9, original_name='MaxHyperModeTime'
        ),
    })
    min_cloaked_time: float = dataclasses.field(default=10.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x86064471, original_name='MinCloakedTime'
        ),
    })
    max_cloaked_time: float = dataclasses.field(default=15.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2132c408, original_name='MaxCloakedTime'
        ),
    })
    unknown_0x587fa387: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x587fa387, original_name='Unknown'
        ),
    })
    unknown_0x3e9ac5f3: float = dataclasses.field(default=4.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3e9ac5f3, original_name='Unknown'
        ),
    })
    melee_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xc9416034, original_name='MeleeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    radial_melee_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x5f11893b, original_name='RadialMeleeDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    energy_wave_projectile_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x37ed6ebb, original_name='EnergyWaveProjectileDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
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
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6552bcc0
        speed_increase = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8a1eac8
        hyper_mode_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xede35a42
        min_hyper_mode_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xfea6bce9
        max_hyper_mode_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x86064471
        min_cloaked_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2132c408
        max_cloaked_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x587fa387
        unknown_0x587fa387 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x3e9ac5f3
        unknown_0x3e9ac5f3 = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc9416034
        melee_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5f11893b
        radial_melee_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x37ed6ebb
        energy_wave_projectile_damage = DamageInfo.from_stream(data, property_size)
    
        return cls(speed_increase, hyper_mode_vulnerability, min_hyper_mode_time, max_hyper_mode_time, min_cloaked_time, max_cloaked_time, unknown_0x587fa387, unknown_0x3e9ac5f3, melee_damage, radial_melee_damage, energy_wave_projectile_damage)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'eR\xbc\xc0')  # 0x6552bcc0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed_increase))

        data.write(b'\xc8\xa1\xea\xc8')  # 0xc8a1eac8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_mode_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\xe3ZB')  # 0xede35a42
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_hyper_mode_time))

        data.write(b'\xfe\xa6\xbc\xe9')  # 0xfea6bce9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_hyper_mode_time))

        data.write(b'\x86\x06Dq')  # 0x86064471
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.min_cloaked_time))

        data.write(b'!2\xc4\x08')  # 0x2132c408
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.max_cloaked_time))

        data.write(b'X\x7f\xa3\x87')  # 0x587fa387
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x587fa387))

        data.write(b'>\x9a\xc5\xf3')  # 0x3e9ac5f3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3e9ac5f3))

        data.write(b'\xc9A`4')  # 0xc9416034
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.melee_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'_\x11\x89;')  # 0x5f11893b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.radial_melee_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'7\xedn\xbb')  # 0x37ed6ebb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.energy_wave_projectile_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("UnknownStruct34Json", data)
        return cls(
            speed_increase=json_data['speed_increase'],
            hyper_mode_vulnerability=DamageVulnerability.from_json(json_data['hyper_mode_vulnerability']),
            min_hyper_mode_time=json_data['min_hyper_mode_time'],
            max_hyper_mode_time=json_data['max_hyper_mode_time'],
            min_cloaked_time=json_data['min_cloaked_time'],
            max_cloaked_time=json_data['max_cloaked_time'],
            unknown_0x587fa387=json_data['unknown_0x587fa387'],
            unknown_0x3e9ac5f3=json_data['unknown_0x3e9ac5f3'],
            melee_damage=DamageInfo.from_json(json_data['melee_damage']),
            radial_melee_damage=DamageInfo.from_json(json_data['radial_melee_damage']),
            energy_wave_projectile_damage=DamageInfo.from_json(json_data['energy_wave_projectile_damage']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'speed_increase': self.speed_increase,
            'hyper_mode_vulnerability': self.hyper_mode_vulnerability.to_json(),
            'min_hyper_mode_time': self.min_hyper_mode_time,
            'max_hyper_mode_time': self.max_hyper_mode_time,
            'min_cloaked_time': self.min_cloaked_time,
            'max_cloaked_time': self.max_cloaked_time,
            'unknown_0x587fa387': self.unknown_0x587fa387,
            'unknown_0x3e9ac5f3': self.unknown_0x3e9ac5f3,
            'melee_damage': self.melee_damage.to_json(),
            'radial_melee_damage': self.radial_melee_damage.to_json(),
            'energy_wave_projectile_damage': self.energy_wave_projectile_damage.to_json(),
        }


def _decode_speed_increase(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_hyper_mode_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_hyper_mode_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_min_cloaked_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_max_cloaked_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x587fa387(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3e9ac5f3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x6552bcc0: ('speed_increase', _decode_speed_increase),
    0xc8a1eac8: ('hyper_mode_vulnerability', DamageVulnerability.from_stream),
    0xede35a42: ('min_hyper_mode_time', _decode_min_hyper_mode_time),
    0xfea6bce9: ('max_hyper_mode_time', _decode_max_hyper_mode_time),
    0x86064471: ('min_cloaked_time', _decode_min_cloaked_time),
    0x2132c408: ('max_cloaked_time', _decode_max_cloaked_time),
    0x587fa387: ('unknown_0x587fa387', _decode_unknown_0x587fa387),
    0x3e9ac5f3: ('unknown_0x3e9ac5f3', _decode_unknown_0x3e9ac5f3),
    0xc9416034: ('melee_damage', DamageInfo.from_stream),
    0x5f11893b: ('radial_melee_damage', DamageInfo.from_stream),
    0x37ed6ebb: ('energy_wave_projectile_damage', DamageInfo.from_stream),
}
