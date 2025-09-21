# pyRecFusionSDK

Easy multi-sensor mesh reconstruction with Python bindings to RecFusion SDK (C++).

## Changes to original API

This project slightly modifies or adds new functionalites to the original RecFusion SDK API:

- RecFusionSDK version string: `version() -> str`
- Open all available sensors: `SensorManager.open_all() -> list[Sensor]`
- Open any available sensor: `SensorManager.open_any() -> Sensor | None`
- Obtain list of sensor color and depth formats:
  - `Sensor.color_formats: list[SensorFormat]`
  - `Sensor.depth_formats: list[SensorFormat]`
- Initialize playback recorder using sensor options: `RFSRecorder.init_from_sensor(sensor: Sensor) -> None`
- Initialize empty `ColorImage` and `DepthImage` for a given `Sensor` (using its resolution etc.):
  - `ColorIamge.allocate_for_sensor(sensor: Sensor) -> ColorImage`
  - `DepthIamge.allocate_for_sensor(sensor: Sensor) -> DepthImage`
- Save images to \*.png files:
  - `ColorImage.to_image(filename: str, compression: int = 3) -> None`
  - `DepthImage.to_image(filename: str, compression: int = 3) -> None`

## Usage

Requirements:
* Installed locally the [RecFusion SDK](https://www.recfusion.net/download-recfusion/)

Then:

```shell
pip install pyRecFusionSDK
```
## Publish new version to PyPi

1. Remove `dist/` and `build/`
2. Run `uv build --sdist`
3. Run `uv publish`
4. Type the token!

## Examples

We provide several examples of using RecFusionSDK with Python:

- [capture_playback.py](./examples/capture_playback.py) - capture sequence of images as playback file (\*.rfs)
- [capture_png.py](./examples/capture_png.py) - capture single frame to image (\*.png)
- [machine_token.py](./examples/machine_token.py) - display machine token required for offline license
- [reconstruct_from_playback.py](./examples/reconstruct_from_playback.py) - reconstruct mesh from playback file (\*.rfs)
- [reconstruct_sensor.py](./examples/reconstruct_sensor.py) - reconstruct mesh directly from sensor data
- [reconstruct_sensor_listener.py](./examples/reconstruct_sensor_listener.py) - (NOT WORKING) reconstruct mesh directly from sensor data using sensor listener
- [show_sensor_info.py](./examples/show_sensor_info.py) - show information about sensor (e.g. model, UUID, resolutions)
