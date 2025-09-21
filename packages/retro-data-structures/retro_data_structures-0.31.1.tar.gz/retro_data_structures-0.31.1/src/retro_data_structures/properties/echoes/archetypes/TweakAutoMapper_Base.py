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
from retro_data_structures.properties.echoes.core.Color import Color

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakAutoMapper_BaseJson(typing_extensions.TypedDict):
        unknown_0xcbe595d8: bool
        unknown_0x8ecb53a6: bool
        scale_move_speed_with_camera_distance: bool
        unknown_0x6bea9324: float
        unknown_0x065dd754: float
        unknown_0x57a46c09: float
        unknown_0xb54255b5: float
        unknown_0x0c64cec4: float
        unknown_0x335ebc7e: float
        map_screen_area_opacity: float
        unknown_0x533c5684: json_util.JsonValue
        unknown_0xeb383668: float
        unknown_0x27151ede: float
        unknown_0x434172c3: float
        unknown_0x68097036: float
        unknown_0x03adcf46: json_util.JsonValue
        unknown_0xd3fae283: json_util.JsonValue
        unknown_0x65d2cf45: json_util.JsonValue
        unknown_0xb5752c08: json_util.JsonValue
        unknown_0x035d01ce: json_util.JsonValue
        unknown_0x805d5fa3: json_util.JsonValue
        unknown_0x36757265: json_util.JsonValue
        unknown_0xe550fcbd: json_util.JsonValue
        unknown_0x5378d17b: json_util.JsonValue
        unknown_0x0ebf3cbc: json_util.JsonValue
        unknown_0xb897117a: json_util.JsonValue
        unknown_0x3e670f6a: json_util.JsonValue
        unknown_0x884f22ac: json_util.JsonValue
        unknown_0x7bdb0edf: float
        unknown_0x12221909: float
        unknown_0x38dbbc09: float
        unknown_0x30610062: float
        unknown_0xb6acea88: float
        unknown_0x73de4110: float
        map_screen_zoom_speed: float
        map_screen_circle_speed: float
        map_screen_move_speed: float
        unknown_0xab82e268: json_util.JsonValue
        unknown_0x1daacfae: json_util.JsonValue
        unknown_0xdad161a1: json_util.JsonValue
        unknown_0x6cf94c67: json_util.JsonValue
        unknown_0x47967404: float
        unknown_0x0ece1950: float
        unknown_0x9ac1bdde: float
        unknown_0x97a19386: float
        unknown_0xcb9e3a54: float
        unknown_0x2511a49b: float
        unknown_0x16c9f38e: float
        unknown_0xbc7e2e4d: float
        unknown_0x15564d32: float
        unknown_0xf5479260: float
        unknown_0x271b644e: float
        unknown_0x52dc08c1: float
        unknown_0x9980db64: float
        unknown_0x23f59057: float
        unknown_0xad3d5a3f: float
        unknown_0x3315d22b: float
        unknown_0x9e4007b6: float
        unknown_0x7a8d3d46: float
        unknown_0x2b97d64c: bool
        unknown_0xbdc57ce0: float
        unknown_0x7d59c854: float
        unknown_0x3c4ef7d2: float
        unknown_0x2b483e9f: float
        unknown_0x706f52fe: float
        unknown_0x62f9ebf6: float
        unknown_0xa9a53853: float
        unknown_0x722b1bc0: float
        player_model_color: json_util.JsonValue
        unknown_0x5a87c156: json_util.JsonValue
        player_surface_color: json_util.JsonValue
        player_outline_color: json_util.JsonValue
        text_color: json_util.JsonValue
        text_outline_color: json_util.JsonValue
        unknown_0x1a4b8068: json_util.JsonValue
        frame_color: json_util.JsonValue
        title_color: json_util.JsonValue
        legend_background_color: json_util.JsonValue
        legend_gradient_color: json_util.JsonValue
    

_FAST_FORMAT: struct.Struct | None = None
_FAST_IDS = (0xcbe595d8, 0x8ecb53a6, 0x30b13740, 0x6bea9324, 0x65dd754, 0x57a46c09, 0xb54255b5, 0xc64cec4, 0x335ebc7e, 0x45be3f6b, 0x533c5684, 0xeb383668, 0x27151ede, 0x434172c3, 0x68097036, 0x3adcf46, 0xd3fae283, 0x65d2cf45, 0xb5752c08, 0x35d01ce, 0x805d5fa3, 0x36757265, 0xe550fcbd, 0x5378d17b, 0xebf3cbc, 0xb897117a, 0x3e670f6a, 0x884f22ac, 0x7bdb0edf, 0x12221909, 0x38dbbc09, 0x30610062, 0xb6acea88, 0x73de4110, 0x19069725, 0x5ba0de1e, 0x310b37a1, 0xab82e268, 0x1daacfae, 0xdad161a1, 0x6cf94c67, 0x47967404, 0xece1950, 0x9ac1bdde, 0x97a19386, 0xcb9e3a54, 0x2511a49b, 0x16c9f38e, 0xbc7e2e4d, 0x15564d32, 0xf5479260, 0x271b644e, 0x52dc08c1, 0x9980db64, 0x23f59057, 0xad3d5a3f, 0x3315d22b, 0x9e4007b6, 0x7a8d3d46, 0x2b97d64c, 0xbdc57ce0, 0x7d59c854, 0x3c4ef7d2, 0x2b483e9f, 0x706f52fe, 0x62f9ebf6, 0xa9a53853, 0x722b1bc0, 0x4c3fc933, 0x5a87c156, 0x9c0c5318, 0x2a247ede, 0x44303a9c, 0xf2e13506, 0x1a4b8068, 0xa485372c, 0x536647d5, 0xa6b633fa, 0x1cea7f9)


