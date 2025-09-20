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
from retro_data_structures.properties.corruption.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.corruption.archetypes.RundasData import RundasData
from retro_data_structures.properties.corruption.archetypes.UnknownStruct55 import UnknownStruct55

if typing.TYPE_CHECKING:
    class RundasJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_struct55: json_util.JsonObject
        rundas_data_0x9d90d49f: json_util.JsonObject
        patterned: json_util.JsonObject
        rundas_data_0x877b2ce9: json_util.JsonObject
        patterned_ai_0x1464ae05: json_util.JsonObject
        rundas_data_0xce6183d8: json_util.JsonObject
        patterned_ai_0x24d00673: json_util.JsonObject
        actor_information: json_util.JsonObject
    

@dataclasses.dataclass()
class Rundas(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_struct55: UnknownStruct55 = dataclasses.field(default_factory=UnknownStruct55, metadata={
        'reflection': FieldReflection[UnknownStruct55](
            UnknownStruct55, id=0xa6790709, original_name='UnknownStruct55', from_json=UnknownStruct55.from_json, to_json=UnknownStruct55.to_json
        ),
    })
    rundas_data_0x9d90d49f: RundasData = dataclasses.field(default_factory=RundasData, metadata={
        'reflection': FieldReflection[RundasData](
            RundasData, id=0x9d90d49f, original_name='RundasData', from_json=RundasData.from_json, to_json=RundasData.to_json
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    rundas_data_0x877b2ce9: RundasData = dataclasses.field(default_factory=RundasData, metadata={
        'reflection': FieldReflection[RundasData](
            RundasData, id=0x877b2ce9, original_name='RundasData', from_json=RundasData.from_json, to_json=RundasData.to_json
        ),
    })
    patterned_ai_0x1464ae05: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x1464ae05, original_name='PatternedAI', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    rundas_data_0xce6183d8: RundasData = dataclasses.field(default_factory=RundasData, metadata={
        'reflection': FieldReflection[RundasData](
            RundasData, id=0xce6183d8, original_name='RundasData', from_json=RundasData.from_json, to_json=RundasData.to_json
        ),
    })
    patterned_ai_0x24d00673: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x24d00673, original_name='PatternedAI', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    actor_information: ActorParameters = dataclasses.field(default_factory=ActorParameters, metadata={
        'reflection': FieldReflection[ActorParameters](
            ActorParameters, id=0x7e397fed, original_name='ActorInformation', from_json=ActorParameters.from_json, to_json=ActorParameters.to_json
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
        return 'RUND'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_Rundas.rso']

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
        if property_count != 9:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa6790709
        unknown_struct55 = UnknownStruct55.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9d90d49f
        rundas_data_0x9d90d49f = RundasData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x877b2ce9
        rundas_data_0x877b2ce9 = RundasData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1464ae05
        patterned_ai_0x1464ae05 = PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce6183d8
        rundas_data_0xce6183d8 = RundasData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24d00673
        patterned_ai_0x24d00673 = PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        return cls(editor_properties, unknown_struct55, rundas_data_0x9d90d49f, patterned, rundas_data_0x877b2ce9, patterned_ai_0x1464ae05, rundas_data_0xce6183d8, patterned_ai_0x24d00673, actor_information)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\t')  # 9 properties

        data.write(b'%ZE\x80')  # 0x255a4580
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.editor_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa6y\x07\t')  # 0xa6790709
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct55.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9d\x90\xd4\x9f')  # 0x9d90d49f
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rundas_data_0x9d90d49f.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'leash_radius': 100.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x87{,\xe9')  # 0x877b2ce9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rundas_data_0x877b2ce9.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x14d\xae\x05')  # 0x1464ae05
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x1464ae05.to_stream(data, default_override={'leash_radius': 100.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcea\x83\xd8')  # 0xce6183d8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.rundas_data_0xce6183d8.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'$\xd0\x06s')  # 0x24d00673
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x24d00673.to_stream(data, default_override={'leash_radius': 100.0})
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

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("RundasJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_struct55=UnknownStruct55.from_json(json_data['unknown_struct55']),
            rundas_data_0x9d90d49f=RundasData.from_json(json_data['rundas_data_0x9d90d49f']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            rundas_data_0x877b2ce9=RundasData.from_json(json_data['rundas_data_0x877b2ce9']),
            patterned_ai_0x1464ae05=PatternedAITypedef.from_json(json_data['patterned_ai_0x1464ae05']),
            rundas_data_0xce6183d8=RundasData.from_json(json_data['rundas_data_0xce6183d8']),
            patterned_ai_0x24d00673=PatternedAITypedef.from_json(json_data['patterned_ai_0x24d00673']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_struct55': self.unknown_struct55.to_json(),
            'rundas_data_0x9d90d49f': self.rundas_data_0x9d90d49f.to_json(),
            'patterned': self.patterned.to_json(),
            'rundas_data_0x877b2ce9': self.rundas_data_0x877b2ce9.to_json(),
            'patterned_ai_0x1464ae05': self.patterned_ai_0x1464ae05.to_json(),
            'rundas_data_0xce6183d8': self.rundas_data_0xce6183d8.to_json(),
            'patterned_ai_0x24d00673': self.patterned_ai_0x24d00673.to_json(),
            'actor_information': self.actor_information.to_json(),
        }


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0})


def _decode_patterned_ai_0x1464ae05(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0})


def _decode_patterned_ai_0x24d00673(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'leash_radius': 100.0})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xa6790709: ('unknown_struct55', UnknownStruct55.from_stream),
    0x9d90d49f: ('rundas_data_0x9d90d49f', RundasData.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x877b2ce9: ('rundas_data_0x877b2ce9', RundasData.from_stream),
    0x1464ae05: ('patterned_ai_0x1464ae05', _decode_patterned_ai_0x1464ae05),
    0xce6183d8: ('rundas_data_0xce6183d8', RundasData.from_stream),
    0x24d00673: ('patterned_ai_0x24d00673', _decode_patterned_ai_0x24d00673),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
}
