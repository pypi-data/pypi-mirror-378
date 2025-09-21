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
from retro_data_structures.properties.echoes.archetypes.TweakBall_BoostBall import TweakBall_BoostBall
from retro_data_structures.properties.echoes.archetypes.TweakBall_Camera import TweakBall_Camera
from retro_data_structures.properties.echoes.archetypes.TweakBall_CannonBall import TweakBall_CannonBall
from retro_data_structures.properties.echoes.archetypes.TweakBall_DeathBall import TweakBall_DeathBall
from retro_data_structures.properties.echoes.archetypes.TweakBall_Misc import TweakBall_Misc
from retro_data_structures.properties.echoes.archetypes.TweakBall_Movement import TweakBall_Movement
from retro_data_structures.properties.echoes.archetypes.TweakBall_ScrewAttack import TweakBall_ScrewAttack

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakBallJson(typing_extensions.TypedDict):
        instance_name: str
        movement: json_util.JsonObject
        camera: json_util.JsonObject
        misc: json_util.JsonObject
        boost_ball: json_util.JsonObject
        cannon_ball: json_util.JsonObject
        screw_attack: json_util.JsonObject
        death_ball: json_util.JsonObject
    

@dataclasses.dataclass()
class TweakBall(BaseObjectType):
    instance_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x7fda1466, original_name='InstanceName'
        ),
    })
    movement: TweakBall_Movement = dataclasses.field(default_factory=TweakBall_Movement, metadata={
        'reflection': FieldReflection[TweakBall_Movement](
            TweakBall_Movement, id=0x0def1ffb, original_name='Movement', from_json=TweakBall_Movement.from_json, to_json=TweakBall_Movement.to_json
        ),
    })
    camera: TweakBall_Camera = dataclasses.field(default_factory=TweakBall_Camera, metadata={
        'reflection': FieldReflection[TweakBall_Camera](
            TweakBall_Camera, id=0x7aac09b9, original_name='Camera', from_json=TweakBall_Camera.from_json, to_json=TweakBall_Camera.to_json
        ),
    })
    misc: TweakBall_Misc = dataclasses.field(default_factory=TweakBall_Misc, metadata={
        'reflection': FieldReflection[TweakBall_Misc](
            TweakBall_Misc, id=0x0c67b730, original_name='Misc', from_json=TweakBall_Misc.from_json, to_json=TweakBall_Misc.to_json
        ),
    })
    boost_ball: TweakBall_BoostBall = dataclasses.field(default_factory=TweakBall_BoostBall, metadata={
        'reflection': FieldReflection[TweakBall_BoostBall](
            TweakBall_BoostBall, id=0xcb4ea3bf, original_name='BoostBall', from_json=TweakBall_BoostBall.from_json, to_json=TweakBall_BoostBall.to_json
        ),
    })
    cannon_ball: TweakBall_CannonBall = dataclasses.field(default_factory=TweakBall_CannonBall, metadata={
        'reflection': FieldReflection[TweakBall_CannonBall](
            TweakBall_CannonBall, id=0x5fb9e808, original_name='CannonBall', from_json=TweakBall_CannonBall.from_json, to_json=TweakBall_CannonBall.to_json
        ),
    })
    screw_attack: TweakBall_ScrewAttack = dataclasses.field(default_factory=TweakBall_ScrewAttack, metadata={
        'reflection': FieldReflection[TweakBall_ScrewAttack](
            TweakBall_ScrewAttack, id=0x4b1c7b7d, original_name='ScrewAttack', from_json=TweakBall_ScrewAttack.from_json, to_json=TweakBall_ScrewAttack.to_json
        ),
    })
    death_ball: TweakBall_DeathBall = dataclasses.field(default_factory=TweakBall_DeathBall, metadata={
        'reflection': FieldReflection[TweakBall_DeathBall](
            TweakBall_DeathBall, id=0xbb5fc8a4, original_name='DeathBall', from_json=TweakBall_DeathBall.from_json, to_json=TweakBall_DeathBall.to_json
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
        return 'TWBL'

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
        if property_count != 8:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fda1466
        instance_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0def1ffb
        movement = TweakBall_Movement.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7aac09b9
        camera = TweakBall_Camera.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x0c67b730
        misc = TweakBall_Misc.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xcb4ea3bf
        boost_ball = TweakBall_BoostBall.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x5fb9e808
        cannon_ball = TweakBall_CannonBall.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x4b1c7b7d
        screw_attack = TweakBall_ScrewAttack.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xbb5fc8a4
        death_ball = TweakBall_DeathBall.from_stream(data, property_size)
    
        return cls(instance_name, movement, camera, misc, boost_ball, cannon_ball, screw_attack, death_ball)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\x08')  # 8 properties

        data.write(b'\x7f\xda\x14f')  # 0x7fda1466
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.instance_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\r\xef\x1f\xfb')  # 0xdef1ffb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.movement.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'z\xac\t\xb9')  # 0x7aac09b9
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.camera.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x0cg\xb70')  # 0xc67b730
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.misc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xcbN\xa3\xbf')  # 0xcb4ea3bf
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.boost_ball.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'_\xb9\xe8\x08')  # 0x5fb9e808
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.cannon_ball.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'K\x1c{}')  # 0x4b1c7b7d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.screw_attack.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xbb_\xc8\xa4')  # 0xbb5fc8a4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.death_ball.to_stream(data)
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
        json_data = typing.cast("TweakBallJson", data)
        return cls(
            instance_name=json_data['instance_name'],
            movement=TweakBall_Movement.from_json(json_data['movement']),
            camera=TweakBall_Camera.from_json(json_data['camera']),
            misc=TweakBall_Misc.from_json(json_data['misc']),
            boost_ball=TweakBall_BoostBall.from_json(json_data['boost_ball']),
            cannon_ball=TweakBall_CannonBall.from_json(json_data['cannon_ball']),
            screw_attack=TweakBall_ScrewAttack.from_json(json_data['screw_attack']),
            death_ball=TweakBall_DeathBall.from_json(json_data['death_ball']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'instance_name': self.instance_name,
            'movement': self.movement.to_json(),
            'camera': self.camera.to_json(),
            'misc': self.misc.to_json(),
            'boost_ball': self.boost_ball.to_json(),
            'cannon_ball': self.cannon_ball.to_json(),
            'screw_attack': self.screw_attack.to_json(),
            'death_ball': self.death_ball.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.movement.dependencies_for, "movement", "TweakBall_Movement"),
            (self.camera.dependencies_for, "camera", "TweakBall_Camera"),
            (self.misc.dependencies_for, "misc", "TweakBall_Misc"),
            (self.boost_ball.dependencies_for, "boost_ball", "TweakBall_BoostBall"),
            (self.cannon_ball.dependencies_for, "cannon_ball", "TweakBall_CannonBall"),
            (self.screw_attack.dependencies_for, "screw_attack", "TweakBall_ScrewAttack"),
            (self.death_ball.dependencies_for, "death_ball", "TweakBall_DeathBall"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakBall.{field_name} ({field_type}): {e}"
                )


def _decode_instance_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7fda1466: ('instance_name', _decode_instance_name),
    0xdef1ffb: ('movement', TweakBall_Movement.from_stream),
    0x7aac09b9: ('camera', TweakBall_Camera.from_stream),
    0xc67b730: ('misc', TweakBall_Misc.from_stream),
    0xcb4ea3bf: ('boost_ball', TweakBall_BoostBall.from_stream),
    0x5fb9e808: ('cannon_ball', TweakBall_CannonBall.from_stream),
    0x4b1c7b7d: ('screw_attack', TweakBall_ScrewAttack.from_stream),
    0xbb5fc8a4: ('death_ball', TweakBall_DeathBall.from_stream),
}
