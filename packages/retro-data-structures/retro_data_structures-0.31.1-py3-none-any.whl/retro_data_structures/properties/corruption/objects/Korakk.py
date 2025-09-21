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
from retro_data_structures.properties.corruption.archetypes.KorakkData import KorakkData
from retro_data_structures.properties.corruption.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.corruption.archetypes.UnknownStruct44 import UnknownStruct44

if typing.TYPE_CHECKING:
    class KorakkJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        unknown_struct44: json_util.JsonObject
        korakk_data_0xadb462e2: json_util.JsonObject
        patterned: json_util.JsonObject
        korakk_data_0xc8e90b50: json_util.JsonObject
        patterned_ai_0x1464ae05: json_util.JsonObject
        korakk_data_0xba37072a: json_util.JsonObject
        patterned_ai_0x24d00673: json_util.JsonObject
        actor_information: json_util.JsonObject
    

@dataclasses.dataclass()
class Korakk(BaseObjectType):
    editor_properties: EditorProperties = dataclasses.field(default_factory=EditorProperties, metadata={
        'reflection': FieldReflection[EditorProperties](
            EditorProperties, id=0x255a4580, original_name='EditorProperties', from_json=EditorProperties.from_json, to_json=EditorProperties.to_json
        ),
    })
    unknown_struct44: UnknownStruct44 = dataclasses.field(default_factory=UnknownStruct44, metadata={
        'reflection': FieldReflection[UnknownStruct44](
            UnknownStruct44, id=0x85bb6891, original_name='UnknownStruct44', from_json=UnknownStruct44.from_json, to_json=UnknownStruct44.to_json
        ),
    })
    korakk_data_0xadb462e2: KorakkData = dataclasses.field(default_factory=KorakkData, metadata={
        'reflection': FieldReflection[KorakkData](
            KorakkData, id=0xadb462e2, original_name='KorakkData', from_json=KorakkData.from_json, to_json=KorakkData.to_json
        ),
    })
    patterned: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0xb3774750, original_name='Patterned', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    korakk_data_0xc8e90b50: KorakkData = dataclasses.field(default_factory=KorakkData, metadata={
        'reflection': FieldReflection[KorakkData](
            KorakkData, id=0xc8e90b50, original_name='KorakkData', from_json=KorakkData.from_json, to_json=KorakkData.to_json
        ),
    })
    patterned_ai_0x1464ae05: PatternedAITypedef = dataclasses.field(default_factory=PatternedAITypedef, metadata={
        'reflection': FieldReflection[PatternedAITypedef](
            PatternedAITypedef, id=0x1464ae05, original_name='PatternedAI', from_json=PatternedAITypedef.from_json, to_json=PatternedAITypedef.to_json
        ),
    })
    korakk_data_0xba37072a: KorakkData = dataclasses.field(default_factory=KorakkData, metadata={
        'reflection': FieldReflection[KorakkData](
            KorakkData, id=0xba37072a, original_name='KorakkData', from_json=KorakkData.from_json, to_json=KorakkData.to_json
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
        return 'KRAK'

    @classmethod
    def modules(cls) -> list[str]:
        return ['RSO_BeastRider.rso']

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
        assert property_id == 0x85bb6891
        unknown_struct44 = UnknownStruct44.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xadb462e2
        korakk_data_0xadb462e2 = KorakkData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 65.0, 'detection_range': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc8e90b50
        korakk_data_0xc8e90b50 = KorakkData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x1464ae05
        patterned_ai_0x1464ae05 = PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 65.0, 'detection_range': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xba37072a
        korakk_data_0xba37072a = KorakkData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x24d00673
        patterned_ai_0x24d00673 = PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 65.0, 'detection_range': 5.0})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        return cls(editor_properties, unknown_struct44, korakk_data_0xadb462e2, patterned, korakk_data_0xc8e90b50, patterned_ai_0x1464ae05, korakk_data_0xba37072a, patterned_ai_0x24d00673, actor_information)

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

        data.write(b'\x85\xbbh\x91')  # 0x85bb6891
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown_struct44.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xad\xb4b\xe2')  # 0xadb462e2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.korakk_data_0xadb462e2.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb3wGP')  # 0xb3774750
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned.to_stream(data, default_override={'turn_speed': 65.0, 'detection_range': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc8\xe9\x0bP')  # 0xc8e90b50
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.korakk_data_0xc8e90b50.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x14d\xae\x05')  # 0x1464ae05
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x1464ae05.to_stream(data, default_override={'turn_speed': 65.0, 'detection_range': 5.0})
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xba7\x07*')  # 0xba37072a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.korakk_data_0xba37072a.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'$\xd0\x06s')  # 0x24d00673
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.patterned_ai_0x24d00673.to_stream(data, default_override={'turn_speed': 65.0, 'detection_range': 5.0})
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
        json_data = typing.cast("KorakkJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            unknown_struct44=UnknownStruct44.from_json(json_data['unknown_struct44']),
            korakk_data_0xadb462e2=KorakkData.from_json(json_data['korakk_data_0xadb462e2']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            korakk_data_0xc8e90b50=KorakkData.from_json(json_data['korakk_data_0xc8e90b50']),
            patterned_ai_0x1464ae05=PatternedAITypedef.from_json(json_data['patterned_ai_0x1464ae05']),
            korakk_data_0xba37072a=KorakkData.from_json(json_data['korakk_data_0xba37072a']),
            patterned_ai_0x24d00673=PatternedAITypedef.from_json(json_data['patterned_ai_0x24d00673']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'unknown_struct44': self.unknown_struct44.to_json(),
            'korakk_data_0xadb462e2': self.korakk_data_0xadb462e2.to_json(),
            'patterned': self.patterned.to_json(),
            'korakk_data_0xc8e90b50': self.korakk_data_0xc8e90b50.to_json(),
            'patterned_ai_0x1464ae05': self.patterned_ai_0x1464ae05.to_json(),
            'korakk_data_0xba37072a': self.korakk_data_0xba37072a.to_json(),
            'patterned_ai_0x24d00673': self.patterned_ai_0x24d00673.to_json(),
            'actor_information': self.actor_information.to_json(),
        }


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 65.0, 'detection_range': 5.0})


def _decode_patterned_ai_0x1464ae05(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 65.0, 'detection_range': 5.0})


def _decode_patterned_ai_0x24d00673(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'turn_speed': 65.0, 'detection_range': 5.0})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0x85bb6891: ('unknown_struct44', UnknownStruct44.from_stream),
    0xadb462e2: ('korakk_data_0xadb462e2', KorakkData.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0xc8e90b50: ('korakk_data_0xc8e90b50', KorakkData.from_stream),
    0x1464ae05: ('patterned_ai_0x1464ae05', _decode_patterned_ai_0x1464ae05),
    0xba37072a: ('korakk_data_0xba37072a', KorakkData.from_stream),
    0x24d00673: ('patterned_ai_0x24d00673', _decode_patterned_ai_0x24d00673),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
}
