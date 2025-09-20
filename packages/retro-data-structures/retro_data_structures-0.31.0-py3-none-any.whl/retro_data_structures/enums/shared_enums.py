# Generated File
import typing

import retro_data_structures.enums.corruption as _corruption_enums
import retro_data_structures.enums.echoes as _echoes_enums
import retro_data_structures.enums.prime as _prime_enums
import retro_data_structures.enums.prime_remastered as _prime_remastered_enums

Message = typing.Union[
    _prime_enums.Message,
    _echoes_enums.Message,
    _corruption_enums.Message
]
PlayerItemEnum = typing.Union[
    _prime_enums.PlayerItemEnum,
    _echoes_enums.PlayerItemEnum,
    _corruption_enums.PlayerItemEnum,
    _prime_remastered_enums.PlayerItemEnum
]
ScanSpeedEnum = typing.Union[
    _prime_enums.ScanSpeedEnum,
    _echoes_enums.ScanSpeedEnum,
    _corruption_enums.ScanSpeedEnum
]
State = typing.Union[
    _prime_enums.State,
    _echoes_enums.State,
    _corruption_enums.State
]
WeaponTypeEnum = typing.Union[
    _prime_enums.WeaponTypeEnum,
    _echoes_enums.WeaponTypeEnum
]