@dataclasses.dataclass()
class TweakAutoMapper_Base(BaseProperty):
    unknown_0xcbe595d8: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0xcbe595d8, original_name='Unknown'
        ),
    })
    unknown_0x8ecb53a6: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x8ecb53a6, original_name='Unknown'
        ),
    })
    scale_move_speed_with_camera_distance: bool = dataclasses.field(default=True, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x30b13740, original_name='ScaleMoveSpeedWithCameraDistance'
        ),
    })
    unknown_0x6bea9324: float = dataclasses.field(default=175.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x6bea9324, original_name='Unknown'
        ),
    })
    unknown_0x065dd754: float = dataclasses.field(default=50.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x065dd754, original_name='Unknown'
        ),
    })
    unknown_0x57a46c09: float = dataclasses.field(default=700.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x57a46c09, original_name='Unknown'
        ),
    })
    unknown_0xb54255b5: float = dataclasses.field(default=-89.9000015258789, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb54255b5, original_name='Unknown'
        ),
    })
    unknown_0x0c64cec4: float = dataclasses.field(default=0.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0c64cec4, original_name='Unknown'
        ),
    })
    unknown_0x335ebc7e: float = dataclasses.field(default=75.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x335ebc7e, original_name='Unknown'
        ),
    })
    map_screen_area_opacity: float = dataclasses.field(default=0.699999988079071, metadata={
        'reflection': FieldReflection[float](
            float, id=0x45be3f6b, original_name='MapScreenAreaOpacity'
        ),
    })
    unknown_0x533c5684: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x533c5684, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xeb383668: float = dataclasses.field(default=120.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xeb383668, original_name='Unknown'
        ),
    })
    unknown_0x27151ede: float = dataclasses.field(default=-45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x27151ede, original_name='Unknown'
        ),
    })
    unknown_0x434172c3: float = dataclasses.field(default=45.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x434172c3, original_name='Unknown'
        ),
    })
    unknown_0x68097036: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x68097036, original_name='Unknown'
        ),
    })
    unknown_0x03adcf46: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x03adcf46, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xd3fae283: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xd3fae283, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x65d2cf45: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x65d2cf45, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xb5752c08: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xb5752c08, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x035d01ce: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x035d01ce, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x805d5fa3: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x805d5fa3, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x36757265: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x36757265, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xe550fcbd: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xe550fcbd, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x5378d17b: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5378d17b, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x0ebf3cbc: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x0ebf3cbc, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xb897117a: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xb897117a, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x3e670f6a: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x3e670f6a, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x884f22ac: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x884f22ac, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x7bdb0edf: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7bdb0edf, original_name='Unknown'
        ),
    })
    unknown_0x12221909: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x12221909, original_name='Unknown'
        ),
    })
    unknown_0x38dbbc09: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x38dbbc09, original_name='Unknown'
        ),
    })
    unknown_0x30610062: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x30610062, original_name='Unknown'
        ),
    })
    unknown_0xb6acea88: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0xb6acea88, original_name='Unknown'
        ),
    })
    unknown_0x73de4110: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x73de4110, original_name='Unknown'
        ),
    })
    map_screen_zoom_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x19069725, original_name='MapScreenZoomSpeed'
        ),
    })
    map_screen_circle_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x5ba0de1e, original_name='MapScreenCircleSpeed'
        ),
    })
    map_screen_move_speed: float = dataclasses.field(default=3.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x310b37a1, original_name='MapScreenMoveSpeed'
        ),
    })
    unknown_0xab82e268: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xab82e268, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x1daacfae: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1daacfae, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0xdad161a1: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xdad161a1, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x6cf94c67: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x6cf94c67, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x47967404: float = dataclasses.field(default=0.6000000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x47967404, original_name='Unknown'
        ),
    })
    unknown_0x0ece1950: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x0ece1950, original_name='Unknown'
        ),
    })
    unknown_0x9ac1bdde: float = dataclasses.field(default=0.4000000059604645, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9ac1bdde, original_name='Unknown'
        ),
    })
    unknown_0x97a19386: float = dataclasses.field(default=0.30000001192092896, metadata={
        'reflection': FieldReflection[float](
            float, id=0x97a19386, original_name='Unknown'
        ),
    })
    unknown_0xcb9e3a54: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0xcb9e3a54, original_name='Unknown'
        ),
    })
    unknown_0x2511a49b: float = dataclasses.field(default=0.25, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2511a49b, original_name='Unknown'
        ),
    })
    unknown_0x16c9f38e: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0x16c9f38e, original_name='Unknown'
        ),
    })
    unknown_0xbc7e2e4d: float = dataclasses.field(default=0.20000000298023224, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbc7e2e4d, original_name='Unknown'
        ),
    })
    unknown_0x15564d32: float = dataclasses.field(default=3.569999933242798, metadata={
        'reflection': FieldReflection[float](
            float, id=0x15564d32, original_name='Unknown'
        ),
    })
    unknown_0xf5479260: float = dataclasses.field(default=3.569999933242798, metadata={
        'reflection': FieldReflection[float](
            float, id=0xf5479260, original_name='Unknown'
        ),
    })
    unknown_0x271b644e: float = dataclasses.field(default=2.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x271b644e, original_name='Unknown'
        ),
    })
    unknown_0x52dc08c1: float = dataclasses.field(default=24.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x52dc08c1, original_name='Unknown'
        ),
    })
    unknown_0x9980db64: float = dataclasses.field(default=348.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9980db64, original_name='Unknown'
        ),
    })
    unknown_0x23f59057: float = dataclasses.field(default=152.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x23f59057, original_name='Unknown'
        ),
    })
    unknown_0xad3d5a3f: float = dataclasses.field(default=114.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xad3d5a3f, original_name='Unknown'
        ),
    })
    unknown_0x3315d22b: float = dataclasses.field(default=0.8500000238418579, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3315d22b, original_name='Unknown'
        ),
    })
    unknown_0x9e4007b6: float = dataclasses.field(default=1.850000023841858, metadata={
        'reflection': FieldReflection[float](
            float, id=0x9e4007b6, original_name='Unknown'
        ),
    })
    unknown_0x7a8d3d46: float = dataclasses.field(default=1.3600000143051147, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7a8d3d46, original_name='Unknown'
        ),
    })
    unknown_0x2b97d64c: bool = dataclasses.field(default=False, metadata={
        'reflection': FieldReflection[bool](
            bool, id=0x2b97d64c, original_name='Unknown'
        ),
    })
    unknown_0xbdc57ce0: float = dataclasses.field(default=800.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0xbdc57ce0, original_name='Unknown'
        ),
    })
    unknown_0x7d59c854: float = dataclasses.field(default=400.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x7d59c854, original_name='Unknown'
        ),
    })
    unknown_0x3c4ef7d2: float = dataclasses.field(default=2000.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x3c4ef7d2, original_name='Unknown'
        ),
    })
    unknown_0x2b483e9f: float = dataclasses.field(default=0.5, metadata={
        'reflection': FieldReflection[float](
            float, id=0x2b483e9f, original_name='Unknown'
        ),
    })
    unknown_0x706f52fe: float = dataclasses.field(default=5.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x706f52fe, original_name='Unknown'
        ),
    })
    unknown_0x62f9ebf6: float = dataclasses.field(default=1.0, metadata={
        'reflection': FieldReflection[float](
            float, id=0x62f9ebf6, original_name='Unknown'
        ),
    })
    unknown_0xa9a53853: float = dataclasses.field(default=0.6349999904632568, metadata={
        'reflection': FieldReflection[float](
            float, id=0xa9a53853, original_name='Unknown'
        ),
    })
    unknown_0x722b1bc0: float = dataclasses.field(default=-0.05000000074505806, metadata={
        'reflection': FieldReflection[float](
            float, id=0x722b1bc0, original_name='Unknown'
        ),
    })
    player_model_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x4c3fc933, original_name='PlayerModelColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x5a87c156: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x5a87c156, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    player_surface_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x9c0c5318, original_name='PlayerSurfaceColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    player_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x2a247ede, original_name='PlayerOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    text_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x44303a9c, original_name='TextColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    text_outline_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xf2e13506, original_name='TextOutlineColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    unknown_0x1a4b8068: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x1a4b8068, original_name='Unknown', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    frame_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa485372c, original_name='FrameColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    title_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x536647d5, original_name='TitleColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    legend_background_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0xa6b633fa, original_name='LegendBackgroundColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })
    legend_gradient_color: Color = dataclasses.field(default_factory=lambda: Color(r=0.0, g=0.0, b=0.0, a=0.0), metadata={
        'reflection': FieldReflection[Color](
            Color, id=0x01cea7f9, original_name='LegendGradientColor', from_json=Color.from_json, to_json=Color.to_json
        ),
    })

    @classmethod
    def game(cls) -> Game:
        return Game.ECHOES

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
        if property_count != 79:
            return None
    
        global _FAST_FORMAT
        if _FAST_FORMAT is None:
            _FAST_FORMAT = struct.Struct('>LH?LH?LH?LHfLHfLHfLHfLHfLHfLHfLHffffLHfLHfLHfLHfLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHfLHfLHfLHfLHfLHfLHfLHfLHfLHffffLHffffLHffffLHffffLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLHfLH?LHfLHfLHfLHfLHfLHfLHfLHfLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffffLHffff')
    
        dec = _FAST_FORMAT.unpack(data.read(1126))
        assert (dec[0], dec[3], dec[6], dec[9], dec[12], dec[15], dec[18], dec[21], dec[24], dec[27], dec[30], dec[36], dec[39], dec[42], dec[45], dec[48], dec[54], dec[60], dec[66], dec[72], dec[78], dec[84], dec[90], dec[96], dec[102], dec[108], dec[114], dec[120], dec[126], dec[129], dec[132], dec[135], dec[138], dec[141], dec[144], dec[147], dec[150], dec[153], dec[159], dec[165], dec[171], dec[177], dec[180], dec[183], dec[186], dec[189], dec[192], dec[195], dec[198], dec[201], dec[204], dec[207], dec[210], dec[213], dec[216], dec[219], dec[222], dec[225], dec[228], dec[231], dec[234], dec[237], dec[240], dec[243], dec[246], dec[249], dec[252], dec[255], dec[258], dec[264], dec[270], dec[276], dec[282], dec[288], dec[294], dec[300], dec[306], dec[312], dec[318]) == _FAST_IDS
        return cls(
            dec[2],
            dec[5],
            dec[8],
            dec[11],
            dec[14],
            dec[17],
            dec[20],
            dec[23],
            dec[26],
            dec[29],
            Color(*dec[32:36]),
            dec[38],
            dec[41],
            dec[44],
            dec[47],
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
            dec[128],
            dec[131],
            dec[134],
            dec[137],
            dec[140],
            dec[143],
            dec[146],
            dec[149],
            dec[152],
            Color(*dec[155:159]),
            Color(*dec[161:165]),
            Color(*dec[167:171]),
            Color(*dec[173:177]),
            dec[179],
            dec[182],
            dec[185],
            dec[188],
            dec[191],
            dec[194],
            dec[197],
            dec[200],
            dec[203],
            dec[206],
            dec[209],
            dec[212],
            dec[215],
            dec[218],
            dec[221],
            dec[224],
            dec[227],
            dec[230],
            dec[233],
            dec[236],
            dec[239],
            dec[242],
            dec[245],
            dec[248],
            dec[251],
            dec[254],
            dec[257],
            Color(*dec[260:264]),
            Color(*dec[266:270]),
            Color(*dec[272:276]),
            Color(*dec[278:282]),
            Color(*dec[284:288]),
            Color(*dec[290:294]),
            Color(*dec[296:300]),
            Color(*dec[302:306]),
            Color(*dec[308:312]),
            Color(*dec[314:318]),
            Color(*dec[320:324]),
        )

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\x00O')  # 79 properties

        data.write(b'\xcb\xe5\x95\xd8')  # 0xcbe595d8
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0xcbe595d8))

        data.write(b'\x8e\xcbS\xa6')  # 0x8ecb53a6
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x8ecb53a6))

        data.write(b'0\xb17@')  # 0x30b13740
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.scale_move_speed_with_camera_distance))

        data.write(b'k\xea\x93$')  # 0x6bea9324
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x6bea9324))

        data.write(b'\x06]\xd7T')  # 0x65dd754
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x065dd754))

        data.write(b'W\xa4l\t')  # 0x57a46c09
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x57a46c09))

        data.write(b'\xb5BU\xb5')  # 0xb54255b5
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb54255b5))

        data.write(b'\x0cd\xce\xc4')  # 0xc64cec4
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0c64cec4))

        data.write(b'3^\xbc~')  # 0x335ebc7e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x335ebc7e))

        data.write(b'E\xbe?k')  # 0x45be3f6b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_area_opacity))

        data.write(b'S<V\x84')  # 0x533c5684
        data.write(b'\x00\x10')  # size
        self.unknown_0x533c5684.to_stream(data)

        data.write(b'\xeb86h')  # 0xeb383668
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xeb383668))

        data.write(b"'\x15\x1e\xde")  # 0x27151ede
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x27151ede))

        data.write(b'CAr\xc3')  # 0x434172c3
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x434172c3))

        data.write(b'h\tp6')  # 0x68097036
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x68097036))

        data.write(b'\x03\xad\xcfF')  # 0x3adcf46
        data.write(b'\x00\x10')  # size
        self.unknown_0x03adcf46.to_stream(data)

        data.write(b'\xd3\xfa\xe2\x83')  # 0xd3fae283
        data.write(b'\x00\x10')  # size
        self.unknown_0xd3fae283.to_stream(data)

        data.write(b'e\xd2\xcfE')  # 0x65d2cf45
        data.write(b'\x00\x10')  # size
        self.unknown_0x65d2cf45.to_stream(data)

        data.write(b'\xb5u,\x08')  # 0xb5752c08
        data.write(b'\x00\x10')  # size
        self.unknown_0xb5752c08.to_stream(data)

        data.write(b'\x03]\x01\xce')  # 0x35d01ce
        data.write(b'\x00\x10')  # size
        self.unknown_0x035d01ce.to_stream(data)

        data.write(b'\x80]_\xa3')  # 0x805d5fa3
        data.write(b'\x00\x10')  # size
        self.unknown_0x805d5fa3.to_stream(data)

        data.write(b'6ure')  # 0x36757265
        data.write(b'\x00\x10')  # size
        self.unknown_0x36757265.to_stream(data)

        data.write(b'\xe5P\xfc\xbd')  # 0xe550fcbd
        data.write(b'\x00\x10')  # size
        self.unknown_0xe550fcbd.to_stream(data)

        data.write(b'Sx\xd1{')  # 0x5378d17b
        data.write(b'\x00\x10')  # size
        self.unknown_0x5378d17b.to_stream(data)

        data.write(b'\x0e\xbf<\xbc')  # 0xebf3cbc
        data.write(b'\x00\x10')  # size
        self.unknown_0x0ebf3cbc.to_stream(data)

        data.write(b'\xb8\x97\x11z')  # 0xb897117a
        data.write(b'\x00\x10')  # size
        self.unknown_0xb897117a.to_stream(data)

        data.write(b'>g\x0fj')  # 0x3e670f6a
        data.write(b'\x00\x10')  # size
        self.unknown_0x3e670f6a.to_stream(data)

        data.write(b'\x88O"\xac')  # 0x884f22ac
        data.write(b'\x00\x10')  # size
        self.unknown_0x884f22ac.to_stream(data)

        data.write(b'{\xdb\x0e\xdf')  # 0x7bdb0edf
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7bdb0edf))

        data.write(b'\x12"\x19\t')  # 0x12221909
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x12221909))

        data.write(b'8\xdb\xbc\t')  # 0x38dbbc09
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x38dbbc09))

        data.write(b'0a\x00b')  # 0x30610062
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x30610062))

        data.write(b'\xb6\xac\xea\x88')  # 0xb6acea88
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xb6acea88))

        data.write(b's\xdeA\x10')  # 0x73de4110
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x73de4110))

        data.write(b'\x19\x06\x97%')  # 0x19069725
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_zoom_speed))

        data.write(b'[\xa0\xde\x1e')  # 0x5ba0de1e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_circle_speed))

        data.write(b'1\x0b7\xa1')  # 0x310b37a1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.map_screen_move_speed))

        data.write(b'\xab\x82\xe2h')  # 0xab82e268
        data.write(b'\x00\x10')  # size
        self.unknown_0xab82e268.to_stream(data)

        data.write(b'\x1d\xaa\xcf\xae')  # 0x1daacfae
        data.write(b'\x00\x10')  # size
        self.unknown_0x1daacfae.to_stream(data)

        data.write(b'\xda\xd1a\xa1')  # 0xdad161a1
        data.write(b'\x00\x10')  # size
        self.unknown_0xdad161a1.to_stream(data)

        data.write(b'l\xf9Lg')  # 0x6cf94c67
        data.write(b'\x00\x10')  # size
        self.unknown_0x6cf94c67.to_stream(data)

        data.write(b'G\x96t\x04')  # 0x47967404
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x47967404))

        data.write(b'\x0e\xce\x19P')  # 0xece1950
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x0ece1950))

        data.write(b'\x9a\xc1\xbd\xde')  # 0x9ac1bdde
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9ac1bdde))

        data.write(b'\x97\xa1\x93\x86')  # 0x97a19386
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x97a19386))

        data.write(b'\xcb\x9e:T')  # 0xcb9e3a54
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xcb9e3a54))

        data.write(b'%\x11\xa4\x9b')  # 0x2511a49b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2511a49b))

        data.write(b'\x16\xc9\xf3\x8e')  # 0x16c9f38e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x16c9f38e))

        data.write(b'\xbc~.M')  # 0xbc7e2e4d
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbc7e2e4d))

        data.write(b'\x15VM2')  # 0x15564d32
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x15564d32))

        data.write(b'\xf5G\x92`')  # 0xf5479260
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xf5479260))

        data.write(b"'\x1bdN")  # 0x271b644e
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x271b644e))

        data.write(b'R\xdc\x08\xc1')  # 0x52dc08c1
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x52dc08c1))

        data.write(b'\x99\x80\xdbd')  # 0x9980db64
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9980db64))

        data.write(b'#\xf5\x90W')  # 0x23f59057
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x23f59057))

        data.write(b'\xad=Z?')  # 0xad3d5a3f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xad3d5a3f))

        data.write(b'3\x15\xd2+')  # 0x3315d22b
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3315d22b))

        data.write(b'\x9e@\x07\xb6')  # 0x9e4007b6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x9e4007b6))

        data.write(b'z\x8d=F')  # 0x7a8d3d46
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7a8d3d46))

        data.write(b'+\x97\xd6L')  # 0x2b97d64c
        data.write(b'\x00\x01')  # size
        data.write(struct.pack('>?', self.unknown_0x2b97d64c))

        data.write(b'\xbd\xc5|\xe0')  # 0xbdc57ce0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xbdc57ce0))

        data.write(b'}Y\xc8T')  # 0x7d59c854
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x7d59c854))

        data.write(b'<N\xf7\xd2')  # 0x3c4ef7d2
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x3c4ef7d2))

        data.write(b'+H>\x9f')  # 0x2b483e9f
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x2b483e9f))

        data.write(b'poR\xfe')  # 0x706f52fe
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x706f52fe))

        data.write(b'b\xf9\xeb\xf6')  # 0x62f9ebf6
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x62f9ebf6))

        data.write(b'\xa9\xa58S')  # 0xa9a53853
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0xa9a53853))

        data.write(b'r+\x1b\xc0')  # 0x722b1bc0
        data.write(b'\x00\x04')  # size
        data.write(struct.pack('>f', self.unknown_0x722b1bc0))

        data.write(b'L?\xc93')  # 0x4c3fc933
        data.write(b'\x00\x10')  # size
        self.player_model_color.to_stream(data)

        data.write(b'Z\x87\xc1V')  # 0x5a87c156
        data.write(b'\x00\x10')  # size
        self.unknown_0x5a87c156.to_stream(data)

        data.write(b'\x9c\x0cS\x18')  # 0x9c0c5318
        data.write(b'\x00\x10')  # size
        self.player_surface_color.to_stream(data)

        data.write(b'*$~\xde')  # 0x2a247ede
        data.write(b'\x00\x10')  # size
        self.player_outline_color.to_stream(data)

        data.write(b'D0:\x9c')  # 0x44303a9c
        data.write(b'\x00\x10')  # size
        self.text_color.to_stream(data)

        data.write(b'\xf2\xe15\x06')  # 0xf2e13506
        data.write(b'\x00\x10')  # size
        self.text_outline_color.to_stream(data)

        data.write(b'\x1aK\x80h')  # 0x1a4b8068
        data.write(b'\x00\x10')  # size
        self.unknown_0x1a4b8068.to_stream(data)

        data.write(b'\xa4\x857,')  # 0xa485372c
        data.write(b'\x00\x10')  # size
        self.frame_color.to_stream(data)

        data.write(b'SfG\xd5')  # 0x536647d5
        data.write(b'\x00\x10')  # size
        self.title_color.to_stream(data)

        data.write(b'\xa6\xb63\xfa')  # 0xa6b633fa
        data.write(b'\x00\x10')  # size
        self.legend_background_color.to_stream(data)

        data.write(b'\x01\xce\xa7\xf9')  # 0x1cea7f9
        data.write(b'\x00\x10')  # size
        self.legend_gradient_color.to_stream(data)

    @classmethod
    def from_json(cls, data: json_util.JsonValue) -> typing_extensions.Self:
        json_data = typing.cast("TweakAutoMapper_BaseJson", data)
        return cls(
            unknown_0xcbe595d8=json_data['unknown_0xcbe595d8'],
            unknown_0x8ecb53a6=json_data['unknown_0x8ecb53a6'],
            scale_move_speed_with_camera_distance=json_data['scale_move_speed_with_camera_distance'],
            unknown_0x6bea9324=json_data['unknown_0x6bea9324'],
            unknown_0x065dd754=json_data['unknown_0x065dd754'],
            unknown_0x57a46c09=json_data['unknown_0x57a46c09'],
            unknown_0xb54255b5=json_data['unknown_0xb54255b5'],
            unknown_0x0c64cec4=json_data['unknown_0x0c64cec4'],
            unknown_0x335ebc7e=json_data['unknown_0x335ebc7e'],
            map_screen_area_opacity=json_data['map_screen_area_opacity'],
            unknown_0x533c5684=Color.from_json(json_data['unknown_0x533c5684']),
            unknown_0xeb383668=json_data['unknown_0xeb383668'],
            unknown_0x27151ede=json_data['unknown_0x27151ede'],
            unknown_0x434172c3=json_data['unknown_0x434172c3'],
            unknown_0x68097036=json_data['unknown_0x68097036'],
            unknown_0x03adcf46=Color.from_json(json_data['unknown_0x03adcf46']),
            unknown_0xd3fae283=Color.from_json(json_data['unknown_0xd3fae283']),
            unknown_0x65d2cf45=Color.from_json(json_data['unknown_0x65d2cf45']),
            unknown_0xb5752c08=Color.from_json(json_data['unknown_0xb5752c08']),
            unknown_0x035d01ce=Color.from_json(json_data['unknown_0x035d01ce']),
            unknown_0x805d5fa3=Color.from_json(json_data['unknown_0x805d5fa3']),
            unknown_0x36757265=Color.from_json(json_data['unknown_0x36757265']),
            unknown_0xe550fcbd=Color.from_json(json_data['unknown_0xe550fcbd']),
            unknown_0x5378d17b=Color.from_json(json_data['unknown_0x5378d17b']),
            unknown_0x0ebf3cbc=Color.from_json(json_data['unknown_0x0ebf3cbc']),
            unknown_0xb897117a=Color.from_json(json_data['unknown_0xb897117a']),
            unknown_0x3e670f6a=Color.from_json(json_data['unknown_0x3e670f6a']),
            unknown_0x884f22ac=Color.from_json(json_data['unknown_0x884f22ac']),
            unknown_0x7bdb0edf=json_data['unknown_0x7bdb0edf'],
            unknown_0x12221909=json_data['unknown_0x12221909'],
            unknown_0x38dbbc09=json_data['unknown_0x38dbbc09'],
            unknown_0x30610062=json_data['unknown_0x30610062'],
            unknown_0xb6acea88=json_data['unknown_0xb6acea88'],
            unknown_0x73de4110=json_data['unknown_0x73de4110'],
            map_screen_zoom_speed=json_data['map_screen_zoom_speed'],
            map_screen_circle_speed=json_data['map_screen_circle_speed'],
            map_screen_move_speed=json_data['map_screen_move_speed'],
            unknown_0xab82e268=Color.from_json(json_data['unknown_0xab82e268']),
            unknown_0x1daacfae=Color.from_json(json_data['unknown_0x1daacfae']),
            unknown_0xdad161a1=Color.from_json(json_data['unknown_0xdad161a1']),
            unknown_0x6cf94c67=Color.from_json(json_data['unknown_0x6cf94c67']),
            unknown_0x47967404=json_data['unknown_0x47967404'],
            unknown_0x0ece1950=json_data['unknown_0x0ece1950'],
            unknown_0x9ac1bdde=json_data['unknown_0x9ac1bdde'],
            unknown_0x97a19386=json_data['unknown_0x97a19386'],
            unknown_0xcb9e3a54=json_data['unknown_0xcb9e3a54'],
            unknown_0x2511a49b=json_data['unknown_0x2511a49b'],
            unknown_0x16c9f38e=json_data['unknown_0x16c9f38e'],
            unknown_0xbc7e2e4d=json_data['unknown_0xbc7e2e4d'],
            unknown_0x15564d32=json_data['unknown_0x15564d32'],
            unknown_0xf5479260=json_data['unknown_0xf5479260'],
            unknown_0x271b644e=json_data['unknown_0x271b644e'],
            unknown_0x52dc08c1=json_data['unknown_0x52dc08c1'],
            unknown_0x9980db64=json_data['unknown_0x9980db64'],
            unknown_0x23f59057=json_data['unknown_0x23f59057'],
            unknown_0xad3d5a3f=json_data['unknown_0xad3d5a3f'],
            unknown_0x3315d22b=json_data['unknown_0x3315d22b'],
            unknown_0x9e4007b6=json_data['unknown_0x9e4007b6'],
            unknown_0x7a8d3d46=json_data['unknown_0x7a8d3d46'],
            unknown_0x2b97d64c=json_data['unknown_0x2b97d64c'],
            unknown_0xbdc57ce0=json_data['unknown_0xbdc57ce0'],
            unknown_0x7d59c854=json_data['unknown_0x7d59c854'],
            unknown_0x3c4ef7d2=json_data['unknown_0x3c4ef7d2'],
            unknown_0x2b483e9f=json_data['unknown_0x2b483e9f'],
            unknown_0x706f52fe=json_data['unknown_0x706f52fe'],
            unknown_0x62f9ebf6=json_data['unknown_0x62f9ebf6'],
            unknown_0xa9a53853=json_data['unknown_0xa9a53853'],
            unknown_0x722b1bc0=json_data['unknown_0x722b1bc0'],
            player_model_color=Color.from_json(json_data['player_model_color']),
            unknown_0x5a87c156=Color.from_json(json_data['unknown_0x5a87c156']),
            player_surface_color=Color.from_json(json_data['player_surface_color']),
            player_outline_color=Color.from_json(json_data['player_outline_color']),
            text_color=Color.from_json(json_data['text_color']),
            text_outline_color=Color.from_json(json_data['text_outline_color']),
            unknown_0x1a4b8068=Color.from_json(json_data['unknown_0x1a4b8068']),
            frame_color=Color.from_json(json_data['frame_color']),
            title_color=Color.from_json(json_data['title_color']),
            legend_background_color=Color.from_json(json_data['legend_background_color']),
            legend_gradient_color=Color.from_json(json_data['legend_gradient_color']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'unknown_0xcbe595d8': self.unknown_0xcbe595d8,
            'unknown_0x8ecb53a6': self.unknown_0x8ecb53a6,
            'scale_move_speed_with_camera_distance': self.scale_move_speed_with_camera_distance,
            'unknown_0x6bea9324': self.unknown_0x6bea9324,
            'unknown_0x065dd754': self.unknown_0x065dd754,
            'unknown_0x57a46c09': self.unknown_0x57a46c09,
            'unknown_0xb54255b5': self.unknown_0xb54255b5,
            'unknown_0x0c64cec4': self.unknown_0x0c64cec4,
            'unknown_0x335ebc7e': self.unknown_0x335ebc7e,
            'map_screen_area_opacity': self.map_screen_area_opacity,
            'unknown_0x533c5684': self.unknown_0x533c5684.to_json(),
            'unknown_0xeb383668': self.unknown_0xeb383668,
            'unknown_0x27151ede': self.unknown_0x27151ede,
            'unknown_0x434172c3': self.unknown_0x434172c3,
            'unknown_0x68097036': self.unknown_0x68097036,
            'unknown_0x03adcf46': self.unknown_0x03adcf46.to_json(),
            'unknown_0xd3fae283': self.unknown_0xd3fae283.to_json(),
            'unknown_0x65d2cf45': self.unknown_0x65d2cf45.to_json(),
            'unknown_0xb5752c08': self.unknown_0xb5752c08.to_json(),
            'unknown_0x035d01ce': self.unknown_0x035d01ce.to_json(),
            'unknown_0x805d5fa3': self.unknown_0x805d5fa3.to_json(),
            'unknown_0x36757265': self.unknown_0x36757265.to_json(),
            'unknown_0xe550fcbd': self.unknown_0xe550fcbd.to_json(),
            'unknown_0x5378d17b': self.unknown_0x5378d17b.to_json(),
            'unknown_0x0ebf3cbc': self.unknown_0x0ebf3cbc.to_json(),
            'unknown_0xb897117a': self.unknown_0xb897117a.to_json(),
            'unknown_0x3e670f6a': self.unknown_0x3e670f6a.to_json(),
            'unknown_0x884f22ac': self.unknown_0x884f22ac.to_json(),
            'unknown_0x7bdb0edf': self.unknown_0x7bdb0edf,
            'unknown_0x12221909': self.unknown_0x12221909,
            'unknown_0x38dbbc09': self.unknown_0x38dbbc09,
            'unknown_0x30610062': self.unknown_0x30610062,
            'unknown_0xb6acea88': self.unknown_0xb6acea88,
            'unknown_0x73de4110': self.unknown_0x73de4110,
            'map_screen_zoom_speed': self.map_screen_zoom_speed,
            'map_screen_circle_speed': self.map_screen_circle_speed,
            'map_screen_move_speed': self.map_screen_move_speed,
            'unknown_0xab82e268': self.unknown_0xab82e268.to_json(),
            'unknown_0x1daacfae': self.unknown_0x1daacfae.to_json(),
            'unknown_0xdad161a1': self.unknown_0xdad161a1.to_json(),
            'unknown_0x6cf94c67': self.unknown_0x6cf94c67.to_json(),
            'unknown_0x47967404': self.unknown_0x47967404,
            'unknown_0x0ece1950': self.unknown_0x0ece1950,
            'unknown_0x9ac1bdde': self.unknown_0x9ac1bdde,
            'unknown_0x97a19386': self.unknown_0x97a19386,
            'unknown_0xcb9e3a54': self.unknown_0xcb9e3a54,
            'unknown_0x2511a49b': self.unknown_0x2511a49b,
            'unknown_0x16c9f38e': self.unknown_0x16c9f38e,
            'unknown_0xbc7e2e4d': self.unknown_0xbc7e2e4d,
            'unknown_0x15564d32': self.unknown_0x15564d32,
            'unknown_0xf5479260': self.unknown_0xf5479260,
            'unknown_0x271b644e': self.unknown_0x271b644e,
            'unknown_0x52dc08c1': self.unknown_0x52dc08c1,
            'unknown_0x9980db64': self.unknown_0x9980db64,
            'unknown_0x23f59057': self.unknown_0x23f59057,
            'unknown_0xad3d5a3f': self.unknown_0xad3d5a3f,
            'unknown_0x3315d22b': self.unknown_0x3315d22b,
            'unknown_0x9e4007b6': self.unknown_0x9e4007b6,
            'unknown_0x7a8d3d46': self.unknown_0x7a8d3d46,
            'unknown_0x2b97d64c': self.unknown_0x2b97d64c,
            'unknown_0xbdc57ce0': self.unknown_0xbdc57ce0,
            'unknown_0x7d59c854': self.unknown_0x7d59c854,
            'unknown_0x3c4ef7d2': self.unknown_0x3c4ef7d2,
            'unknown_0x2b483e9f': self.unknown_0x2b483e9f,
            'unknown_0x706f52fe': self.unknown_0x706f52fe,
            'unknown_0x62f9ebf6': self.unknown_0x62f9ebf6,
            'unknown_0xa9a53853': self.unknown_0xa9a53853,
            'unknown_0x722b1bc0': self.unknown_0x722b1bc0,
            'player_model_color': self.player_model_color.to_json(),
            'unknown_0x5a87c156': self.unknown_0x5a87c156.to_json(),
            'player_surface_color': self.player_surface_color.to_json(),
            'player_outline_color': self.player_outline_color.to_json(),
            'text_color': self.text_color.to_json(),
            'text_outline_color': self.text_outline_color.to_json(),
            'unknown_0x1a4b8068': self.unknown_0x1a4b8068.to_json(),
            'frame_color': self.frame_color.to_json(),
            'title_color': self.title_color.to_json(),
            'legend_background_color': self.legend_background_color.to_json(),
            'legend_gradient_color': self.legend_gradient_color.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        yield from []


def _decode_unknown_0xcbe595d8(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x8ecb53a6(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_scale_move_speed_with_camera_distance(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0x6bea9324(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x065dd754(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x57a46c09(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb54255b5(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0c64cec4(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x335ebc7e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_area_opacity(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x533c5684(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xeb383668(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x27151ede(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x434172c3(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x68097036(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x03adcf46(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xd3fae283(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x65d2cf45(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xb5752c08(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x035d01ce(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x805d5fa3(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x36757265(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xe550fcbd(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x5378d17b(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x0ebf3cbc(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xb897117a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x3e670f6a(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x884f22ac(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x7bdb0edf(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x12221909(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x38dbbc09(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x30610062(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xb6acea88(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x73de4110(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_zoom_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_circle_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_map_screen_move_speed(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xab82e268(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x1daacfae(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0xdad161a1(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x6cf94c67(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x47967404(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x0ece1950(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9ac1bdde(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x97a19386(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xcb9e3a54(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2511a49b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x16c9f38e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xbc7e2e4d(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x15564d32(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xf5479260(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x271b644e(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x52dc08c1(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9980db64(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x23f59057(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xad3d5a3f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3315d22b(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x9e4007b6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7a8d3d46(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2b97d64c(data: typing.BinaryIO, property_size: int) -> bool:
    return struct.unpack('>?', data.read(1))[0]


def _decode_unknown_0xbdc57ce0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x7d59c854(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x3c4ef7d2(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x2b483e9f(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x706f52fe(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x62f9ebf6(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0xa9a53853(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_unknown_0x722b1bc0(data: typing.BinaryIO, property_size: int) -> float:
    return struct.unpack('>f', data.read(4))[0]


def _decode_player_model_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x5a87c156(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_player_surface_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_player_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_text_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_text_outline_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_unknown_0x1a4b8068(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_frame_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_title_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_legend_background_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


def _decode_legend_gradient_color(data: typing.BinaryIO, property_size: int) -> Color:
    return Color.from_stream(data)


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0xcbe595d8: ('unknown_0xcbe595d8', _decode_unknown_0xcbe595d8),
    0x8ecb53a6: ('unknown_0x8ecb53a6', _decode_unknown_0x8ecb53a6),
    0x30b13740: ('scale_move_speed_with_camera_distance', _decode_scale_move_speed_with_camera_distance),
    0x6bea9324: ('unknown_0x6bea9324', _decode_unknown_0x6bea9324),
    0x65dd754: ('unknown_0x065dd754', _decode_unknown_0x065dd754),
    0x57a46c09: ('unknown_0x57a46c09', _decode_unknown_0x57a46c09),
    0xb54255b5: ('unknown_0xb54255b5', _decode_unknown_0xb54255b5),
    0xc64cec4: ('unknown_0x0c64cec4', _decode_unknown_0x0c64cec4),
    0x335ebc7e: ('unknown_0x335ebc7e', _decode_unknown_0x335ebc7e),
    0x45be3f6b: ('map_screen_area_opacity', _decode_map_screen_area_opacity),
    0x533c5684: ('unknown_0x533c5684', _decode_unknown_0x533c5684),
    0xeb383668: ('unknown_0xeb383668', _decode_unknown_0xeb383668),
    0x27151ede: ('unknown_0x27151ede', _decode_unknown_0x27151ede),
    0x434172c3: ('unknown_0x434172c3', _decode_unknown_0x434172c3),
    0x68097036: ('unknown_0x68097036', _decode_unknown_0x68097036),
    0x3adcf46: ('unknown_0x03adcf46', _decode_unknown_0x03adcf46),
    0xd3fae283: ('unknown_0xd3fae283', _decode_unknown_0xd3fae283),
    0x65d2cf45: ('unknown_0x65d2cf45', _decode_unknown_0x65d2cf45),
    0xb5752c08: ('unknown_0xb5752c08', _decode_unknown_0xb5752c08),
    0x35d01ce: ('unknown_0x035d01ce', _decode_unknown_0x035d01ce),
    0x805d5fa3: ('unknown_0x805d5fa3', _decode_unknown_0x805d5fa3),
    0x36757265: ('unknown_0x36757265', _decode_unknown_0x36757265),
    0xe550fcbd: ('unknown_0xe550fcbd', _decode_unknown_0xe550fcbd),
    0x5378d17b: ('unknown_0x5378d17b', _decode_unknown_0x5378d17b),
    0xebf3cbc: ('unknown_0x0ebf3cbc', _decode_unknown_0x0ebf3cbc),
    0xb897117a: ('unknown_0xb897117a', _decode_unknown_0xb897117a),
    0x3e670f6a: ('unknown_0x3e670f6a', _decode_unknown_0x3e670f6a),
    0x884f22ac: ('unknown_0x884f22ac', _decode_unknown_0x884f22ac),
    0x7bdb0edf: ('unknown_0x7bdb0edf', _decode_unknown_0x7bdb0edf),
    0x12221909: ('unknown_0x12221909', _decode_unknown_0x12221909),
    0x38dbbc09: ('unknown_0x38dbbc09', _decode_unknown_0x38dbbc09),
    0x30610062: ('unknown_0x30610062', _decode_unknown_0x30610062),
    0xb6acea88: ('unknown_0xb6acea88', _decode_unknown_0xb6acea88),
    0x73de4110: ('unknown_0x73de4110', _decode_unknown_0x73de4110),
    0x19069725: ('map_screen_zoom_speed', _decode_map_screen_zoom_speed),
    0x5ba0de1e: ('map_screen_circle_speed', _decode_map_screen_circle_speed),
    0x310b37a1: ('map_screen_move_speed', _decode_map_screen_move_speed),
    0xab82e268: ('unknown_0xab82e268', _decode_unknown_0xab82e268),
    0x1daacfae: ('unknown_0x1daacfae', _decode_unknown_0x1daacfae),
    0xdad161a1: ('unknown_0xdad161a1', _decode_unknown_0xdad161a1),
    0x6cf94c67: ('unknown_0x6cf94c67', _decode_unknown_0x6cf94c67),
    0x47967404: ('unknown_0x47967404', _decode_unknown_0x47967404),
    0xece1950: ('unknown_0x0ece1950', _decode_unknown_0x0ece1950),
    0x9ac1bdde: ('unknown_0x9ac1bdde', _decode_unknown_0x9ac1bdde),
    0x97a19386: ('unknown_0x97a19386', _decode_unknown_0x97a19386),
    0xcb9e3a54: ('unknown_0xcb9e3a54', _decode_unknown_0xcb9e3a54),
    0x2511a49b: ('unknown_0x2511a49b', _decode_unknown_0x2511a49b),
    0x16c9f38e: ('unknown_0x16c9f38e', _decode_unknown_0x16c9f38e),
    0xbc7e2e4d: ('unknown_0xbc7e2e4d', _decode_unknown_0xbc7e2e4d),
    0x15564d32: ('unknown_0x15564d32', _decode_unknown_0x15564d32),
    0xf5479260: ('unknown_0xf5479260', _decode_unknown_0xf5479260),
    0x271b644e: ('unknown_0x271b644e', _decode_unknown_0x271b644e),
    0x52dc08c1: ('unknown_0x52dc08c1', _decode_unknown_0x52dc08c1),
    0x9980db64: ('unknown_0x9980db64', _decode_unknown_0x9980db64),
    0x23f59057: ('unknown_0x23f59057', _decode_unknown_0x23f59057),
    0xad3d5a3f: ('unknown_0xad3d5a3f', _decode_unknown_0xad3d5a3f),
    0x3315d22b: ('unknown_0x3315d22b', _decode_unknown_0x3315d22b),
    0x9e4007b6: ('unknown_0x9e4007b6', _decode_unknown_0x9e4007b6),
    0x7a8d3d46: ('unknown_0x7a8d3d46', _decode_unknown_0x7a8d3d46),
    0x2b97d64c: ('unknown_0x2b97d64c', _decode_unknown_0x2b97d64c),
    0xbdc57ce0: ('unknown_0xbdc57ce0', _decode_unknown_0xbdc57ce0),
    0x7d59c854: ('unknown_0x7d59c854', _decode_unknown_0x7d59c854),
    0x3c4ef7d2: ('unknown_0x3c4ef7d2', _decode_unknown_0x3c4ef7d2),
    0x2b483e9f: ('unknown_0x2b483e9f', _decode_unknown_0x2b483e9f),
    0x706f52fe: ('unknown_0x706f52fe', _decode_unknown_0x706f52fe),
    0x62f9ebf6: ('unknown_0x62f9ebf6', _decode_unknown_0x62f9ebf6),
    0xa9a53853: ('unknown_0xa9a53853', _decode_unknown_0xa9a53853),
    0x722b1bc0: ('unknown_0x722b1bc0', _decode_unknown_0x722b1bc0),
    0x4c3fc933: ('player_model_color', _decode_player_model_color),
    0x5a87c156: ('unknown_0x5a87c156', _decode_unknown_0x5a87c156),
    0x9c0c5318: ('player_surface_color', _decode_player_surface_color),
    0x2a247ede: ('player_outline_color', _decode_player_outline_color),
    0x44303a9c: ('text_color', _decode_text_color),
    0xf2e13506: ('text_outline_color', _decode_text_outline_color),
    0x1a4b8068: ('unknown_0x1a4b8068', _decode_unknown_0x1a4b8068),
    0xa485372c: ('frame_color', _decode_frame_color),
    0x536647d5: ('title_color', _decode_title_color),
    0xa6b633fa: ('legend_background_color', _decode_legend_background_color),
    0x1cea7f9: ('legend_gradient_color', _decode_legend_gradient_color),
}
