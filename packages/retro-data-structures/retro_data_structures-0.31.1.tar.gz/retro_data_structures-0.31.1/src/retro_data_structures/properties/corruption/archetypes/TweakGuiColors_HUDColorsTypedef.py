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
from retro_data_structures.properties.corruption.core.Color import Color

if typing.TYPE_CHECKING:
    class TweakGuiColors_HUDColorsTypedefJson(typing_extensions.TypedDict):
        unknown_0xc8ddc662: json_util.JsonValue
        threat_group_active_color: json_util.JsonValue
        threat_group_inactive_color: json_util.JsonValue
        unknown_0xa6609cc5: json_util.JsonValue
        missile_group_active_color: json_util.JsonValue
        missile_group_inactive_color: json_util.JsonValue
        unknown_0xdcaab836: json_util.JsonValue
        unknown_0x57d7ba36: json_util.JsonValue
        unknown_0x20b20348: json_util.JsonValue
        energy_bar_filled_color: json_util.JsonValue
        energy_bar_shadow_color: json_util.JsonValue
        energy_bar_empty_color: json_util.JsonValue
        energy_tanks_filled_color: json_util.JsonValue
        energy_tanks_empty_color: json_util.JsonValue
        radar_widget_color: json_util.JsonValue
        active_text_foreground_color: json_util.JsonValue
        inactive_text_foreground_color: json_util.JsonValue
        text_shadow_outline_color: json_util.JsonValue
        unknown_0x3c1ae0ff: json_util.JsonValue
        missile_bar_shadow_color: json_util.JsonValue
        missile_bar_empty_color: json_util.JsonValue
        unknown_0x8b45a902: json_util.JsonValue
        unknown_0x9e1a78ff: json_util.JsonValue
        unknown_0x8626bab3: json_util.JsonValue
        unknown_0x4c158fc5: json_util.JsonValue
        unknown_0x594a5e38: json_util.JsonValue
        unknown_0x01a8c9c8: json_util.JsonValue
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xc8ddc662, 0x2f3cacaf, 0x74e5ffa1, 0xa6609cc5, 0xcbb3fb76, 0xd110a12f, 0xdcaab836, 0x57d7ba36, 0x20b20348, 0xacf62d93, 0xb9a9fc6e, 0x37e381c2, 0x4377e677, 0x63384f81, 0xa709db40, 0xaa4a5604, 0x6cccdf8f, 0xdaa7d80, 0x3c1ae0ff, 0x29453102, 0x64337ccd, 0x8b45a902, 0x9e1a78ff, 0x8626bab3, 0x4c158fc5, 0x594a5e38, 0x1a8c9c8)


