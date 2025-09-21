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
from retro_data_structures.properties.prime.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.prime.archetypes.GuessStruct import GuessStruct
from retro_data_structures.properties.prime.core.AssetId import AssetId, default_asset_id
from retro_data_structures.properties.prime.core.Vector import Vector

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class SteamJson(typing_extensions.TypedDict):
        name: str
        position: json_util.JsonValue
        scale: json_util.JsonValue
        unnamed: json_util.JsonObject
        unknown_1: json_util.JsonValue
        unknown_2: int
        unknown_3: bool
        texture: int
        guess_struct_1: json_util.JsonObject
        guess_struct_2: json_util.JsonObject
        unknown_8: bool
    

@dataclasses.dataclass()
class Steam(BaseObjectType):
    name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x00000000, original_name='Name'
        ),
    })
    position: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000001, original_name='Position', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    scale: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000002, original_name='Scale', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unnamed: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x00000003, original_name='3', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    unknown_1: Vector = dataclasses.field(default_factory=Vector, metadata={
        'reflection': FieldReflection[Vector](
            Vector, id=0x00000004, original_name='Unknown 1', from_json=Vector.from_json, to_json=Vector.to_json
        ),
    })
    unknown_2: int = dataclasses.field(default=0, metadata={
        'reflection': FieldReflection[int](
            int, id=0x00000005, original_name='Unknown 2'
        ),
    })
    unknown_3: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x00000006, original_name='Unknown 3'
        ),
    })
    texture: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['TXTR'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x00000007, original_name='Texture'
        ),
    })
    guess_struct_1: GuessStruct = dataclasses.field(default_factory=GuessStruct, metadata={
        'reflection': FieldReflection[GuessStruct](
            GuessStruct, id=0x00000008, original_name='GuessStruct 1', from_json=GuessStruct.from_json, to_json=GuessStruct.to_json
        ),
    })
    guess_struct_2: GuessStruct = dataclasses.field(default_factory=GuessStruct, metadata={
        'reflection': FieldReflection[GuessStruct](
            GuessStruct, id=0x00000009, original_name='GuessStruct 2', from_json=GuessStruct.from_json, to_json=GuessStruct.to_json
        ),
    })
    unknown_8: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x0000000a, original_name='Unknown 8'
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
        return 0x46

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_size = None  # Atomic
        property_count = struct.unpack(">L", data.read(4))[0]
        name = b"".join(iter(lambda: data.read(1), b'\x00')).decode("utf-8")
        position = Vector.from_stream(data)
        scale = Vector.from_stream(data)
        unnamed = DamageInfo.from_stream(data, property_size)
        unknown_1 = Vector.from_stream(data)
        unknown_2 = struct.unpack('>l', data.read(4))[0]
        unknown_3 = struct.unpack('>?', data.read(1))[0]
        texture = struct.unpack(">L", data.read(4))[0]
        guess_struct_1 = GuessStruct.from_stream(data, property_size)
        guess_struct_2 = GuessStruct.from_stream(data, property_size)
        unknown_8 = struct.unpack('>?', data.read(1))[0]
        return cls(name, position, scale, unnamed, unknown_1, unknown_2, unknown_3, texture, guess_struct_1, guess_struct_2, unknown_8)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x00\x00\x0b')  # 11 properties
        data.write(self.name.encode("utf-8"))
        data.write(b'\x00')
        self.position.to_stream(data)
        self.scale.to_stream(data)
        self.unnamed.to_stream(data)
        self.unknown_1.to_stream(data)
        data.write(struct.pack('>l', self.unknown_2))
        data.write(struct.pack('>?', self.unknown_3))
        data.write(struct.pack(">L", self.texture))
        self.guess_struct_1.to_stream(data)
        self.guess_struct_2.to_stream(data)
        data.write(struct.pack('>?', self.unknown_8))

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SteamJson", data)
        return cls(
            name=json_data['name'],
            position=Vector.from_json(json_data['position']),
            scale=Vector.from_json(json_data['scale']),
            unnamed=DamageInfo.from_json(json_data['unnamed']),
            unknown_1=Vector.from_json(json_data['unknown_1']),
            unknown_2=json_data['unknown_2'],
            unknown_3=json_data['unknown_3'],
            texture=json_data['texture'],
            guess_struct_1=GuessStruct.from_json(json_data['guess_struct_1']),
            guess_struct_2=GuessStruct.from_json(json_data['guess_struct_2']),
            unknown_8=json_data['unknown_8'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'name': self.name,
            'position': self.position.to_json(),
            'scale': self.scale.to_json(),
            'unnamed': self.unnamed.to_json(),
            'unknown_1': self.unknown_1.to_json(),
            'unknown_2': self.unknown_2,
            'unknown_3': self.unknown_3,
            'texture': self.texture,
            'guess_struct_1': self.guess_struct_1.to_json(),
            'guess_struct_2': self.guess_struct_2.to_json(),
            'unknown_8': self.unknown_8,
        }

    def _dependencies_for_texture(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.texture)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.unnamed.dependencies_for, "unnamed", "DamageInfo"),
            (self._dependencies_for_texture, "texture", "AssetId"),
            (self.guess_struct_1.dependencies_for, "guess_struct_1", "GuessStruct"),
            (self.guess_struct_2.dependencies_for, "guess_struct_2", "GuessStruct"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for Steam.{field_name} ({field_type}): {e}"
                )
