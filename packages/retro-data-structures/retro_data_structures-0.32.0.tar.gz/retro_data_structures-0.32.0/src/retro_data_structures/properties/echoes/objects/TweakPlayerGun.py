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
from retro_data_structures.properties.echoes.archetypes.CameraShakerData import CameraShakerData
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_Arm_Position import TweakPlayerGun_Arm_Position
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_Beam_Misc import TweakPlayerGun_Beam_Misc
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_Holstering import TweakPlayerGun_Holstering
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_Misc import TweakPlayerGun_Misc
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_Position import TweakPlayerGun_Position
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_RicochetDamage_Factor import TweakPlayerGun_RicochetDamage_Factor
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_UnknownStruct1 import TweakPlayerGun_UnknownStruct1
from retro_data_structures.properties.echoes.archetypes.TweakPlayerGun_Weapons import TweakPlayerGun_Weapons

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakPlayerGunJson(typing_extensions.TypedDict):
        instance_name: str
        misc: json_util.JsonObject
        holstering: json_util.JsonObject
        position: json_util.JsonObject
        arm_position: json_util.JsonObject
        weapons: json_util.JsonObject
        combos: json_util.JsonObject
        beam_misc: json_util.JsonObject
        ricochet_damage_factor: json_util.JsonObject
        recoil: json_util.JsonObject
        combo_recoil: json_util.JsonObject
        projectile_recoil: json_util.JsonObject
        flame_thrower: json_util.JsonObject
        wave_buster: json_util.JsonObject
        projectile_impact: json_util.JsonObject
    

