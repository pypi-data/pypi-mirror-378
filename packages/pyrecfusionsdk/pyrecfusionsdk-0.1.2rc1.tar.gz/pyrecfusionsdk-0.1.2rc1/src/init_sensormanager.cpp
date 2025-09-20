#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/vector.h>

using std::vector;
namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_sensormanager(nb::module_ &m) {
  // TODO: I am not sure, how to correctly manage the liveness of this object,
  //       as the wrapped SensorManger cannot be destructed as long as sensors
  //       are in use.
  nb::class_<SensorManager>(m, "SensorManager",
                            "Class for instantiating RGB-D sensors supported "
                            "by RecFusion. It needs to exist as long as the "
                            "instantiated sensors are in use.")
      .def(nb::init<>(), "Construct the sensor manager.")
      .def_prop_ro("device_count", &SensorManager::deviceCount,
                   "Get number of available sensors.")
      .def("sensor", &SensorManager::sensor, "id"_a, nb::rv_policy::reference,
           "Get sensor by its ID. Sensor ID is in the range from 0 to "
           "`.device_count - 1`. The caller is NOT responsible for the memory "
           "deallocation. Memory will be deallocated when the SensorManager is "
           "destructed.")
      // New API
      .def_prop_ro(
          "all",
          [](SensorManager &manager) {
            vector<Sensor *> sensors;
            for (int i = 0; i < manager.deviceCount(); ++i) {
              sensors.emplace_back(manager.sensor(i));
            }
            return sensors;
          },
          "Get list of all available sensors.")
      .def(
          "open_all",
          [](SensorManager &manager, int colorWidth, int colorHeight,
             int depthWidth, int depthHeight, double maxFps) {
            vector<Sensor *> sensors;
            for (int i = 0; i < manager.deviceCount(); ++i) {
              auto sensor = manager.sensor(i);
              if (sensor->open(colorWidth, colorHeight, depthWidth, depthHeight,
                               maxFps)) {
                sensors.emplace_back(sensor);
              }
            }
            return sensors;
          },
          "color_width"_a = 640, "color_height"_a = 480, "depth_width"_a = 640,
          "depth_height"_a = 480, "max_fps"_a = 30, nb::rv_policy::reference,
          "Open all available sensors with common configuration. This might "
          "not function well when working with various sensor models.")
      .def(
          "open_any",
          [](SensorManager &manager, int colorWidth, int colorHeight,
             int depthWidth, int depthHeight, double maxFps) -> Sensor * {
            if (manager.deviceCount() > 0) {
              auto sensor = manager.sensor(0);
              if (sensor->open(colorWidth, colorHeight, depthWidth, depthHeight,
                               maxFps)) {
                return sensor;
              }
            }
            return nullptr;
          },
          "color_width"_a = 640, "color_height"_a = 480, "depth_width"_a = 640,
          "depth_height"_a = 480, "max_fps"_a = 30, nb::rv_policy::reference,
          "Open any available sensor with given configuration. This might "
          "not function well when working with various sensor models.");
}
