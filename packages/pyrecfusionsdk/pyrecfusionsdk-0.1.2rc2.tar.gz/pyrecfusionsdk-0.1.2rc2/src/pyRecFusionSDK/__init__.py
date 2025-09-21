import os
import sys
from pathlib import Path
from typing import Iterable

import numpy as np

# Usually, the package compilation on non-win32 system will fail, so
# we shouldn't even be here... but just in case!
if sys.platform != "win32":
    raise OSError("pyRecFusionSDK works only on Windows")

default_dll_dir: list[Path] = [
    # Path used for local development
    Path(os.getcwd()).joinpath("third-party", "RecFusionSDK", "bin"),
]
# When installed, RecFusion SDK populates the RECFUSION_SDK env variable
# to the root directory of the SDK.
if "RECFUSION_SDK" in os.environ:
    default_dll_dir.insert(0, Path(os.environ["RECFUSION_SDK"], "bin"))

found_dll = False
for dll_dir in default_dll_dir:
    if dll_dir.exists():
        # Make sure the RecFusionSDK.dll is really there
        rf_dll_path = dll_dir.joinpath("RecFusionSDK.dll")
        if rf_dll_path.exists() and rf_dll_path.is_file():
            os.add_dll_directory(dll_dir)
            found_dll = True
            break

if not found_dll:
    raise ImportError(
        f"Couldn't find working installation of RecFusionSDK. Tried: "
        f"{default_dll_dir}. Set up RECFUSION_SDK env variable to the "
        f"RecFusion SDK root directory or reinstall the SDK."
    )

# Export all symbols
from ._pyRecFusionSDK_impl import *

# And hidden ones!
from ._pyRecFusionSDK_impl import (
    _ColorImage,
    _DepthImage,
    _Mat3,
    _Mat4,
    _SensorFormat,
    _Vec3,
    _Vec3i,
)


class SensorFormat(_SensorFormat):
    def __repr__(self):
        return f"SensorFormat(width={self.width}, height={self.height}, fps={self.fps})"

    def __str__(self):
        return f"{self.width}x{self.height}@{self.fps})"


class Mat3(_Mat3):
    def __init__(self, data: np.ndarray | Iterable):
        super().__init__(np.asarray(data))

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return f"Mat3({self.data.tolist()})"


class Mat4(_Mat4):
    def __init__(self, data: np.ndarray | Iterable):
        super().__init__(np.asarray(data))

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return f"Mat4({self.data.tolist()})"


class Vec3(_Vec3):
    def __repr__(self):
        return f"Vec3(x={self.x}, y={self.y}, z={self.z})"


class Vec3i(_Vec3i):
    def __repr__(self):
        return f"Vec3i(x={self.x}, y={self.y}, z={self.z})"


class ColorImage(_ColorImage):
    def __init__(self, array):
        super().__init__(array)

    @classmethod
    def allocate(cls, width, height):
        array = np.zeros((height, width, 3), dtype=np.ubyte)
        return cls(array)

    @classmethod
    def allocate_for_sensor(cls, sensor):
        array = np.zeros((sensor.color_height, sensor.color_width, 3), dtype=np.ubyte)
        return cls(array)

    def __repr__(self):
        return f"ColorImage(width={self.width}, height={self.height})"

    @property
    def channels(self):
        return self.data.shape[2]


class DepthImage(_DepthImage):
    def __init__(self, array):
        super().__init__(array)

    @classmethod
    def allocate(cls, width, height):
        array = np.zeros((height, width), dtype=np.single)
        return cls(array)

    @classmethod
    def allocate_for_sensor(cls, sensor):
        array = np.zeros((sensor.depth_height, sensor.depth_width), dtype=np.single)
        return cls(array)

    def __repr__(self):
        return f"DepthImage(width={self.width}, height={self.height})"


# __all__ = ["Vec3", "Vec3i", "Mat3", "Mat4"]
