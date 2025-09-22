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
from retro_data_structures.properties.prime.archetypes.HealthInfo import HealthInfo
from retro_data_structures.properties.prime.archetypes.MassivePrimeStruct import MassivePrimeStruct
from retro_data_structures.properties.prime.archetypes.PrimeStruct1 import PrimeStruct1
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class MetroidPrimeStage1Json(typing_extensions.TypedDict):
        unknown_1: int
        name: str
        position: json_util.JsonValue
        rotation: json_util.JsonValue
        scale: json_util.JsonValue
        unknown_2: bool
        unknown_3: float
        unknown_4: float
        unknown_5: float
        unknown_6: int
        unknown_7: bool
        unknown_8: int
        health_info_1: json_util.JsonObject
        health_info_2: json_util.JsonObject
        unknown_9: int
        prime_struct1_1: json_util.JsonObject
        prime_struct1_2: json_util.JsonObject
        prime_struct1_3: json_util.JsonObject
        prime_struct1_4: json_util.JsonObject
        unknown_10: int
        unknown_11: int
        unnamed: json_util.JsonObject
    

@dataclasses.dataclass()
class MetroidPrimeStage1(BaseObjectType):
    unknown_1: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000000, original_name='Unknown 1'
        ),
    })
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000001, original_name='Name'
        ),
    })
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    rotation: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000003, original_name='Rotation', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000004, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_2: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000005, original_name='Unknown 2'
        ),
    })
    unknown_3: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000006, original_name='Unknown 3'
        ),
    })
    unknown_4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000007, original_name='Unknown 4'
        ),
    })
    unknown_5: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x00000008, original_name='Unknown 5'
        ),
    })
    unknown_6: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000009, original_name='Unknown 6'
        ),
    })
    unknown_7: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Unknown 7'
        ),
    })
    unknown_8: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000b, original_name='Unknown 8'
        ),
    })
    health_info_1: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x0000000c, original_name='HealthInfo 1', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    health_info_2: HealthInfo = dataclasses.field(default_factory=HealthInfo, metadata={
        'reflection': FieldReflection[HealthInfo](
            HealthInfo, id=0x0000000d, original_name='HealthInfo 2', from_json=HealthInfo.from_json, to_json=HealthInfo.to_json
        ),
    })
    unknown_9: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x0000000e, original_name='Unknown 9'
        ),
    })
    prime_struct1_1: PrimeStruct1 = dataclasses.field(default_factory=PrimeStruct1, metadata={
        'reflection': FieldReflection[PrimeStruct1](
            PrimeStruct1, id=0x0000000f, original_name='PrimeStruct1 1', from_json=PrimeStruct1.from_json, to_json=PrimeStruct1.to_json
        ),
    })
    prime_struct1_2: PrimeStruct1 = dataclasses.field(default_factory=PrimeStruct1, metadata={
        'reflection': FieldReflection[PrimeStruct1](
            PrimeStruct1, id=0x00000010, original_name='PrimeStruct1 2', from_json=PrimeStruct1.from_json, to_json=PrimeStruct1.to_json
        ),
    })
    prime_struct1_3: PrimeStruct1 = dataclasses.field(default_factory=PrimeStruct1, metadata={
        'reflection': FieldReflection[PrimeStruct1](
            PrimeStruct1, id=0x00000011, original_name='PrimeStruct1 3', from_json=PrimeStruct1.from_json, to_json=PrimeStruct1.to_json
        ),
    })
    prime_struct1_4: PrimeStruct1 = dataclasses.field(default_factory=PrimeStruct1, metadata={
        'reflection': FieldReflection[PrimeStruct1](
            PrimeStruct1, id=0x00000012, original_name='PrimeStruct1 4', from_json=PrimeStruct1.from_json, to_json=PrimeStruct1.to_json
        ),
    })
    unknown_10: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000013, original_name='Unknown 10'
        ),
    })
    unknown_11: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000014, original_name='Unknown 11'
        ),
    })
    unnamed: MassivePrimeStruct = dataclasses.field(default_factory=MassivePrimeStruct, metadata={
        'reflection': FieldReflection[MassivePrimeStruct](
            MassivePrimeStruct, id=0x00000015, original_name='21', from_json=MassivePrimeStruct.from_json, to_json=MassivePrimeStruct.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.PRIME

    def get_name(self) -> str | None:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    @classmethod
    def object_type(cls) -> int:
        return 0x84

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        unknown_1 = struct.unpack('>l', data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        rotation = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unknown_2 = struct.unpack('>?', data.read(1))[0]
        unknown_3 = struct.unpack('>f', data.read(4))[0]
        unknown_4 = struct.unpack('>f', data.read(4))[0]
        unknown_5 = struct.unpack('>f', data.read(4))[0]
        unknown_6 = struct.unpack('>l', data.read(4))[0]
        unknown_7 = struct.unpack('>?', data.read(1))[0]
        unknown_8 = struct.unpack('>l', data.read(4))[0]
        health_info_1 = HealthInfo.from_stream(data, property_size)
        health_info_2 = HealthInfo.from_stream(data, property_size)
        unknown_9 = struct.unpack('>l', data.read(4))[0]
        prime_struct1_1 = PrimeStruct1.from_stream(data, property_size)
        prime_struct1_2 = PrimeStruct1.from_stream(data, property_size)
        prime_struct1_3 = PrimeStruct1.from_stream(data, property_size)
        prime_struct1_4 = PrimeStruct1.from_stream(data, property_size)
        unknown_10 = struct.unpack('>l', data.read(4))[0]
        unknown_11 = struct.unpack('>l', data.read(4))[0]
        unnamed = MassivePrimeStruct.from_stream(data, property_size)
        return cls(unknown_1, name, position, rotation, scale, unknown_2, unknown_3, unknown_4, unknown_5, unknown_6, unknown_7, unknown_8, health_info_1, health_info_2, unknown_9, prime_struct1_1, prime_struct1_2, prime_struct1_3, prime_struct1_4, unknown_10, unknown_11, unnamed)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x16')  # 22 properties
        data.write(struct.pack('>l', self.unknown_1))
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.rotation.to_stream(data)
        self.scale.to_stream(data)
        data.write(struct.pack('>?', self.unknown_2))
        data.write(struct.pack('>f', self.unknown_3))
        data.write(struct.pack('>f', self.unknown_4))
        data.write(struct.pack('>f', self.unknown_5))
        data.write(struct.pack('>l', self.unknown_6))
        data.write(struct.pack('>?', self.unknown_7))
        data.write(struct.pack('>l', self.unknown_8))
        self.health_info_1.to_stream(data)
        self.health_info_2.to_stream(data)
        data.write(struct.pack('>l', self.unknown_9))
        self.prime_struct1_1.to_stream(data)
        self.prime_struct1_2.to_stream(data)
        self.prime_struct1_3.to_stream(data)
        self.prime_struct1_4.to_stream(data)
        data.write(struct.pack('>l', self.unknown_10))
        data.write(struct.pack('>l', self.unknown_11))
        self.unnamed.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("MetroidPrimeStage1Json", data)
        return cls(
            unknown_1=json_data['unknown_1'],
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            rotation=Vector.from_json(json_data['rotation']),
            scale=Vector.from_json(json_data['scale']),
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            unknown_4=json_data['unknown_4'],
            unknown_5=json_data['unknown_5'],
            unknown_6=json_data['unknown_6'],
            unknown_7=json_data['unknown_7'],
            unknown_8=json_data['unknown_8'],
            health_info_1=HealthInfo.from_json(json_data['health_info_1']),
            health_info_2=HealthInfo.from_json(json_data['health_info_2']),
            unknown_9=json_data['unknown_9'],
            prime_struct1_1=PrimeStruct1.from_json(json_data['prime_struct1_1']),
            prime_struct1_2=PrimeStruct1.from_json(json_data['prime_struct1_2']),
            prime_struct1_3=PrimeStruct1.from_json(json_data['prime_struct1_3']),
            prime_struct1_4=PrimeStruct1.from_json(json_data['prime_struct1_4']),
            unknown_10=json_data['unknown_10'],
            unknown_11=json_data['unknown_11'],
            unnamed=MassivePrimeStruct.from_json(json_data['unnamed']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_1': self.unknown_1,
            'name': self.name,
            'position': self.position.to_json(),
            'rotation': self.rotation.to_json(),
            'scale': self.scale.to_json(),
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'unknown_4': self.unknown_4,
            'unknown_5': self.unknown_5,
            'unknown_6': self.unknown_6,
            'unknown_7': self.unknown_7,
            'unknown_8': self.unknown_8,
            'health_info_1': self.health_info_1.to_json(),
            'health_info_2': self.health_info_2.to_json(),
            'unknown_9': self.unknown_9,
            'prime_struct1_1': self.prime_struct1_1.to_json(),
            'prime_struct1_2': self.prime_struct1_2.to_json(),
            'prime_struct1_3': self.prime_struct1_3.to_json(),
            'prime_struct1_4': self.prime_struct1_4.to_json(),
            'unknown_10': self.unknown_10,
            'unknown_11': self.unknown_11,
            'unnamed': self.unnamed.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.health_info_1.dependencies_for, "health_info_1", "HealthInfo"),
            (self.health_info_2.dependencies_for, "health_info_2", "HealthInfo"),
            (self.prime_struct1_1.dependencies_for, "prime_struct1_1", "PrimeStruct1"),
            (self.prime_struct1_2.dependencies_for, "prime_struct1_2", "PrimeStruct1"),
            (self.prime_struct1_3.dependencies_for, "prime_struct1_3", "PrimeStruct1"),
            (self.prime_struct1_4.dependencies_for, "prime_struct1_4", "PrimeStruct1"),
            (self.unnamed.dependencies_for, "unnamed", "MassivePrimeStruct"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for MetroidPrimeStage1.{field_name} ({field_type}): {e}"
                )
