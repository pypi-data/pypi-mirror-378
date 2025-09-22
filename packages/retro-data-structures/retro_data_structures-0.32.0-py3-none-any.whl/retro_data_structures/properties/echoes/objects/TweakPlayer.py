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
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_AimStuff import TweakPlayer_AimStuff
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_Collision import TweakPlayer_Collision
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_DarkWorld import TweakPlayer_DarkWorld
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_FirstPersonCamera import TweakPlayer_FirstPersonCamera
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_Frozen import TweakPlayer_Frozen
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_Grapple import TweakPlayer_Grapple
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_GrappleBeam import TweakPlayer_GrappleBeam
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_Misc import TweakPlayer_Misc
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_Motion import TweakPlayer_Motion
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_Orbit import TweakPlayer_Orbit
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_ScanVisor import TweakPlayer_ScanVisor
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_Shield import TweakPlayer_Shield
from retro_data_structures.properties.echoes.archetypes.TweakPlayer_SuitDamageReduction import TweakPlayer_SuitDamageReduction

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakPlayerJson(typing_extensions.TypedDict):
        instance_name: str
        dark_world: json_util.JsonObject
        grapple_beam: json_util.JsonObject
        motion: json_util.JsonObject
        misc: json_util.JsonObject
        aim_stuff: json_util.JsonObject
        orbit: json_util.JsonObject
        scan_visor: json_util.JsonObject
        grapple: json_util.JsonObject
        collision: json_util.JsonObject
        first_person_camera: json_util.JsonObject
        shield: json_util.JsonObject
        frozen: json_util.JsonObject
        suit_damage_reduction: json_util.JsonObject
    

