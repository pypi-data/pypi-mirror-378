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
from retro_data_structures.properties.echoes.archetypes.DamageVulnerability import DamageVulnerability
from retro_data_structures.properties.echoes.archetypes.EditorProperties import EditorProperties
from retro_data_structures.properties.echoes.archetypes.PatternedAITypedef import PatternedAITypedef
from retro_data_structures.properties.echoes.core.AssetId import AssetId, default_asset_id

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class AtomicBetaJson(typing_extensions.TypedDict):
        editor_properties: json_util.JsonObject
        patterned: json_util.JsonObject
        actor_information: json_util.JsonObject
        beam_effect: int
        beam: int
        beam_damage: json_util.JsonObject
        contact_fx: int
        beam_fade_time: float
        beam_radius: float
        hover_speed: float
        frozen_vulnerability: json_util.JsonObject
        normal_rotate_speed: float
        charging_rotate_speed: float
        speed_change_rate: float
        sound_0x14038b71: int
        sound_0x16a435cb: int
        sound_0x67edefc2: int
        damage_delay: float
    

@dataclasses.dataclass()
class AtomicBeta(BaseObjectType):
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
    beam_effect: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['ELSC', 'WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x05439a08, original_name='BeamEffect'
        ),
    })
    beam: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['WPSC'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0x2cbf989b, original_name='Beam'
        ),
    })
    beam_damage: DamageInfo = dataclasses.field(default_factory=DamageInfo, metadata={
        'reflection': FieldReflection[DamageInfo](
            DamageInfo, id=0x13e30e4d, original_name='BeamDamage', from_json=DamageInfo.from_json, to_json=DamageInfo.to_json
        ),
    })
    contact_fx: AssetId = dataclasses.field(default=default_asset_id, metadata={
        'asset_types': ['PART'], 'reflection': FieldReflection[AssetId](
            AssetId, id=0xc271eaf5, original_name='ContactFx'
        ),
    })
    beam_fade_time: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x18093fa8, original_name='BeamFadeTime'
        ),
    })
    beam_radius: float = dataclasses.field(default=0.10000000149011612, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcb0af075, original_name='BeamRadius'
        ),
    })
    hover_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x845ef489, original_name='HoverSpeed'
        ),
    })
    frozen_vulnerability: DamageVulnerability = dataclasses.field(default_factory=DamageVulnerability, metadata={
        'reflection': FieldReflection[DamageVulnerability](
            DamageVulnerability, id=0x411938aa, original_name='FrozenVulnerability', from_json=DamageVulnerability.from_json, to_json=DamageVulnerability.to_json
        ),
    })
    normal_rotate_speed: float = dataclasses.field(default=1.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xce1893cc, original_name='NormalRotateSpeed'
        ),
    })
    charging_rotate_speed: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6a453d89, original_name='ChargingRotateSpeed'
        ),
    })
    speed_change_rate: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xac202a5d, original_name='SpeedChangeRate'
        ),
    })
    sound_0x14038b71: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x14038b71, original_name='Sound'
        ),
    })
    sound_0x16a435cb: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x16a435cb, original_name='Sound'
        ),
    })
    sound_0x67edefc2: int = dataclasses.field(default=0, metadata={
        'sound': True, 'reflection': FieldReflection[int](
            int, id=0x67edefc2, original_name='Sound'
        ),
    })
    damage_delay: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x8f4fb79d, original_name='DamageDelay'
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
        return 'ATMB'

    @classmethod
    def modules(cls) -> list[str]:
        return ['AtomicBeta.rel']

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
        if property_count != 18:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255a4580
        editor_properties = EditorProperties.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb3774750
        patterned = PatternedAITypedef.from_stream(data, property_size, default_override={'mass': 25.0, 'turn_speed': 720.0, 'detection_range': 5.0, 'detection_height_range': 5.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'max_attack_range': 20.0, 'damage_wait_time': 1.0, 'collision_radius': 0.5, 'collision_height': 1.5})
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7e397fed
        actor_information = ActorParameters.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x05439a08
        beam_effect = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2cbf989b
        beam = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x13e30e4d
        beam_damage = DamageInfo.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc271eaf5
        contact_fx = struct.unpack(">L", data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x18093fa8
        beam_fade_time = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb0af075
        beam_radius = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x845ef489
        hover_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x411938aa
        frozen_vulnerability = DamageVulnerability.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xce1893cc
        normal_rotate_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6a453d89
        charging_rotate_speed = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xac202a5d
        speed_change_rate = struct.unpack('>f', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x14038b71
        sound_0x14038b71 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x16a435cb
        sound_0x16a435cb = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x67edefc2
        sound_0x67edefc2 = struct.unpack('>l', data.read(4))[0]
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8f4fb79d
        damage_delay = struct.unpack('>f', data.read(4))[0]
    
        return cls(editor_properties, patterned, actor_information, beam_effect, beam, beam_damage, contact_fx, beam_fade_time, beam_radius, hover_speed, frozen_vulnerability, normal_rotate_speed, charging_rotate_speed, speed_change_rate, sound_0x14038b71, sound_0x16a435cb, sound_0x67edefc2, damage_delay)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x12')  # 18 properties

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
        self.patterned.to_stream(data, default_override={'mass': 25.0, 'turn_speed': 720.0, 'detection_range': 5.0, 'detection_height_range': 5.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'max_attack_range': 20.0, 'damage_wait_time': 1.0, 'collision_radius': 0.5, 'collision_height': 1.5})
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

        data.write(b'\x05C\x9a\x08')  # 0x5439a08
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.beam_effect))

        data.write(b',\xbf\x98\x9b')  # 0x2cbf989b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.beam))

        data.write(b'\x13\xe3\x0eM')  # 0x13e30e4d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_damage.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc2q\xea\xf5')  # 0xc271eaf5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack(">L", self.contact_fx))

        data.write(b'\x18\t?\xa8')  # 0x18093fa8
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.beam_fade_time))

        data.write(b'\xcb\n\xf0u')  # 0xcb0af075
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.beam_radius))

        data.write(b'\x84^\xf4\x89')  # 0x845ef489
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.hover_speed))

        data.write(b'A\x198\xaa')  # 0x411938aa
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.frozen_vulnerability.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xce\x18\x93\xcc')  # 0xce1893cc
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.normal_rotate_speed))

        data.write(b'jE=\x89')  # 0x6a453d89
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.charging_rotate_speed))

        data.write(b'\xac *]')  # 0xac202a5d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.speed_change_rate))

        data.write(b'\x14\x03\x8bq')  # 0x14038b71
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x14038b71))

        data.write(b'\x16\xa45\xcb')  # 0x16a435cb
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x16a435cb))

        data.write(b'g\xed\xef\xc2')  # 0x67edefc2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>l', self.sound_0x67edefc2))

        data.write(b'\x8fO\xb7\x9d')  # 0x8f4fb79d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.damage_delay))

        struct_end_offset = data.tell()
        data.seek(root_size_offset)
        data.write(struct.pack(">H", struct_end_offset - root_size_offset - 2))
        data.seek(struct_end_offset)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("AtomicBetaJson", data)
        return cls(
            editor_properties=EditorProperties.from_json(json_data['editor_properties']),
            patterned=PatternedAITypedef.from_json(json_data['patterned']),
            actor_information=ActorParameters.from_json(json_data['actor_information']),
            beam_effect=json_data['beam_effect'],
            beam=json_data['beam'],
            beam_damage=DamageInfo.from_json(json_data['beam_damage']),
            contact_fx=json_data['contact_fx'],
            beam_fade_time=json_data['beam_fade_time'],
            beam_radius=json_data['beam_radius'],
            hover_speed=json_data['hover_speed'],
            frozen_vulnerability=DamageVulnerability.from_json(json_data['frozen_vulnerability']),
            normal_rotate_speed=json_data['normal_rotate_speed'],
            charging_rotate_speed=json_data['charging_rotate_speed'],
            speed_change_rate=json_data['speed_change_rate'],
            sound_0x14038b71=json_data['sound_0x14038b71'],
            sound_0x16a435cb=json_data['sound_0x16a435cb'],
            sound_0x67edefc2=json_data['sound_0x67edefc2'],
            damage_delay=json_data['damage_delay'],
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'editor_properties': self.editor_properties.to_json(),
            'patterned': self.patterned.to_json(),
            'actor_information': self.actor_information.to_json(),
            'beam_effect': self.beam_effect,
            'beam': self.beam,
            'beam_damage': self.beam_damage.to_json(),
            'contact_fx': self.contact_fx,
            'beam_fade_time': self.beam_fade_time,
            'beam_radius': self.beam_radius,
            'hover_speed': self.hover_speed,
            'frozen_vulnerability': self.frozen_vulnerability.to_json(),
            'normal_rotate_speed': self.normal_rotate_speed,
            'charging_rotate_speed': self.charging_rotate_speed,
            'speed_change_rate': self.speed_change_rate,
            'sound_0x14038b71': self.sound_0x14038b71,
            'sound_0x16a435cb': self.sound_0x16a435cb,
            'sound_0x67edefc2': self.sound_0x67edefc2,
            'damage_delay': self.damage_delay,
        }

    def _dependencies_for_beam_effect(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.beam_effect)

    def _dependencies_for_beam(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.beam)

    def _dependencies_for_contact_fx(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_dependencies_for_asset(self.contact_fx)

    def _dependencies_for_sound_0x14038b71(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x14038b71)

    def _dependencies_for_sound_0x16a435cb(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x16a435cb)

    def _dependencies_for_sound_0x67edefc2(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from asset_manager.get_audio_group_dependency(self.sound_0x67edefc2)

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.editor_properties.dependencies_for, "editor_properties", "EditorProperties"),
            (self.patterned.dependencies_for, "patterned", "PatternedAITypedef"),
            (self.actor_information.dependencies_for, "actor_information", "ActorParameters"),
            (self._dependencies_for_beam_effect, "beam_effect", "AssetId"),
            (self._dependencies_for_beam, "beam", "AssetId"),
            (self.beam_damage.dependencies_for, "beam_damage", "DamageInfo"),
            (self._dependencies_for_contact_fx, "contact_fx", "AssetId"),
            (self.frozen_vulnerability.dependencies_for, "frozen_vulnerability", "DamageVulnerability"),
            (self._dependencies_for_sound_0x14038b71, "sound_0x14038b71", "int"),
            (self._dependencies_for_sound_0x16a435cb, "sound_0x16a435cb", "int"),
            (self._dependencies_for_sound_0x67edefc2, "sound_0x67edefc2", "int"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for AtomicBeta.{field_name} ({field_type}): {e}"
                )


def _decode_patterned(data: typing.BinaryIO, property_size: int) -> PatternedAITypedef:
    return PatternedAITypedef.from_stream(data, property_size, default_override={'mass': 25.0, 'turn_speed': 720.0, 'detection_range': 5.0, 'detection_height_range': 5.0, 'detection_angle': 90.0, 'min_attack_range': 4.0, 'max_attack_range': 20.0, 'damage_wait_time': 1.0, 'collision_radius': 0.5, 'collision_height': 1.5})


def _decode_beam_effect(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_beam(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_contact_fx(data: typing.BinaryIO, property_size: int) -> AssetId:
    return struct.unpack(">L", data.read(4))[0]


def _decode_beam_fade_time(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_beam_radius(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_hover_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_normal_rotate_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_charging_rotate_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_speed_change_rate(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_sound_0x14038b71(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x16a435cb(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_sound_0x67edefc2(data: typing.BinaryIO, property_size: int) -> int:
    return struct.unpack('>l', data.read(4))[0]


def _decode_damage_delay(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x255a4580: ('editor_properties', EditorProperties.from_stream),
    0xb3774750: ('patterned', _decode_patterned),
    0x7e397fed: ('actor_information', ActorParameters.from_stream),
    0x5439a08: ('beam_effect', _decode_beam_effect),
    0x2cbf989b: ('beam', _decode_beam),
    0x13e30e4d: ('beam_damage', DamageInfo.from_stream),
    0xc271eaf5: ('contact_fx', _decode_contact_fx),
    0x18093fa8: ('beam_fade_time', _decode_beam_fade_time),
    0xcb0af075: ('beam_radius', _decode_beam_radius),
    0x845ef489: ('hover_speed', _decode_hover_speed),
    0x411938aa: ('frozen_vulnerability', DamageVulnerability.from_stream),
    0xce1893cc: ('normal_rotate_speed', _decode_normal_rotate_speed),
    0x6a453d89: ('charging_rotate_speed', _decode_charging_rotate_speed),
    0xac202a5d: ('speed_change_rate', _decode_speed_change_rate),
    0x14038b71: ('sound_0x14038b71', _decode_sound_0x14038b71),
    0x16a435cb: ('sound_0x16a435cb', _decode_sound_0x16a435cb),
    0x67edefc2: ('sound_0x67edefc2', _decode_sound_0x67edefc2),
    0x8f4fb79d: ('damage_delay', _decode_damage_delay),
}
