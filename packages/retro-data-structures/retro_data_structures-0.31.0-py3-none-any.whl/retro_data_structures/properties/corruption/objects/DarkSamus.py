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
from retro_data_structures.properties.corruption.archetypes.DarkSamusData import DarkSamusData
from retro_data_structures.properties.corruption.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.corruption.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.corruption.archetypes.UnknownStruct27 import UnknownStruct27

if typing.TYPE_CHECKING:
    class DarkSamusJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_struct27: json_util.JsonObject
        dark_samus_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        dark_samus_data: json_util.JsonObject
        patterned_ai_0x1464ae05: json_util.JsonObject
        dark_samus_properties_elite_difficulty: json_util.JsonObject
        patterned_ai_0x24d00673: json_util.JsonObject
        actor_information: json_util.JsonObject
    

@dataclasses.dataclass()
class DarkSamus(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_struct27: UnknownStruct27 = dataclasses.field(default_factory=UnknownStruct27, metadata={
        'reflection': FieldReflection[UnknownStruct27](
            UnknownStruct27, id=0x0214a7eb, original_name='UnknownStruct27', from_json=UnknownStruct27.from_json, to_json=UnknownStruct27.to_json
        ),
    })
    dark_samus_properties: DarkSamusData = dataclasses.field(default_factory=DarkSamusData, metadata={
        'reflection': FieldReflection[DarkSamusData](
            DarkSamusData, id=0x02c43c41, original_name='DarkSamusProperties', from_json=DarkSamusData.from_json, to_json=DarkSamusData.to_json
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    dark_samus_data: DarkSamusData = dataclasses.field(default_factory=DarkSamusData, metadata={
        'reflection': FieldReflection[DarkSamusData](
            DarkSamusData, id=0xdd042fe0, original_name='DarkSamusData', from_json=DarkSamusData.from_json, to_json=DarkSamusData.to_json
        ),
    })
    patterned_ai_0x1464ae05: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x1464ae05, original_name='PatternedAI', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    dark_samus_properties_elite_difficulty: DarkSamusData = dataclasses.field(default_factory=DarkSamusData, metadata={
        'reflection': FieldReflection[DarkSamusData](
            DarkSamusData, id=0xd0621c92, original_name='DarkSamusPropertiesEliteDifficulty', from_json=DarkSamusData.from_json, to_json=DarkSamusData.to_json
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
        return 'DRKS'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_DarkSamus.rso']

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
        assert property_id == 0x0214a7eb
        unknown_struct27 = UnknownStruct27.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02c43c41
        dark_samus_properties = DarkSamusData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdd042fe0
        dark_samus_data = DarkSamusData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1464ae05
        patterned_ai_0x1464ae05 = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd0621c92
        dark_samus_properties_elite_difficulty = DarkSamusData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24d00673
        patterned_ai_0x24d00673 = PatternedAITypedef.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        return cls(editor_properties, unknown_struct27, dark_samus_properties, patterned, dark_samus_data, patterned_ai_0x1464ae05, dark_samus_properties_elite_difficulty, patterned_ai_0x24d00673, actor_information)

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

        data.write(b'\x02\x14\xa7\xeb')  # 0x214a7eb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct27.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x02\xc4<A')  # 0x2c43c41
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dark_samus_properties.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdd\x04/\xe0')  # 0xdd042fe0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dark_samus_data.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x14d\xae\x05')  # 0x1464ae05
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x1464ae05.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd0b\x1c\x92')  # 0xd0621c92
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dark_samus_properties_elite_difficulty.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'$\xd0\x06s')  # 0x24d00673
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x24d00673.to_stream(data)
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
        json_data = typing.cast("DarkSamusJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_struct27=UnknownStruct27.from_json(json_data['unknown_struct27']),
            dark_samus_properties=DarkSamusData.from_json(json_data['dark_samus_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            dark_samus_data=DarkSamusData.from_json(json_data['dark_samus_data']),
            patterned_ai_0x1464ae05=PatternedAITypedef.from_json(json_data['patterned_ai_0x1464ae05']),
            dark_samus_properties_elite_difficulty=DarkSamusData.from_json(json_data['dark_samus_properties_elite_difficulty']),
            patterned_ai_0x24d00673=PatternedAITypedef.from_json(json_data['patterned_ai_0x24d00673']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_struct27': self.unknown_struct27.to_json(),
            'dark_samus_properties': self.dark_samus_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'dark_samus_data': self.dark_samus_data.to_json(),
            'patterned_ai_0x1464ae05': self.patterned_ai_0x1464ae05.to_json(),
            'dark_samus_properties_elite_difficulty': self.dark_samus_properties_elite_difficulty.to_json(),
            'patterned_ai_0x24d00673': self.patterned_ai_0x24d00673.to_json(),
            'actor_information': self.actor_information.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x214a7eb: ('unknown_struct27', UnknownStruct27.from_stream),
    0x2c43c41: ('dark_samus_properties', DarkSamusData.from_stream),
    0xb3774750: ('patterned', PatternedAITypedef.from_stream),
    0xdd042fe0: ('dark_samus_data', DarkSamusData.from_stream),
    0x1464ae05: ('patterned_ai_0x1464ae05', PatternedAITypedef.from_stream),
    0xd0621c92: ('dark_samus_properties_elite_difficulty', DarkSamusData.from_stream),
    0x24d00673: ('patterned_ai_0x24d00673', PatternedAITypedef.from_stream),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
}