@dataclasses.dataclass()
class TweakPlayerGun(BaseObjectType):
    instance_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x7fda1466, original_name='InstanceName'
        ),
    })
    misc: TweakPlayerGun_Misc = dataclasses.field(default_factory=TweakPlayerGun_Misc, metadata={
        'reflection': FieldReflection[TweakPlayerGun_Misc](
            TweakPlayerGun_Misc, id=0xb82ed424, original_name='Misc', from_json=TweakPlayerGun_Misc.from_json, to_json=TweakPlayerGun_Misc.to_json
        ),
    })
    holstering: TweakPlayerGun_Holstering = dataclasses.field(default_factory=TweakPlayerGun_Holstering, metadata={
        'reflection': FieldReflection[TweakPlayerGun_Holstering](
            TweakPlayerGun_Holstering, id=0x6b6bdc47, original_name='Holstering', from_json=TweakPlayerGun_Holstering.from_json, to_json=TweakPlayerGun_Holstering.to_json
        ),
    })
    position: TweakPlayerGun_Position = dataclasses.field(default_factory=TweakPlayerGun_Position, metadata={
        'reflection': FieldReflection[TweakPlayerGun_Position](
            TweakPlayerGun_Position, id=0x87882cb0, original_name='Position', from_json=TweakPlayerGun_Position.from_json, to_json=TweakPlayerGun_Position.to_json
        ),
    })
    arm_position: TweakPlayerGun_Arm_Position = dataclasses.field(default_factory=TweakPlayerGun_Arm_Position, metadata={
        'reflection': FieldReflection[TweakPlayerGun_Arm_Position](
            TweakPlayerGun_Arm_Position, id=0x255007ad, original_name='Arm_Position', from_json=TweakPlayerGun_Arm_Position.from_json, to_json=TweakPlayerGun_Arm_Position.to_json
        ),
    })
    weapons: TweakPlayerGun_Weapons = dataclasses.field(default_factory=TweakPlayerGun_Weapons, metadata={
        'reflection': FieldReflection[TweakPlayerGun_Weapons](
            TweakPlayerGun_Weapons, id=0x83d758ab, original_name='Weapons', from_json=TweakPlayerGun_Weapons.from_json, to_json=TweakPlayerGun_Weapons.to_json
        ),
    })
    combos: TweakPlayerGun_UnknownStruct1 = dataclasses.field(default_factory=TweakPlayerGun_UnknownStruct1, metadata={
        'reflection': FieldReflection[TweakPlayerGun_UnknownStruct1](
            TweakPlayerGun_UnknownStruct1, id=0x888c8775, original_name='Combos', from_json=TweakPlayerGun_UnknownStruct1.from_json, to_json=TweakPlayerGun_UnknownStruct1.to_json
        ),
    })
    beam_misc: TweakPlayerGun_Beam_Misc = dataclasses.field(default_factory=TweakPlayerGun_Beam_Misc, metadata={
        'reflection': FieldReflection[TweakPlayerGun_Beam_Misc](
            TweakPlayerGun_Beam_Misc, id=0xaaebb73e, original_name='Beam_Misc', from_json=TweakPlayerGun_Beam_Misc.from_json, to_json=TweakPlayerGun_Beam_Misc.to_json
        ),
    })
    ricochet_damage_factor: TweakPlayerGun_RicochetDamage_Factor = dataclasses.field(default_factory=TweakPlayerGun_RicochetDamage_Factor, metadata={
        'reflection': FieldReflection[TweakPlayerGun_RicochetDamage_Factor](
            TweakPlayerGun_RicochetDamage_Factor, id=0x8da058fe, original_name='RicochetDamage_Factor', from_json=TweakPlayerGun_RicochetDamage_Factor.from_json, to_json=TweakPlayerGun_RicochetDamage_Factor.to_json
        ),
    })
    recoil: CameraShakerData = dataclasses.field(default_factory=CameraShakerData, metadata={
        'reflection': FieldReflection[CameraShakerData](
            CameraShakerData, id=0xffdb4bb7, original_name='Recoil', from_json=CameraShakerData.from_json, to_json=CameraShakerData.to_json
        ),
    })
    combo_recoil: CameraShakerData = dataclasses.field(default_factory=CameraShakerData, metadata={
        'reflection': FieldReflection[CameraShakerData](
            CameraShakerData, id=0x937a35bd, original_name='ComboRecoil', from_json=CameraShakerData.from_json, to_json=CameraShakerData.to_json
        ),
    })
    projectile_recoil: CameraShakerData = dataclasses.field(default_factory=CameraShakerData, metadata={
        'reflection': FieldReflection[CameraShakerData](
            CameraShakerData, id=0x26196738, original_name='ProjectileRecoil', from_json=CameraShakerData.from_json, to_json=CameraShakerData.to_json
        ),
    })
    flame_thrower: CameraShakerData = dataclasses.field(default_factory=CameraShakerData, metadata={
        'reflection': FieldReflection[CameraShakerData](
            CameraShakerData, id=0xf40808c9, original_name='FlameThrower', from_json=CameraShakerData.from_json, to_json=CameraShakerData.to_json
        ),
    })
    wave_buster: CameraShakerData = dataclasses.field(default_factory=CameraShakerData, metadata={
        'reflection': FieldReflection[CameraShakerData](
            CameraShakerData, id=0x9a6d7a31, original_name='WaveBuster', from_json=CameraShakerData.from_json, to_json=CameraShakerData.to_json
        ),
    })
    projectile_impact: CameraShakerData = dataclasses.field(default_factory=CameraShakerData, metadata={
        'reflection': FieldReflection[CameraShakerData](
            CameraShakerData, id=0x12f14c5a, original_name='ProjectileImpact', from_json=CameraShakerData.from_json, to_json=CameraShakerData.to_json
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
        return 'TWPM'

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
        if property_count != 15:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fda1466
        instance_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xb82ed424
        misc = TweakPlayerGun_Misc.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x6b6bdc47
        holstering = TweakPlayerGun_Holstering.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x87882cb0
        position = TweakPlayerGun_Position.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x255007ad
        arm_position = TweakPlayerGun_Arm_Position.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x83d758ab
        weapons = TweakPlayerGun_Weapons.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x888c8775
        combos = TweakPlayerGun_UnknownStruct1.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xaaebb73e
        beam_misc = TweakPlayerGun_Beam_Misc.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x8da058fe
        ricochet_damage_factor = TweakPlayerGun_RicochetDamage_Factor.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xffdb4bb7
        recoil = CameraShakerData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x937a35bd
        combo_recoil = CameraShakerData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x26196738
        projectile_recoil = CameraShakerData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xf40808c9
        flame_thrower = CameraShakerData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x9a6d7a31
        wave_buster = CameraShakerData.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x12f14c5a
        projectile_impact = CameraShakerData.from_stream(data, property_size, default_override={'flags_camera_shaker': 19})
    
        return cls(instance_name, misc, holstering, position, arm_position, weapons, combos, beam_misc, ricochet_damage_factor, recoil, combo_recoil, projectile_recoil, flame_thrower, wave_buster, projectile_impact)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x0f')  # 15 properties

        data.write(b'\x7f\xda\x14f')  # 0x7fda1466
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.instance_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xb8.\xd4$')  # 0xb82ed424
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.misc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'kk\xdcG')  # 0x6b6bdc47
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.holstering.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x87\x88,\xb0')  # 0x87882cb0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.position.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'%P\x07\xad')  # 0x255007ad
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.arm_position.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x83\xd7X\xab')  # 0x83d758ab
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weapons.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x88\x8c\x87u')  # 0x888c8775
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.combos.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xaa\xeb\xb7>')  # 0xaaebb73e
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.beam_misc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x8d\xa0X\xfe')  # 0x8da058fe
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ricochet_damage_factor.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xff\xdbK\xb7')  # 0xffdb4bb7
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.recoil.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x93z5\xbd')  # 0x937a35bd
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.combo_recoil.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'&\x19g8')  # 0x26196738
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile_recoil.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xf4\x08\x08\xc9')  # 0xf40808c9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.flame_thrower.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x9amz1')  # 0x9a6d7a31
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.wave_buster.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x12\xf1LZ')  # 0x12f14c5a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.projectile_impact.to_stream(data, default_override={'flags_camera_shaker': 19})
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
        json_data = typing.cast("TweakPlayerGunJson", data)
        return cls(
            instance_name=json_data['instance_name'],
            misc=TweakPlayerGun_Misc.from_json(json_data['misc']),
            holstering=TweakPlayerGun_Holstering.from_json(json_data['holstering']),
            position=TweakPlayerGun_Position.from_json(json_data['position']),
            arm_position=TweakPlayerGun_Arm_Position.from_json(json_data['arm_position']),
            weapons=TweakPlayerGun_Weapons.from_json(json_data['weapons']),
            combos=TweakPlayerGun_UnknownStruct1.from_json(json_data['combos']),
            beam_misc=TweakPlayerGun_Beam_Misc.from_json(json_data['beam_misc']),
            ricochet_damage_factor=TweakPlayerGun_RicochetDamage_Factor.from_json(json_data['ricochet_damage_factor']),
            recoil=CameraShakerData.from_json(json_data['recoil']),
            combo_recoil=CameraShakerData.from_json(json_data['combo_recoil']),
            projectile_recoil=CameraShakerData.from_json(json_data['projectile_recoil']),
            flame_thrower=CameraShakerData.from_json(json_data['flame_thrower']),
            wave_buster=CameraShakerData.from_json(json_data['wave_buster']),
            projectile_impact=CameraShakerData.from_json(json_data['projectile_impact']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'instance_name': self.instance_name,
            'misc': self.misc.to_json(),
            'holstering': self.holstering.to_json(),
            'position': self.position.to_json(),
            'arm_position': self.arm_position.to_json(),
            'weapons': self.weapons.to_json(),
            'combos': self.combos.to_json(),
            'beam_misc': self.beam_misc.to_json(),
            'ricochet_damage_factor': self.ricochet_damage_factor.to_json(),
            'recoil': self.recoil.to_json(),
            'combo_recoil': self.combo_recoil.to_json(),
            'projectile_recoil': self.projectile_recoil.to_json(),
            'flame_thrower': self.flame_thrower.to_json(),
            'wave_buster': self.wave_buster.to_json(),
            'projectile_impact': self.projectile_impact.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.misc.dependencies_for, "misc", "TweakPlayerGun_Misc"),
            (self.holstering.dependencies_for, "holstering", "TweakPlayerGun_Holstering"),
            (self.position.dependencies_for, "position", "TweakPlayerGun_Position"),
            (self.arm_position.dependencies_for, "arm_position", "TweakPlayerGun_Arm_Position"),
            (self.weapons.dependencies_for, "weapons", "TweakPlayerGun_Weapons"),
            (self.combos.dependencies_for, "combos", "TweakPlayerGun_UnknownStruct1"),
            (self.beam_misc.dependencies_for, "beam_misc", "TweakPlayerGun_Beam_Misc"),
            (self.ricochet_damage_factor.dependencies_for, "ricochet_damage_factor", "TweakPlayerGun_RicochetDamage_Factor"),
            (self.recoil.dependencies_for, "recoil", "CameraShakerData"),
            (self.combo_recoil.dependencies_for, "combo_recoil", "CameraShakerData"),
            (self.projectile_recoil.dependencies_for, "projectile_recoil", "CameraShakerData"),
            (self.flame_thrower.dependencies_for, "flame_thrower", "CameraShakerData"),
            (self.wave_buster.dependencies_for, "wave_buster", "CameraShakerData"),
            (self.projectile_impact.dependencies_for, "projectile_impact", "CameraShakerData"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakPlayerGun.{field_name} ({field_type}): {e}"
                )


def _decode_instance_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


def _decode_projectile_impact(data: typing.BinaryIO, property_size: int) -> CameraShakerData:
    return CameraShakerData.from_stream(data, property_size, default_override={'flags_camera_shaker': 19})


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7fda1466: ('instance_name', _decode_instance_name),
    0xb82ed424: ('misc', TweakPlayerGun_Misc.from_stream),
    0x6b6bdc47: ('holstering', TweakPlayerGun_Holstering.from_stream),
    0x87882cb0: ('position', TweakPlayerGun_Position.from_stream),
    0x255007ad: ('arm_position', TweakPlayerGun_Arm_Position.from_stream),
    0x83d758ab: ('weapons', TweakPlayerGun_Weapons.from_stream),
    0x888c8775: ('combos', TweakPlayerGun_UnknownStruct1.from_stream),
    0xaaebb73e: ('beam_misc', TweakPlayerGun_Beam_Misc.from_stream),
    0x8da058fe: ('ricochet_damage_factor', TweakPlayerGun_RicochetDamage_Factor.from_stream),
    0xffdb4bb7: ('recoil', CameraShakerData.from_stream),
    0x937a35bd: ('combo_recoil', CameraShakerData.from_stream),
    0x26196738: ('projectile_recoil', CameraShakerData.from_stream),
    0xf40808c9: ('flame_thrower', CameraShakerData.from_stream),
    0x9a6d7a31: ('wave_buster', CameraShakerData.from_stream),
    0x12f14c5a: ('projectile_impact', _decode_projectile_impact),
}