@dataclasses.dataclass()
class TweakGuiColors_HUDColorsTypedef(BaseProperty):
    unknown_0xc8ddc662: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xc8ddc662, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    threat_group_active_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x2f3cacaf, original_name='ThreatGroupActiveColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    threat_group_inactive_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x74e5ffa1, original_name='ThreatGroupInactiveColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xa6609cc5: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa6609cc5, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    missile_group_active_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xcbb3fb76, original_name='MissileGroupActiveColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    missile_group_inactive_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd110a12f, original_name='MissileGroupInactiveColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xdcaab836: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xdcaab836, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x57d7ba36: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x57d7ba36, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x20b20348: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x20b20348, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_bar_filled_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xacf62d93, original_name='EnergyBarFilledColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_bar_shadow_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xb9a9fc6e, original_name='EnergyBarShadowColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_bar_empty_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x37e381c2, original_name='EnergyBarEmptyColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_tanks_filled_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x4377e677, original_name='EnergyTanksFilledColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    energy_tanks_empty_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x63384f81, original_name='EnergyTanksEmptyColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    radar_widget_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa709db40, original_name='RadarWidgetColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    active_text_foreground_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xaa4a5604, original_name='ActiveTextForegroundColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    inactive_text_foreground_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x6cccdf8f, original_name='InactiveTextForegroundColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    text_shadow_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x0daa7d80, original_name='TextShadowOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x3c1ae0ff: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x3c1ae0ff, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    missile_bar_shadow_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x29453102, original_name='MissileBarShadowColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    missile_bar_empty_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x64337ccd, original_name='MissileBarEmptyColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x8b45a902: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x8b45a902, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x9e1a78ff: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x9e1a78ff, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x8626bab3: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x8626bab3, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x4c158fc5: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x4c158fc5, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x594a5e38: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x594a5e38, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x01a8c9c8: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x01a8c9c8, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
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
        if property_count != 27:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffff')
    
        dec = _FAST_FORMAT.unpack(data.read(594))
        assert (dec[0], dec[6], dec[12], dec[18], dec[24], dec[30], dec[36], dec[42], dec[48], dec[54], dec[60], dec[66], dec[72], dec[78], dec[84], dec[90], dec[96], dec[102], dec[108], dec[114], dec[120], dec[126], dec[132], dec[138], dec[144], dec[150], dec[156]) == _FAST_IDS
        return cls(
            Color(*dec[2:6]),
            Color(*dec[8:12]),
            Color(*dec[14:18]),
            Color(*dec[20:24]),
            Color(*dec[26:30]),
            Color(*dec[32:36]),
            Color(*dec[38:42]),
            Color(*dec[44:48]),
            Color(*dec[50:54]),
            Color(*dec[56:60]),
            Color(*dec[62:66]),
            Color(*dec[68:72]),
            Color(*dec[74:78]),
            Color(*dec[80:84]),
            Color(*dec[86:90]),
            Color(*dec[92:96]),
            Color(*dec[98:102]),
            Color(*dec[104:108]),
            Color(*dec[110:114]),
            Color(*dec[116:120]),
            Color(*dec[122:126]),
            Color(*dec[128:132]),
            Color(*dec[134:138]),
            Color(*dec[140:144]),
            Color(*dec[146:150]),
            Color(*dec[152:156]),
            Color(*dec[158:162]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00\x1b')  # 27 properties

        data.write(b'\xc8\xdd\xc6b')  # 0xc8ddc662
        data.write(b'\x00\x10')  # size
        self.unknown_0xc8ddc662.to_stream(data)

        data.write(b'/<\xac\xaf')  # 0x2f3cacaf
        data.write(b'\x00\x10')  # size
        self.threat_group_active_color.to_stream(data)

        data.write(b't\xe5\xff\xa1')  # 0x74e5ffa1
        data.write(b'\x00\x10')  # size
        self.threat_group_inactive_color.to_stream(data)

        data.write(b'\xa6`\x9c\xc5')  # 0xa6609cc5
        data.write(b'\x00\x10')  # size
        self.unknown_0xa6609cc5.to_stream(data)

        data.write(b'\xcb\xb3\xfbv')  # 0xcbb3fb76
        data.write(b'\x00\x10')  # size
        self.missile_group_active_color.to_stream(data)

        data.write(b'\xd1\x10\xa1/')  # 0xd110a12f
        data.write(b'\x00\x10')  # size
        self.missile_group_inactive_color.to_stream(data)

        data.write(b'\xdc\xaa\xb86')  # 0xdcaab836
        data.write(b'\x00\x10')  # size
        self.unknown_0xdcaab836.to_stream(data)

        data.write(b'W\xd7\xba6')  # 0x57d7ba36
        data.write(b'\x00\x10')  # size
        self.unknown_0x57d7ba36.to_stream(data)

        data.write(b' \xb2\x03H')  # 0x20b20348
        data.write(b'\x00\x10')  # size
        self.unknown_0x20b20348.to_stream(data)

        data.write(b'\xac\xf6-\x93')  # 0xacf62d93
        data.write(b'\x00\x10')  # size
        self.energy_bar_filled_color.to_stream(data)

        data.write(b'\xb9\xa9\xfcn')  # 0xb9a9fc6e
        data.write(b'\x00\x10')  # size
        self.energy_bar_shadow_color.to_stream(data)

        data.write(b'7\xe3\x81\xc2')  # 0x37e381c2
        data.write(b'\x00\x10')  # size
        self.energy_bar_empty_color.to_stream(data)

        data.write(b'Cw\xe6w')  # 0x4377e677
        data.write(b'\x00\x10')  # size
        self.energy_tanks_filled_color.to_stream(data)

        data.write(b'c8O\x81')  # 0x63384f81
        data.write(b'\x00\x10')  # size
        self.energy_tanks_empty_color.to_stream(data)

        data.write(b'\xa7\t\xdb@')  # 0xa709db40
        data.write(b'\x00\x10')  # size
        self.radar_widget_color.to_stream(data)

        data.write(b'\xaaJV\x04')  # 0xaa4a5604
        data.write(b'\x00\x10')  # size
        self.active_text_foreground_color.to_stream(data)

        data.write(b'l\xcc\xdf\x8f')  # 0x6cccdf8f
        data.write(b'\x00\x10')  # size
        self.inactive_text_foreground_color.to_stream(data)

        data.write(b'\r\xaa}\x80')  # 0xdaa7d80
        data.write(b'\x00\x10')  # size
        self.text_shadow_outline_color.to_stream(data)

        data.write(b'<\x1a\xe0\xff')  # 0x3c1ae0ff
        data.write(b'\x00\x10')  # size
        self.unknown_0x3c1ae0ff.to_stream(data)

        data.write(b')E1\x02')  # 0x29453102
        data.write(b'\x00\x10')  # size
        self.missile_bar_shadow_color.to_stream(data)

        data.write(b'd3|\xcd')  # 0x64337ccd
        data.write(b'\x00\x10')  # size
        self.missile_bar_empty_color.to_stream(data)

        data.write(b'\x8bE\xa9\x02')  # 0x8b45a902
        data.write(b'\x00\x10')  # size
        self.unknown_0x8b45a902.to_stream(data)

        data.write(b'\x9e\x1ax\xff')  # 0x9e1a78ff
        data.write(b'\x00\x10')  # size
        self.unknown_0x9e1a78ff.to_stream(data)

        data.write(b'\x86&\xba\xb3')  # 0x8626bab3
        data.write(b'\x00\x10')  # size
        self.unknown_0x8626bab3.to_stream(data)

        data.write(b'L\x15\x8f\xc5')  # 0x4c158fc5
        data.write(b'\x00\x10')  # size
        self.unknown_0x4c158fc5.to_stream(data)

        data.write(b'YJ^8')  # 0x594a5e38
        data.write(b'\x00\x10')  # size
        self.unknown_0x594a5e38.to_stream(data)

        data.write(b'\x01\xa8\xc9\xc8')  # 0x1a8c9c8
        data.write(b'\x00\x10')  # size
        self.unknown_0x01a8c9c8.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakGuiColors_HUDColorsTypedefJson", data)
        return cls(
            unknown_0xc8ddc662=Color.from_json(json_data['unknown_0xc8ddc662']),
            threat_group_active_color=Color.from_json(json_data['threat_group_active_color']),
            threat_group_inactive_color=Color.from_json(json_data['threat_group_inactive_color']),
            unknown_0xa6609cc5=Color.from_json(json_data['unknown_0xa6609cc5']),
            missile_group_active_color=Color.from_json(json_data['missile_group_active_color']),
            missile_group_inactive_color=Color.from_json(json_data['missile_group_inactive_color']),
            unknown_0xdcaab836=Color.from_json(json_data['unknown_0xdcaab836']),
            unknown_0x57d7ba36=Color.from_json(json_data['unknown_0x57d7ba36']),
            unknown_0x20b20348=Color.from_json(json_data['unknown_0x20b20348']),
            energy_bar_filled_color=Color.from_json(json_data['energy_bar_filled_color']),
            energy_bar_shadow_color=Color.from_json(json_data['energy_bar_shadow_color']),
            energy_bar_empty_color=Color.from_json(json_data['energy_bar_empty_color']),
            energy_tanks_filled_color=Color.from_json(json_data['energy_tanks_filled_color']),
            energy_tanks_empty_color=Color.from_json(json_data['energy_tanks_empty_color']),
            radar_widget_color=Color.from_json(json_data['radar_widget_color']),
            active_text_foreground_color=Color.from_json(json_data['active_text_foreground_color']),
            inactive_text_foreground_color=Color.from_json(json_data['inactive_text_foreground_color']),
            text_shadow_outline_color=Color.from_json(json_data['text_shadow_outline_color']),
            unknown_0x3c1ae0ff=Color.from_json(json_data['unknown_0x3c1ae0ff']),
            missile_bar_shadow_color=Color.from_json(json_data['missile_bar_shadow_color']),
            missile_bar_empty_color=Color.from_json(json_data['missile_bar_empty_color']),
            unknown_0x8b45a902=Color.from_json(json_data['unknown_0x8b45a902']),
            unknown_0x9e1a78ff=Color.from_json(json_data['unknown_0x9e1a78ff']),
            unknown_0x8626bab3=Color.from_json(json_data['unknown_0x8626bab3']),
            unknown_0x4c158fc5=Color.from_json(json_data['unknown_0x4c158fc5']),
            unknown_0x594a5e38=Color.from_json(json_data['unknown_0x594a5e38']),
            unknown_0x01a8c9c8=Color.from_json(json_data['unknown_0x01a8c9c8']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xc8ddc662': self.unknown_0xc8ddc662.to_json(),
            'threat_group_active_color': self.threat_group_active_color.to_json(),
            'threat_group_inactive_color': self.threat_group_inactive_color.to_json(),
            'unknown_0xa6609cc5': self.unknown_0xa6609cc5.to_json(),
            'missile_group_active_color': self.missile_group_active_color.to_json(),
            'missile_group_inactive_color': self.missile_group_inactive_color.to_json(),
            'unknown_0xdcaab836': self.unknown_0xdcaab836.to_json(),
            'unknown_0x57d7ba36': self.unknown_0x57d7ba36.to_json(),
            'unknown_0x20b20348': self.unknown_0x20b20348.to_json(),
            'energy_bar_filled_color': self.energy_bar_filled_color.to_json(),
            'energy_bar_shadow_color': self.energy_bar_shadow_color.to_json(),
            'energy_bar_empty_color': self.energy_bar_empty_color.to_json(),
            'energy_tanks_filled_color': self.energy_tanks_filled_color.to_json(),
            'energy_tanks_empty_color': self.energy_tanks_empty_color.to_json(),
            'radar_widget_color': self.radar_widget_color.to_json(),
            'active_text_foreground_color': self.active_text_foreground_color.to_json(),
            'inactive_text_foreground_color': self.inactive_text_foreground_color.to_json(),
            'text_shadow_outline_color': self.text_shadow_outline_color.to_json(),
            'unknown_0x3c1ae0ff': self.unknown_0x3c1ae0ff.to_json(),
            'missile_bar_shadow_color': self.missile_bar_shadow_color.to_json(),
            'missile_bar_empty_color': self.missile_bar_empty_color.to_json(),
            'unknown_0x8b45a902': self.unknown_0x8b45a902.to_json(),
            'unknown_0x9e1a78ff': self.unknown_0x9e1a78ff.to_json(),
            'unknown_0x8626bab3': self.unknown_0x8626bab3.to_json(),
            'unknown_0x4c158fc5': self.unknown_0x4c158fc5.to_json(),
            'unknown_0x594a5e38': self.unknown_0x594a5e38.to_json(),
            'unknown_0x01a8c9c8': self.unknown_0x01a8c9c8.to_json(),
        }


def _decode_unknown_0xc8ddc662(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_threat_group_active_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_threat_group_inactive_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xa6609cc5(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_missile_group_active_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_missile_group_inactive_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xdcaab836(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x57d7ba36(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x20b20348(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_bar_filled_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_bar_shadow_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_bar_empty_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_tanks_filled_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_energy_tanks_empty_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_radar_widget_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_active_text_foreground_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_inactive_text_foreground_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_text_shadow_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x3c1ae0ff(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_missile_bar_shadow_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_missile_bar_empty_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x8b45a902(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x9e1a78ff(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x8626bab3(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x4c158fc5(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x594a5e38(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x01a8c9c8(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xc8ddc662: ('unknown_0xc8ddc662', _decode_unknown_0xc8ddc662),
    0x2f3cacaf: ('threat_group_active_color', _decode_threat_group_active_color),
    0x74e5ffa1: ('threat_group_inactive_color', _decode_threat_group_inactive_color),
    0xa6609cc5: ('unknown_0xa6609cc5', _decode_unknown_0xa6609cc5),
    0xcbb3fb76: ('missile_group_active_color', _decode_missile_group_active_color),
    0xd110a12f: ('missile_group_inactive_color', _decode_missile_group_inactive_color),
    0xdcaab836: ('unknown_0xdcaab836', _decode_unknown_0xdcaab836),
    0x57d7ba36: ('unknown_0x57d7ba36', _decode_unknown_0x57d7ba36),
    0x20b20348: ('unknown_0x20b20348', _decode_unknown_0x20b20348),
    0xacf62d93: ('energy_bar_filled_color', _decode_energy_bar_filled_color),
    0xb9a9fc6e: ('energy_bar_shadow_color', _decode_energy_bar_shadow_color),
    0x37e381c2: ('energy_bar_empty_color', _decode_energy_bar_empty_color),
    0x4377e677: ('energy_tanks_filled_color', _decode_energy_tanks_filled_color),
    0x63384f81: ('energy_tanks_empty_color', _decode_energy_tanks_empty_color),
    0xa709db40: ('radar_widget_color', _decode_radar_widget_color),
    0xaa4a5604: ('active_text_foreground_color', _decode_active_text_foreground_color),
    0x6cccdf8f: ('inactive_text_foreground_color', _decode_inactive_text_foreground_color),
    0xdaa7d80: ('text_shadow_outline_color', _decode_text_shadow_outline_color),
    0x3c1ae0ff: ('unknown_0x3c1ae0ff', _decode_unknown_0x3c1ae0ff),
    0x29453102: ('missile_bar_shadow_color', _decode_missile_bar_shadow_color),
    0x64337ccd: ('missile_bar_empty_color', _decode_missile_bar_empty_color),
    0x8b45a902: ('unknown_0x8b45a902', _decode_unknown_0x8b45a902),
    0x9e1a78ff: ('unknown_0x9e1a78ff', _decode_unknown_0x9e1a78ff),
    0x8626bab3: ('unknown_0x8626bab3', _decode_unknown_0x8626bab3),
    0x4c158fc5: ('unknown_0x4c158fc5', _decode_unknown_0x4c158fc5),
    0x594a5e38: ('unknown_0x594a5e38', _decode_unknown_0x594a5e38),
    0x1a8c9c8: ('unknown_0x01a8c9c8', _decode_unknown_0x01a8c9c8),
}
