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
from retro_data_structures.properties.echoes.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.echoes.archetypes.DamageInfo import DamageInfo
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class AtomicAlphaJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        bomb_weapon: int
        bomb_model: int
        bomb_damage: json_util.JsonObject
        bomb_drop_delay: float
        bomb_reappear_delay: float
        bomb_reappear_time: float
        invisible: bool
        home_while_charging: bool
    

@dataclasses.dataclass()
class AtomicAlpha(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    bomb_weapon: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x1720b91f, original_name='BombWeapon'
        ),
    })
    bomb_model: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['CMDL'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc75f9516, original_name='BombModel'
        ),
    })
    bomb_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0xb48d5fe6, original_name='BombDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    bomb_drop_delay: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x66ba009c, original_name='BombDropDelay'
        ),
    })
    bomb_reappear_delay: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x79dd66a9, original_name='BombReappearDelay'
        ),
    })
    bomb_reappear_time: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbb4284ea, original_name='BombReappearTime'
        ),
    })
    invisible: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x7017edfc, original_name='Invisible'
        ),
    })
    home_while_charging: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2639f0b9, original_name='HomeWhileCharging'
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'ATMA'

    @classmethod
    def modules(cls) -> list[str]:
        return ['AtomicAlpha.rel']

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        struct_id, size, property_count = struct.unpack(">LHH", data.read(8))
        assert struct_id == 0xFFFFFFFF
        root_size_start = data.tell() - 2

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

        assert data.tell() - root_size_start == size
        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 11:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'mass': 25.0, 'turn_speed': 720.0, 'detection_range': 5.0, 'detection_height_range': 5.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'max_attack_range': 20.0, 'damage_wait_time': 1.0, 'collision_radius': 0.5, 'collision_height': 1.5, 'creature_size': 1})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1720b91f
        bomb_weapon = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc75f9516
        bomb_model = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb48d5fe6
        bomb_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x66ba009c
        bomb_drop_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x79dd66a9
        bomb_reappear_delay = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbb4284ea
        bomb_reappear_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7017edfc
        invisible = struct.unpack('>?', data.read(1))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2639f0b9
        home_while_charging = struct.unpack('>?', data.read(1))[0]
    
        return cls(editor_properties, patterned, actor_information, bomb_weapon, bomb_model, bomb_damage, bomb_drop_delay, bomb_reappear_delay, bomb_reappear_time, invisible, home_while_charging)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0b')  # 11 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'mass': 25.0, 'turn_speed': 720.0, 'detection_range': 5.0, 'detection_height_range': 5.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'max_attack_range': 20.0, 'damage_wait_time': 1.0, 'collision_radius': 0.5, 'collision_height': 1.5, 'creature_size': 1})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'~9\x7f\xed')  # 0x7e397fed
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.actor_information.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x17 \xb9\x1f')  # 0x1720b91f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.bomb_weapon))

        data.write(b'\xc7_\x95\x16')  # 0xc75f9516
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.bomb_model))

        data.write(b'\xb4\x8d_\xe6')  # 0xb48d5fe6
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.bomb_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'f\xba\x00\x9c')  # 0x66ba009c
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bomb_drop_delay))

        data.write(b'y\xddf\xa9')  # 0x79dd66a9
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bomb_reappear_delay))

        data.write(b'\xbbB\x84\xea')  # 0xbb4284ea
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.bomb_reappear_time))

        data.write(b'p\x17\xed\xfc')  # 0x7017edfc
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.invisible))

        data.write(b'&9\xf0\xb9')  # 0x2639f0b9
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.home_while_charging))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AtomicAlphaJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            bomb_weapon=json_data['bomb_weapon'],
            bomb_model=json_data['bomb_model'],
            bomb_damage=DamageInfo.from_json(json_data['bomb_damage']),
            bomb_drop_delay=json_data['bomb_drop_delay'],
            bomb_reappear_delay=json_data['bomb_reappear_delay'],
            bomb_reappear_time=json_data['bomb_reappear_time'],
            invisible=json_data['invisible'],
            home_while_charging=json_data['home_while_charging'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'bomb_weapon': self.bomb_weapon,
            'bomb_model': self.bomb_model,
            'bomb_damage': self.bomb_damage.to_json(),
            'bomb_drop_delay': self.bomb_drop_delay,
            'bomb_reappear_delay': self.bomb_reappear_delay,
            'bomb_reappear_time': self.bomb_reappear_time,
            'invisible': self.invisible,
            'home_while_charging': self.home_while_charging,
        }

    def _dependencies_for_bomb_weapon(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.bomb_weapon)

    def _dependencies_for_bomb_model(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.bomb_model)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_bomb_weapon, "bomb_weapon", "AssetId"),
            (self._dependencies_for_bomb_model, "bomb_model", "AssetId"),
            (self.bomb_damage.dependencies_for, "bomb_damage", "DamageInfo"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for AtomicAlpha.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'mass': 25.0, 'turn_speed': 720.0, 'detection_range': 5.0, 'detection_height_range': 5.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'max_attack_range': 20.0, 'damage_wait_time': 1.0, 'collision_radius': 0.5, 'collision_height': 1.5, 'creature_size': 1})


def _decode_bomb_weapon(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_bomb_model(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_bomb_drop_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bomb_reappear_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_bomb_reappear_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_invisible(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_home_while_charging(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x1720b91f: ('bomb_weapon', _decode_bomb_weapon),
    0xc75f9516: ('bomb_model', _decode_bomb_model),
    0xb48d5fe6: ('bomb_damage', DamageInfo.from_stream),
    0x66ba009c: ('bomb_drop_delay', _decode_bomb_drop_delay),
    0x79dd66a9: ('bomb_reappear_delay', _decode_bomb_reappear_delay),
    0xbb4284ea: ('bomb_reappear_time', _decode_bomb_reappear_time),
    0x7017edfc: ('invisible', _decode_invisible),
    0x2639f0b9: ('home_while_charging', _decode_home_while_charging),
}
