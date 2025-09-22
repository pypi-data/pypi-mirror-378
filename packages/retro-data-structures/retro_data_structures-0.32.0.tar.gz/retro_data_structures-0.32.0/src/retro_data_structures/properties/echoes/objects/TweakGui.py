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
from retro_data_structures.properties.echoes.archetypes.TweakGui_Completion import TweakGui_Completion
from retro_data_structures.properties.echoes.archetypes.TweakGui_Credits import TweakGui_Credits
from retro_data_structures.properties.echoes.archetypes.TweakGui_DarkVisor import TweakGui_DarkVisor
from retro_data_structures.properties.echoes.archetypes.TweakGui_EchoVisor import TweakGui_EchoVisor
from retro_data_structures.properties.echoes.archetypes.TweakGui_LogBook import TweakGui_LogBook
from retro_data_structures.properties.echoes.archetypes.TweakGui_Misc import TweakGui_Misc
from retro_data_structures.properties.echoes.archetypes.TweakGui_MovieVolumes import TweakGui_MovieVolumes
from retro_data_structures.properties.echoes.archetypes.TweakGui_ScanVisor import TweakGui_ScanVisor
from retro_data_structures.properties.echoes.archetypes.TweakGui_ScannableObjectDownloadTimes import TweakGui_ScannableObjectDownloadTimes

if typing.TYPE_CHECKING:
    from retro_data_structures.asset_manager import AssetManager
    from retro_data_structures.base_resource import Dependency

    class TweakGuiJson(typing_extensions.TypedDict):
        instance_name: str
        misc: json_util.JsonObject
        scannable_object_download_times: json_util.JsonObject
        unknown: json_util.JsonObject
        echo_visor: json_util.JsonObject
        scan_visor: json_util.JsonObject
        log_book: json_util.JsonObject
        credits: json_util.JsonObject
        completion: json_util.JsonObject
        movie_volumes: json_util.JsonObject
    

