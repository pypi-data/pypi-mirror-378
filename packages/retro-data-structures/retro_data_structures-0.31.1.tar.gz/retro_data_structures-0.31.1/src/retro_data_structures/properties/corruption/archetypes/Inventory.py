# Generated File
from __future__ import annotations

import dataclasses
import struct
import typing
import typing_extensions

from retro_data_structures import json_util
from retro_data_structures.game_check import Game
from retro_data_structures.properties.base_property import BaseProperty
from retro_data_structures.properties.field_reflection import FieldReflection
from retro_data_structures.properties.corruption.archetypes.Abilities import Abilities
from retro_data_structures.properties.corruption.archetypes.Ball import Ball
from retro_data_structures.properties.corruption.archetypes.HyperMode import HyperMode
from retro_data_structures.properties.corruption.archetypes.Misc import Misc
from retro_data_structures.properties.corruption.archetypes.Ship import Ship
from retro_data_structures.properties.corruption.archetypes.Visors import Visors
from retro_data_structures.properties.corruption.archetypes.Weapons import Weapons

if typing.TYPE_CHECKING:
    class InventoryJson(typing_extensions.TypedDict):
        misc: json_util.JsonObject
        weapons: json_util.JsonObject
        visors: json_util.JsonObject
        ball: json_util.JsonObject
        abilities: json_util.JsonObject
        hyper_mode: json_util.JsonObject
        ship: json_util.JsonObject
    

@dataclasses.dataclass()
class Inventory(BaseProperty):
    misc: Misc = dataclasses.field(default_factory=Misc, metadata={
        'reflection': FieldReflection[Misc](
            Misc, id=0x52c779c0, original_name='Misc', from_json=Misc.from_json, to_json=Misc.to_json
        ),
    })
    weapons: Weapons = dataclasses.field(default_factory=Weapons, metadata={
        'reflection': FieldReflection[Weapons](
            Weapons, id=0xef43b845, original_name='Weapons', from_json=Weapons.from_json, to_json=Weapons.to_json
        ),
    })
    visors: Visors = dataclasses.field(default_factory=Visors, metadata={
        'reflection': FieldReflection[Visors](
            Visors, id=0x317d45bb, original_name='Visors', from_json=Visors.from_json, to_json=Visors.to_json
        ),
    })
    ball: Ball = dataclasses.field(default_factory=Ball, metadata={
        'reflection': FieldReflection[Ball](
            Ball, id=0xed7f3b4a, original_name='Ball', from_json=Ball.from_json, to_json=Ball.to_json
        ),
    })
    abilities: Abilities = dataclasses.field(default_factory=Abilities, metadata={
        'reflection': FieldReflection[Abilities](
            Abilities, id=0x267f91e5, original_name='Abilities', from_json=Abilities.from_json, to_json=Abilities.to_json
        ),
    })
    hyper_mode: HyperMode = dataclasses.field(default_factory=HyperMode, metadata={
        'reflection': FieldReflection[HyperMode](
            HyperMode, id=0x378e02b2, original_name='HyperMode', from_json=HyperMode.from_json, to_json=HyperMode.to_json
        ),
    })
    ship: Ship = dataclasses.field(default_factory=Ship, metadata={
        'reflection': FieldReflection[Ship](
            Ship, id=0xe9c4a786, original_name='Ship', from_json=Ship.from_json, to_json=Ship.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.CORRUPTION

    @classmethod
    def from_stream(cls, data: typing.BinaryIO, size: int | None = None, default_override: dict | None = None) -> typing_extensions.Self:
        property_count = struct.unpack(">H", data.read(2))[0]
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

        return cls(**present_fields)

    @classmethod
    def _fast_decode(cls, data: typing.BinaryIO, property_count: int) -> typing_extensions.Self | None:
        if property_count != 7:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x52c779c0
        misc = Misc.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xef43b845
        weapons = Weapons.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x317d45bb
        visors = Visors.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xed7f3b4a
        ball = Ball.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x267f91e5
        abilities = Abilities.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x378e02b2
        hyper_mode = HyperMode.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xe9c4a786
        ship = Ship.from_stream(data, property_size)
    
        return cls(misc, weapons, visors, ball, abilities, hyper_mode, ship)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x07')  # 7 properties

        data.write(b'R\xc7y\xc0')  # 0x52c779c0
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.misc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xefC\xb8E')  # 0xef43b845
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.weapons.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'1}E\xbb')  # 0x317d45bb
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.visors.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xed\x7f;J')  # 0xed7f3b4a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ball.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'&\x7f\x91\xe5')  # 0x267f91e5
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.abilities.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'7\x8e\x02\xb2')  # 0x378e02b2
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.hyper_mode.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xe9\xc4\xa7\x86')  # 0xe9c4a786
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.ship.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("InventoryJson", data)
        return cls(
            misc=Misc.from_json(json_data['misc']),
            weapons=Weapons.from_json(json_data['weapons']),
            visors=Visors.from_json(json_data['visors']),
            ball=Ball.from_json(json_data['ball']),
            abilities=Abilities.from_json(json_data['abilities']),
            hyper_mode=HyperMode.from_json(json_data['hyper_mode']),
            ship=Ship.from_json(json_data['ship']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'misc': self.misc.to_json(),
            'weapons': self.weapons.to_json(),
            'visors': self.visors.to_json(),
            'ball': self.ball.to_json(),
            'abilities': self.abilities.to_json(),
            'hyper_mode': self.hyper_mode.to_json(),
            'ship': self.ship.to_json(),
        }


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x52c779c0: ('misc', Misc.from_stream),
    0xef43b845: ('weapons', Weapons.from_stream),
    0x317d45bb: ('visors', Visors.from_stream),
    0xed7f3b4a: ('ball', Ball.from_stream),
    0x267f91e5: ('abilities', Abilities.from_stream),
    0x378e02b2: ('hyper_mode', HyperMode.from_stream),
    0xe9c4a786: ('ship', Ship.from_stream),
}