@dataclasses.dataclass()
class TweakPlayer(BaseObjectType):
    instance_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x7fda1466, original_name='InstanceName'
        ),
    })
    dark_world: TweakPlayer_DarkWorld = dataclasses.field(default_factory=TweakPlayer_DarkWorld, metadata={
        'reflection': FieldReflection[TweakPlayer_DarkWorld](
            TweakPlayer_DarkWorld, id=0xdfd08eba, original_name='DarkWorld', from_json=TweakPlayer_DarkWorld.from_json, to_json=TweakPlayer_DarkWorld.to_json
        ),
    })
    grapple_beam: TweakPlayer_GrappleBeam = dataclasses.field(default_factory=TweakPlayer_GrappleBeam, metadata={
        'reflection': FieldReflection[TweakPlayer_GrappleBeam](
            TweakPlayer_GrappleBeam, id=0x45171a96, original_name='GrappleBeam', from_json=TweakPlayer_GrappleBeam.from_json, to_json=TweakPlayer_GrappleBeam.to_json
        ),
    })
    motion: TweakPlayer_Motion = dataclasses.field(default_factory=TweakPlayer_Motion, metadata={
        'reflection': FieldReflection[TweakPlayer_Motion](
            TweakPlayer_Motion, id=0x82cf4cf1, original_name='Motion', from_json=TweakPlayer_Motion.from_json, to_json=TweakPlayer_Motion.to_json
        ),
    })
    misc: TweakPlayer_Misc = dataclasses.field(default_factory=TweakPlayer_Misc, metadata={
        'reflection': FieldReflection[TweakPlayer_Misc](
            TweakPlayer_Misc, id=0x56a720c8, original_name='Misc', from_json=TweakPlayer_Misc.from_json, to_json=TweakPlayer_Misc.to_json
        ),
    })
    aim_stuff: TweakPlayer_AimStuff = dataclasses.field(default_factory=TweakPlayer_AimStuff, metadata={
        'reflection': FieldReflection[TweakPlayer_AimStuff](
            TweakPlayer_AimStuff, id=0x42a17438, original_name='AimStuff', from_json=TweakPlayer_AimStuff.from_json, to_json=TweakPlayer_AimStuff.to_json
        ),
    })
    orbit: TweakPlayer_Orbit = dataclasses.field(default_factory=TweakPlayer_Orbit, metadata={
        'reflection': FieldReflection[TweakPlayer_Orbit](
            TweakPlayer_Orbit, id=0x243ae038, original_name='Orbit', from_json=TweakPlayer_Orbit.from_json, to_json=TweakPlayer_Orbit.to_json
        ),
    })
    scan_visor: TweakPlayer_ScanVisor = dataclasses.field(default_factory=TweakPlayer_ScanVisor, metadata={
        'reflection': FieldReflection[TweakPlayer_ScanVisor](
            TweakPlayer_ScanVisor, id=0x20124c3d, original_name='ScanVisor', from_json=TweakPlayer_ScanVisor.from_json, to_json=TweakPlayer_ScanVisor.to_json
        ),
    })
    grapple: TweakPlayer_Grapple = dataclasses.field(default_factory=TweakPlayer_Grapple, metadata={
        'reflection': FieldReflection[TweakPlayer_Grapple](
            TweakPlayer_Grapple, id=0x30412440, original_name='Grapple', from_json=TweakPlayer_Grapple.from_json, to_json=TweakPlayer_Grapple.to_json
        ),
    })
    collision: TweakPlayer_Collision = dataclasses.field(default_factory=TweakPlayer_Collision, metadata={
        'reflection': FieldReflection[TweakPlayer_Collision](
            TweakPlayer_Collision, id=0xc4d32ae5, original_name='Collision', from_json=TweakPlayer_Collision.from_json, to_json=TweakPlayer_Collision.to_json
        ),
    })
    first_person_camera: TweakPlayer_FirstPersonCamera = dataclasses.field(default_factory=TweakPlayer_FirstPersonCamera, metadata={
        'reflection': FieldReflection[TweakPlayer_FirstPersonCamera](
            TweakPlayer_FirstPersonCamera, id=0xd6155d4b, original_name='FirstPersonCamera', from_json=TweakPlayer_FirstPersonCamera.from_json, to_json=TweakPlayer_FirstPersonCamera.to_json
        ),
    })
    shield: TweakPlayer_Shield = dataclasses.field(default_factory=TweakPlayer_Shield, metadata={
        'reflection': FieldReflection[TweakPlayer_Shield](
            TweakPlayer_Shield, id=0xbcca767e, original_name='Shield', from_json=TweakPlayer_Shield.from_json, to_json=TweakPlayer_Shield.to_json
        ),
    })
    frozen: TweakPlayer_Frozen = dataclasses.field(default_factory=TweakPlayer_Frozen, metadata={
        'reflection': FieldReflection[TweakPlayer_Frozen](
            TweakPlayer_Frozen, id=0x4d3b20b7, original_name='Frozen', from_json=TweakPlayer_Frozen.from_json, to_json=TweakPlayer_Frozen.to_json
        ),
    })
    suit_damage_reduction: TweakPlayer_SuitDamageReduction = dataclasses.field(default_factory=TweakPlayer_SuitDamageReduction, metadata={
        'reflection': FieldReflection[TweakPlayer_SuitDamageReduction](
            TweakPlayer_SuitDamageReduction, id=0xaeaff210, original_name='SuitDamageReduction', from_json=TweakPlayer_SuitDamageReduction.from_json, to_json=TweakPlayer_SuitDamageReduction.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

    def get_name(self) -> str | None:
        return None

    def set_name(self, name: str) -> None:
        raise RuntimeError(f"{self.__class__.__name__} does not have name")

    @classmethod
    def object_type(cls) -> str:
        return 'TWPL'

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
        if property_count != 14:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fda1466
        instance_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xdfd08eba
        dark_world = TweakPlayer_DarkWorld.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x45171a96
        grapple_beam = TweakPlayer_GrappleBeam.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x82cf4cf1
        motion = TweakPlayer_Motion.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x56a720c8
        misc = TweakPlayer_Misc.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x42a17438
        aim_stuff = TweakPlayer_AimStuff.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x243ae038
        orbit = TweakPlayer_Orbit.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x20124c3d
        scan_visor = TweakPlayer_ScanVisor.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x30412440
        grapple = TweakPlayer_Grapple.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xc4d32ae5
        collision = TweakPlayer_Collision.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd6155d4b
        first_person_camera = TweakPlayer_FirstPersonCamera.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbcca767e
        shield = TweakPlayer_Shield.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4d3b20b7
        frozen = TweakPlayer_Frozen.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaeaff210
        suit_damage_reduction = TweakPlayer_SuitDamageReduction.from_stream(data, property_size)
    
        return cls(instance_name, dark_world, grapple_beam, motion, misc, aim_stuff, orbit, scan_visor, grapple, collision, first_person_camera, shield, frozen, suit_damage_reduction)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0e')  # 14 properties

        data.write(b'\x7f\xda\x14f')  # 0x7fda1466
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.instance_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xdf\xd0\x8e\xba')  # 0xdfd08eba
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.dark_world.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'E\x17\x1a\x96')  # 0x45171a96
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple_beam.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x82\xcfL\xf1')  # 0x82cf4cf1
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.motion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'V\xa7 \xc8')  # 0x56a720c8
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.misc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'B\xa1t8')  # 0x42a17438
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.aim_stuff.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'$:\xe08')  # 0x243ae038
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.orbit.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b' \x12L=')  # 0x20124c3d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.scan_visor.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'0A$@')  # 0x30412440
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.grapple.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xc4\xd3*\xe5')  # 0xc4d32ae5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.collision.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd6\x15]K')  # 0xd6155d4b
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.first_person_camera.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbc\xcav~')  # 0xbcca767e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.shield.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'M; \xb7')  # 0x4d3b20b7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.frozen.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xae\xaf\xf2\x10')  # 0xaeaff210
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.suit_damage_reduction.to_stream(data)
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
        json_data = typing.cast("TweakPlayerJson", data)
        return cls(
            instance_name=json_data['instance_name'],
            dark_world=TweakPlayer_DarkWorld.from_json(json_data['dark_world']),
            grapple_beam=TweakPlayer_GrappleBeam.from_json(json_data['grapple_beam']),
            motion=TweakPlayer_Motion.from_json(json_data['motion']),
            misc=TweakPlayer_Misc.from_json(json_data['misc']),
            aim_stuff=TweakPlayer_AimStuff.from_json(json_data['aim_stuff']),
            orbit=TweakPlayer_Orbit.from_json(json_data['orbit']),
            scan_visor=TweakPlayer_ScanVisor.from_json(json_data['scan_visor']),
            grapple=TweakPlayer_Grapple.from_json(json_data['grapple']),
            collision=TweakPlayer_Collision.from_json(json_data['collision']),
            first_person_camera=TweakPlayer_FirstPersonCamera.from_json(json_data['first_person_camera']),
            shield=TweakPlayer_Shield.from_json(json_data['shield']),
            frozen=TweakPlayer_Frozen.from_json(json_data['frozen']),
            suit_damage_reduction=TweakPlayer_SuitDamageReduction.from_json(json_data['suit_damage_reduction']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'instance_name': self.instance_name,
            'dark_world': self.dark_world.to_json(),
            'grapple_beam': self.grapple_beam.to_json(),
            'motion': self.motion.to_json(),
            'misc': self.misc.to_json(),
            'aim_stuff': self.aim_stuff.to_json(),
            'orbit': self.orbit.to_json(),
            'scan_visor': self.scan_visor.to_json(),
            'grapple': self.grapple.to_json(),
            'collision': self.collision.to_json(),
            'first_person_camera': self.first_person_camera.to_json(),
            'shield': self.shield.to_json(),
            'frozen': self.frozen.to_json(),
            'suit_damage_reduction': self.suit_damage_reduction.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.dark_world.dependencies_for, "dark_world", "TweakPlayer_DarkWorld"),
            (self.grapple_beam.dependencies_for, "grapple_beam", "TweakPlayer_GrappleBeam"),
            (self.motion.dependencies_for, "motion", "TweakPlayer_Motion"),
            (self.misc.dependencies_for, "misc", "TweakPlayer_Misc"),
            (self.aim_stuff.dependencies_for, "aim_stuff", "TweakPlayer_AimStuff"),
            (self.orbit.dependencies_for, "orbit", "TweakPlayer_Orbit"),
            (self.scan_visor.dependencies_for, "scan_visor", "TweakPlayer_ScanVisor"),
            (self.grapple.dependencies_for, "grapple", "TweakPlayer_Grapple"),
            (self.collision.dependencies_for, "collision", "TweakPlayer_Collision"),
            (self.first_person_camera.dependencies_for, "first_person_camera", "TweakPlayer_FirstPersonCamera"),
            (self.shield.dependencies_for, "shield", "TweakPlayer_Shield"),
            (self.frozen.dependencies_for, "frozen", "TweakPlayer_Frozen"),
            (self.suit_damage_reduction.dependencies_for, "suit_damage_reduction", "TweakPlayer_SuitDamageReduction"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakPlayer.{field_name} ({field_type}): {e}"
                )


def _decode_instance_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7fda1466: ('instance_name', _decode_instance_name),
    0xdfd08eba: ('dark_world', TweakPlayer_DarkWorld.from_stream),
    0x45171a96: ('grapple_beam', TweakPlayer_GrappleBeam.from_stream),
    0x82cf4cf1: ('motion', TweakPlayer_Motion.from_stream),
    0x56a720c8: ('misc', TweakPlayer_Misc.from_stream),
    0x42a17438: ('aim_stuff', TweakPlayer_AimStuff.from_stream),
    0x243ae038: ('orbit', TweakPlayer_Orbit.from_stream),
    0x20124c3d: ('scan_visor', TweakPlayer_ScanVisor.from_stream),
    0x30412440: ('grapple', TweakPlayer_Grapple.from_stream),
    0xc4d32ae5: ('collision', TweakPlayer_Collision.from_stream),
    0xd6155d4b: ('first_person_camera', TweakPlayer_FirstPersonCamera.from_stream),
    0xbcca767e: ('shield', TweakPlayer_Shield.from_stream),
    0x4d3b20b7: ('frozen', TweakPlayer_Frozen.from_stream),
    0xaeaff210: ('suit_damage_reduction', TweakPlayer_SuitDamageReduction.from_stream),
}