@dataclasses.dataclass()
class TweakGui(BaseObjectType):
    instance_name: str = dataclasses.field(default='', metadata={
        'reflection': FieldReflection[str](
            str, id=0x7fda1466, original_name='InstanceName'
        ),
    })
    misc: TweakGui_Misc = dataclasses.field(default_factory=TweakGui_Misc, metadata={
        'reflection': FieldReflection[TweakGui_Misc](
            TweakGui_Misc, id=0xd45f7663, original_name='Misc', from_json=TweakGui_Misc.from_json, to_json=TweakGui_Misc.to_json
        ),
    })
    scannable_object_download_times: TweakGui_ScannableObjectDownloadTimes = dataclasses.field(default_factory=TweakGui_ScannableObjectDownloadTimes, metadata={
        'reflection': FieldReflection[TweakGui_ScannableObjectDownloadTimes](
            TweakGui_ScannableObjectDownloadTimes, id=0x80b13e60, original_name='ScannableObjectDownloadTimes', from_json=TweakGui_ScannableObjectDownloadTimes.from_json, to_json=TweakGui_ScannableObjectDownloadTimes.to_json
        ),
    })
    unknown: TweakGui_DarkVisor = dataclasses.field(default_factory=TweakGui_DarkVisor, metadata={
        'reflection': FieldReflection[TweakGui_DarkVisor](
            TweakGui_DarkVisor, id=0x102aa38d, original_name='Unknown', from_json=TweakGui_DarkVisor.from_json, to_json=TweakGui_DarkVisor.to_json
        ),
    })
    echo_visor: TweakGui_EchoVisor = dataclasses.field(default_factory=TweakGui_EchoVisor, metadata={
        'reflection': FieldReflection[TweakGui_EchoVisor](
            TweakGui_EchoVisor, id=0x2b698e45, original_name='EchoVisor', from_json=TweakGui_EchoVisor.from_json, to_json=TweakGui_EchoVisor.to_json
        ),
    })
    scan_visor: TweakGui_ScanVisor = dataclasses.field(default_factory=TweakGui_ScanVisor, metadata={
        'reflection': FieldReflection[TweakGui_ScanVisor](
            TweakGui_ScanVisor, id=0x40ffb3c4, original_name='ScanVisor', from_json=TweakGui_ScanVisor.from_json, to_json=TweakGui_ScanVisor.to_json
        ),
    })
    log_book: TweakGui_LogBook = dataclasses.field(default_factory=TweakGui_LogBook, metadata={
        'reflection': FieldReflection[TweakGui_LogBook](
            TweakGui_LogBook, id=0x97b8a76a, original_name='LogBook', from_json=TweakGui_LogBook.from_json, to_json=TweakGui_LogBook.to_json
        ),
    })
    credits: TweakGui_Credits = dataclasses.field(default_factory=TweakGui_Credits, metadata={
        'reflection': FieldReflection[TweakGui_Credits](
            TweakGui_Credits, id=0x77393416, original_name='Credits', from_json=TweakGui_Credits.from_json, to_json=TweakGui_Credits.to_json
        ),
    })
    completion: TweakGui_Completion = dataclasses.field(default_factory=TweakGui_Completion, metadata={
        'reflection': FieldReflection[TweakGui_Completion](
            TweakGui_Completion, id=0x02149892, original_name='Completion', from_json=TweakGui_Completion.from_json, to_json=TweakGui_Completion.to_json
        ),
    })
    movie_volumes: TweakGui_MovieVolumes = dataclasses.field(default_factory=TweakGui_MovieVolumes, metadata={
        'reflection': FieldReflection[TweakGui_MovieVolumes](
            TweakGui_MovieVolumes, id=0xa4f61e92, original_name='MovieVolumes', from_json=TweakGui_MovieVolumes.from_json, to_json=TweakGui_MovieVolumes.to_json
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
        return 'TWGU'

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
        if property_count != 10:
            return None
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x7fda1466
        instance_name = data.read(property_size)[:-1].decode("utf-8")
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xd45f7663
        misc = TweakGui_Misc.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x80b13e60
        scannable_object_download_times = TweakGui_ScannableObjectDownloadTimes.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x102aa38d
        unknown = TweakGui_DarkVisor.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x2b698e45
        echo_visor = TweakGui_EchoVisor.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x40ffb3c4
        scan_visor = TweakGui_ScanVisor.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x97b8a76a
        log_book = TweakGui_LogBook.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x77393416
        credits = TweakGui_Credits.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0x02149892
        completion = TweakGui_Completion.from_stream(data, property_size)
    
        property_id, property_size = struct.unpack(">LH", data.read(6))
        assert property_id == 0xa4f61e92
        movie_volumes = TweakGui_MovieVolumes.from_stream(data, property_size)
    
        return cls(instance_name, misc, scannable_object_download_times, unknown, echo_visor, scan_visor, log_book, credits, completion, movie_volumes)

    def to_stream(self, data: typing.BinaryIO, default_override: dict | None = None) -> None:
        default_override = default_override or {}
        data.write(b'\xff\xff\xff\xff')  # struct object id
        root_size_offset = data.tell()
        data.write(b'\x00\x00')  # placeholder for root struct size
        data.write(b'\x00\n')  # 10 properties

        data.write(b'\x7f\xda\x14f')  # 0x7fda1466
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        data.write(self.instance_name.encode("utf-8"))
        data.write(b'\x00')
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xd4_vc')  # 0xd45f7663
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.misc.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x80\xb1>`')  # 0x80b13e60
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.scannable_object_download_times.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x10*\xa3\x8d')  # 0x102aa38d
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.unknown.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'+i\x8eE')  # 0x2b698e45
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.echo_visor.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'@\xff\xb3\xc4')  # 0x40ffb3c4
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.scan_visor.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x97\xb8\xa7j')  # 0x97b8a76a
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.log_book.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'w94\x16')  # 0x77393416
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.credits.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\x02\x14\x98\x92')  # 0x2149892
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.completion.to_stream(data)
        after = data.tell()
        data.seek(before)
        data.write(struct.pack(">H", after - before - 2))
        data.seek(after)

        data.write(b'\xa4\xf6\x1e\x92')  # 0xa4f61e92
        before = data.tell()
        data.write(b'\x00\x00')  # size placeholder
        self.movie_volumes.to_stream(data)
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
        json_data = typing.cast("TweakGuiJson", data)
        return cls(
            instance_name=json_data['instance_name'],
            misc=TweakGui_Misc.from_json(json_data['misc']),
            scannable_object_download_times=TweakGui_ScannableObjectDownloadTimes.from_json(json_data['scannable_object_download_times']),
            unknown=TweakGui_DarkVisor.from_json(json_data['unknown']),
            echo_visor=TweakGui_EchoVisor.from_json(json_data['echo_visor']),
            scan_visor=TweakGui_ScanVisor.from_json(json_data['scan_visor']),
            log_book=TweakGui_LogBook.from_json(json_data['log_book']),
            credits=TweakGui_Credits.from_json(json_data['credits']),
            completion=TweakGui_Completion.from_json(json_data['completion']),
            movie_volumes=TweakGui_MovieVolumes.from_json(json_data['movie_volumes']),
        )

    def to_json(self) -> json_util.JsonObject:
        return {
            'instance_name': self.instance_name,
            'misc': self.misc.to_json(),
            'scannable_object_download_times': self.scannable_object_download_times.to_json(),
            'unknown': self.unknown.to_json(),
            'echo_visor': self.echo_visor.to_json(),
            'scan_visor': self.scan_visor.to_json(),
            'log_book': self.log_book.to_json(),
            'credits': self.credits.to_json(),
            'completion': self.completion.to_json(),
            'movie_volumes': self.movie_volumes.to_json(),
        }

    def dependencies_for(self, asset_manager: AssetManager) -> typing.Iterator[Dependency]:
        for method, field_name, field_type in [
            (self.misc.dependencies_for, "misc", "TweakGui_Misc"),
            (self.scannable_object_download_times.dependencies_for, "scannable_object_download_times", "TweakGui_ScannableObjectDownloadTimes"),
            (self.unknown.dependencies_for, "unknown", "TweakGui_DarkVisor"),
            (self.echo_visor.dependencies_for, "echo_visor", "TweakGui_EchoVisor"),
            (self.scan_visor.dependencies_for, "scan_visor", "TweakGui_ScanVisor"),
            (self.log_book.dependencies_for, "log_book", "TweakGui_LogBook"),
            (self.credits.dependencies_for, "credits", "TweakGui_Credits"),
            (self.completion.dependencies_for, "completion", "TweakGui_Completion"),
            (self.movie_volumes.dependencies_for, "movie_volumes", "TweakGui_MovieVolumes"),
        ]:
            try:
                yield from method(asset_manager)
            except Exception as e:
                raise Exception(
                    f"Error finding dependencies for TweakGui.{field_name} ({field_type}): {e}"
                )


def _decode_instance_name(data: typing.BinaryIO, property_size: int) -> str:
    return data.read(property_size)[:-1].decode("utf-8")


_property_decoder: dict[int, tuple[str, typing.Callable[[typing.BinaryIO, int], typing.Any]]] = {
    0x7fda1466: ('instance_name', _decode_instance_name),
    0xd45f7663: ('misc', TweakGui_Misc.from_stream),
    0x80b13e60: ('scannable_object_download_times', TweakGui_ScannableObjectDownloadTimes.from_stream),
    0x102aa38d: ('unknown', TweakGui_DarkVisor.from_stream),
    0x2b698e45: ('echo_visor', TweakGui_EchoVisor.from_stream),
    0x40ffb3c4: ('scan_visor', TweakGui_ScanVisor.from_stream),
    0x97b8a76a: ('log_book', TweakGui_LogBook.from_stream),
    0x77393416: ('credits', TweakGui_Credits.from_stream),
    0x2149892: ('completion', TweakGui_Completion.from_stream),
    0xa4f61e92: ('movie_volumes', TweakGui_MovieVolumes.from_stream),
}
