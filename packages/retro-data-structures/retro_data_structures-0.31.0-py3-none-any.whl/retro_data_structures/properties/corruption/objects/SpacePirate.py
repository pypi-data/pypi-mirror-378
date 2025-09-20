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
from retro_data_structures.properties.corruption.archetypes.ActorParameters import ActorParameters
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.FriendlyData import FriendlyData
from retro_data_structures.properties.corruption.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.corruption.archetypes.SpacePirateData import SpacePirateData

if typing.TYPE_CHECKING:
    class SpacePirateJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        actor_information: json_util.JsonObject
        patterned_info: json_util.JsonObject
        friendly_data: json_util.JsonObject
        space_pirate_info: json_util.JsonObject
    

@dataclasses.dataclass()
class SpacePirate(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
        ),
    })
    patterned_info: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x43bbb1dd, original_name='PatternedInfo', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    friendly_data: FriendlyData = dataclasses.field(default_factory=FriendlyData, metadata={
        'reflection': FieldReflection[FriendlyData](
            FriendlyData, id=0xe677af2c, original_name='FriendlyData', from_json=FriendlyData.from_json, to_json=FriendlyData.to_json
        ),
    })
    space_pirate_info: SpacePirateData = dataclasses.field(default_factory=SpacePirateData, metadata={
        'reflection': FieldReflection[SpacePirateData](
            SpacePirateData, id=0xdda1cace, original_name='SpacePirateInfo', from_json=SpacePirateData.from_json, to_json=SpacePirateData.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    def get_name(self) -> str | None:
        return self.editor_properties.name

    def set_name(self, name: str) -> None:
        self.editor_properties.name = name

    @classmethod
    def object_type(cls) -> str:
        return 'PIRT'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_SpacePirate.rso']

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
        if property_count != 5:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x43bbb1dd
        patterned_info = PatternedAITypedef.from_stream(data, property_size, default_override={'damage_wait_time': 3.0, 'collision_radius': 0.800000011920929, 'collision_height': 4.5, 'step_up_height': 0.30000001192092896, 'creature_size': 1, 'turn_speed': 360.0, 'detection_range': 50.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'average_attack_time': 1.0, 'attack_time_variation': 0.5})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe677af2c
        friendly_data = FriendlyData.from_stream(data, property_size, default_override={'is_grabbable': True})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdda1cace
        space_pirate_info = SpacePirateData.from_stream(data, property_size)
    
        return cls(editor_properties, actor_information, patterned_info, friendly_data, space_pirate_info)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x05')  # 5 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
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

        data.write(b'C\xbb\xb1\xdd')  # 0x43bbb1dd
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_info.to_stream(data, default_override={'damage_wait_time': 3.0, 'collision_radius': 0.800000011920929, 'collision_height': 4.5, 'step_up_height': 0.30000001192092896, 'creature_size': 1, 'turn_speed': 360.0, 'detection_range': 50.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'average_attack_time': 1.0, 'attack_time_variation': 0.5})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe6w\xaf,')  # 0xe677af2c
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.friendly_data.to_stream(data, default_override={'is_grabbable': True})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdd\xa1\xca\xce')  # 0xdda1cace
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.space_pirate_info.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("SpacePirateJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            patterned_info=PatternedAITypedef.from_json(json_data['patterned_info']),
            friendly_data=FriendlyData.from_json(json_data['friendly_data']),
            space_pirate_info=SpacePirateData.from_json(json_data['space_pirate_info']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'actor_information': self.actor_information.to_json(),
            'patterned_info': self.patterned_info.to_json(),
            'friendly_data': self.friendly_data.to_json(),
            'space_pirate_info': self.space_pirate_info.to_json(),
        }


def _decode_patterned_info(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'damage_wait_time': 3.0, 'collision_radius': 0.800000011920929, 'collision_height': 4.5, 'step_up_height': 0.30000001192092896, 'creature_size': 1, 'turn_speed': 360.0, 'detection_range': 50.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'average_attack_time': 1.0, 'attack_time_variation': 0.5})


def _decode_friendly_data(data: typing.BinaryIO, property_size: int) -> FriendlyData:
    return FriendlyData.from_stream(data, property_size, default_override={'is_grabbable': True})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x43bbb1dd: ('patterned_info', _decode_patterned_info),
    0xe677af2c: ('friendly_data', _decode_friendly_data),
    0xdda1cace: ('space_pirate_info', SpacePirateData.from_stream),
}
