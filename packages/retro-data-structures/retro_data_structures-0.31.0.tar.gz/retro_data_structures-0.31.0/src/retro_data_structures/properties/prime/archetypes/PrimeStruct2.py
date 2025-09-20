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
from retro_data_structures.properties.prime.archetypes.PrimeStruct3 import PrimeStruct3

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class PrimeStruct2Json(typing_extensions.TypedDict):
        unknown_1: bool
        unknown_2: float
        unknown_3: float
        prime_struct3_1: json_util.JsonObject
        prime_struct3_2: json_util.JsonObject
        prime_struct3_3: json_util.JsonObject
    

@dataclasses.dataclass()
class PrimeStruct2(BaseProperty):
    unknown_1: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000000, original_name='Unknown 1'
        ),
    })
    unknown_2: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000001, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000002, original_name='Unknown 3'
        ),
    })
    prime_struct3_1: PrimeStruct3 = dataclasses.field(default_factory=PrimeStruct3, metadata={
        'reflection': FieldReflection[PrimeStruct3](
            PrimeStruct3, id=0x00000003, original_name='PrimeStruct3 1', from_json=PrimeStruct3.from_json, to_json=PrimeStruct3.to_json
        ),
    })
    prime_struct3_2: PrimeStruct3 = dataclasses.field(default_factory=PrimeStruct3, metadata={
        'reflection': FieldReflection[PrimeStruct3](
            PrimeStruct3, id=0x00000004, original_name='PrimeStruct3 2', from_json=PrimeStruct3.from_json, to_json=PrimeStruct3.to_json
        ),
    })
    prime_struct3_3: PrimeStruct3 = dataclasses.field(default_factory=PrimeStruct3, metadata={
        'reflection': FieldReflection[PrimeStruct3](
            PrimeStruct3, id=0x00000005, original_name='PrimeStruct3 3', from_json=PrimeStruct3.from_json, to_json=PrimeStruct3.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        unknown_1 = struct.unpack('>?', data.read(1))[0]
        unknown_2 = struct.unpack('>f', data.read(4))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        prime_struct3_1 = PrimeStruct3.from_stream(data, property_size)
        prime_struct3_2 = PrimeStruct3.from_stream(data, property_size)
        prime_struct3_3 = PrimeStruct3.from_stream(data, property_size)
        return cls(unknown_1, unknown_2, unknown_3, prime_struct3_1, prime_struct3_2, prime_struct3_3)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(struct.pack('>?', self.unknown_1))
        data.write(struct.pack('>f', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        self.prime_struct3_1.to_stream(data)
        self.prime_struct3_2.to_stream(data)
        self.prime_struct3_3.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("PrimeStruct2Json", data)
        return cls(
            unknown_1=json_data['unknown_1'],
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            prime_struct3_1=PrimeStruct3.from_json(json_data['prime_struct3_1']),
            prime_struct3_2=PrimeStruct3.from_json(json_data['prime_struct3_2']),
            prime_struct3_3=PrimeStruct3.from_json(json_data['prime_struct3_3']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_1': self.unknown_1,
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'prime_struct3_1': self.prime_struct3_1.to_json(),
            'prime_struct3_2': self.prime_struct3_2.to_json(),
            'prime_struct3_3': self.prime_struct3_3.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.prime_struct3_1.dependencies_for, "prime_struct3_1", "PrimeStruct3"),
            (self.prime_struct3_2.dependencies_for, "prime_struct3_2", "PrimeStruct3"),
            (self.prime_struct3_3.dependencies_for, "prime_struct3_3", "PrimeStruct3"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for PrimeStruct2.{field_name} ({field_type}): {e}"
                )
