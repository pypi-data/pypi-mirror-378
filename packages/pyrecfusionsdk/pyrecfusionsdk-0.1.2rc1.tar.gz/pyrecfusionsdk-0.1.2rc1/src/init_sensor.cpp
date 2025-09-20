#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <nanobind/stl/tuple.h>
#include <nanobind/stl/vector.h>
#include <nanobind/trampoline.h>

using std::string, std::make_tuple, std::vector;
namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

struct PySensorListener : public SensorListener {
  NB_TRAMPOLINE(SensorListener, 1);

  void onSensorData(const ColorImage &colorImg,
                    const DepthImage &depthImg) override {
    NB_OVERRIDE_PURE(onSensorData, colorImg, depthImg);
  }
};

void init_sensor(nb::module_ &m) {
  nb::class_<Sensor>(m, "Sensor",
                     "Class providing access to RGB-D sensors supported by "
                     "RecFusion, use SensorManager for instantiation.")
      .def_prop_ro(
          "device_name",
          [](Sensor &sensor) {
            char buffer[256];
            auto result = sensor.deviceName(buffer, 256);
            if (result == -2)
              return string("buffer_too_small");
            if (result == -1)
              return string("sensor_manager_non_existing");
            return string(buffer, result);
          },
          "Get sensor name.")
      .def_prop_ro(
          "uuid",
          [](Sensor &sensor) {
            char buffer[256];
            auto result = sensor.uuid(buffer, 256);
            if (result == -2)
              return string("buffer_too_small");
            if (result == -1)
              return string("sensor_manager_non_existing");
            return string(buffer, result);
          },
          "Get sensor UUID.")
      .def("depth_format_count", &Sensor::depthFormatCount,
           "Returns a number of depth stream formats supported by the sensor. "
           "Returns 0 if available formats could not be queried. Must be "
           "called before depth formats can be queried.")
      .def("color_format_count", &Sensor::colorFormatCount,
           "Returns a number of color stream formats supported by the sensor. "
           "Returns 0 if available formats could not be queried. Must be "
           "called before color formats can be queried.")
      .def("depth_format", &Sensor::depthFormat, "id"_a,
           "Get a depth stream format. depthFormatCount() must be called "
           "first. Return stream format. All values are set to 0 if invalid "
           "index is provided.")
      .def("color_format", &Sensor::colorFormat, "id"_a,
           "Get a color stream format. colorFormatCount() must be called "
           "first. Return stream format. All values are set to 0 if invalid "
           "index is provided.")
      .def("open", &Sensor::open, "color_width"_a = 640, "color_height"_a = 480,
           "depth_width"_a = 640, "depth_height"_a = 480, "max_fps"_a = 30,
           "Open sensor. Must be called before any other functions can be "
           "used. Return True if sensor supports the requested resolution on "
           "both depth and color sensor and could be opened, false otherwise.")
      .def("close", &Sensor::close, "Close sensor.")
      .def("start", &Sensor::start, "Start listener-based data capture.")
      .def("stop", &Sensor::stop, "Stop listener-based data capture.")
      .def_prop_ro("is_open", &Sensor::isOpen,
                   "True when sensor is open and ready for acquisition.")
      .def_prop_ro("depth_width", &Sensor::depthWidth,
                   "Width of depth image returned by the sensor.")
      .def_prop_ro("depth_height", &Sensor::depthHeight,
                   "Height of depth image returned by the sensor.")
      .def_prop_ro("color_width", &Sensor::colorWidth,
                   "Width of color image returned by sensor.")
      .def_prop_ro("color_height", &Sensor::colorHeight,
                   "Height of color image returned by sensor.")
      .def_prop_ro("depth_intrinsics", &Sensor::depthIntrinsics,
                   "Depth sensor intrinsics as 3x3 matrix. Returns zero matrix "
                   "when no depth intrinsics are available.")
      .def_prop_ro("color_intrinsics", &Sensor::colorIntrinsics,
                   "Color sensor intrnsics as 3x3 matrix. Returns zero matrix "
                   "when no color intrinsics are available.")
      .def_prop_ro("depth_to_color_transformation",
                   &Sensor::depthToColorTransformation,
                   "Depth to color transformation as 4x4 matrix. Returns zero "
                   "matrix when no transformation is available.")
      .def_prop_ro("supports_color", &Sensor::supportsColor,
                   "True if sensor supports color.")
      .def("set_laser_state", &Sensor::setLaserState,
           "Turn laser on or off. The availabilty of this option depends "
           "heavily on sensors and their drivers.")
      .def_prop_ro("supports_auto_white_balance",
                   &Sensor::supportsAutoWhiteBalance,
                   "True if sensor supports auto white-balance.")
      .def("set_auto_white_balance_enabled",
           &Sensor::setAutoWhiteBalanceEnabled, "Set auto white-balance state.")
      .def_prop_ro("is_auto_white_balance_enabled",
                   &Sensor::isAutoWhiteBalanceEnabled,
                   "True if auto white-balance is enabled.")
      .def_prop_ro("supports_auto_exposure", &Sensor::supportsAutoExposure,
                   "True if sensor supports auto exposure.")
      .def("set_auto_exposure_enabled", &Sensor::setAutoExposureEnabled,
           "Set auto exposure state.")
      .def_prop_ro("is_auto_exposure_enabled", &Sensor::isAutoExposureEnabled,
                   "True if auto exposure is enabled.")
      .def("set_exposure", &Sensor::setExposure, "exposure_time_ms"_a,
           "Set auto exposure to specified value in ms. Only works when auto "
           "exposure is disabled.")
      .def_prop_ro("exposure", &Sensor::exposure,
                   "Get exposure time in non-auto mode in ms.")
      .def(
          "add_listener",
          [](Sensor &sensor, SensorListener &listener) {
            sensor.addListener(&listener);
          },
          "listener"_a, "Register sensor listener.")
      .def("remove_listener", &Sensor::removeListener, "listener"_a,
           "Remove previously registered sensor listener.")
      .def("read_image", &Sensor::readImage, "img_depth"_a, "img_color"_a,
           "timeout"_a = 2000,
           "Read image from sensor. The images passed in need to be allocated "
           "by the caller.")
      // New API
      .def_prop_ro(
          "image_size",
          [](Sensor &sensor) {
            return make_tuple(sensor.colorWidth(), sensor.colorHeight(),
                              sensor.depthWidth(), sensor.depthHeight());
          },
          "Return a tuple with color and depth image sizes.")
      .def_prop_ro(
          "depth_formats",
          [](Sensor &sensor) {
            vector<Sensor::Format> formats;
            for (int i = 0; i < sensor.depthFormatCount(); ++i) {
              formats.emplace_back(sensor.depthFormat(i));
            }
            return formats;
          },
          "Return all available depth formats for this sensor.")
      .def_prop_ro(
          "color_formats",
          [](Sensor &sensor) {
            vector<Sensor::Format> formats;
            for (int i = 0; i < sensor.colorFormatCount(); ++i) {
              formats.emplace_back(sensor.colorFormat(i));
            }
            return formats;
          },
          "Return all available color formats for this sensor.");

  nb::class_<Sensor::Format>(
      m, "_SensorFormat",
      "Structure representing the sensor format of depth and color cameras.")
      .def_ro("width", &Sensor::Format::width, "Image width.")
      .def_ro("height", &Sensor::Format::height, "Image height.")
      .def_ro("fps", &Sensor::Format::fps, "Image frame per seconds (fps).");
  // New API
  // .def("__repr__", [](Sensor::Format &format) {
  //   return to_string(format.width) + "x" + to_string(format.height) + "@"
  //   +
  //          to_string(format.fps) + "fps";
  // });

  nb::class_<SensorListener, PySensorListener>(
      m, "SensorListener", "Listener interface for RGB-D sensor data.")
      .def(nb::init<>(), "Construct the listener.")
      .def("on_sensor_data", &SensorListener::onSensorData,
           "Called when new RGB-D data is available. Data is owned by calling "
           "instance.");
}
