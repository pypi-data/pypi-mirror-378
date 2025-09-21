#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/optional.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_calibration(nb::module_ &m) {
  nb::class_<Calibration>(
      m, "Calibration",
      "Provides functions for calibrating multi-sensor setups.\nTo calibrate a "
      "multi-sensor setup a calibration marker needs to be placed in such a "
      "way that it is visible in all sensors which are to be calibrated. For "
      "each sensor a color image needs to be acquired. The calibration object "
      "needs to be initialized with the number of sensors to calibrate by "
      "calling the init method. Next the markers used for calibration have to "
      "be specified using setMarker. It is possible to specify more than one "
      "marker. In this case the transformation from each marker coordinate "
      "system to a common calibration coordinate system needs to be provided. "
      "Next the calibration images need to be set using setImage. At this "
      "point calibrate can be called to calibrate the sensor locations. The "
      "results can be retrieved using getTransformation. The returned "
      "transformation provides the transformation from the specified sensor "
      "coordinate system to the coordinate system of the first sensor. It is "
      "represented as homogeneous 4x4 matrix with the upper left 3x3 matrix "
      "representig the rotation component and the upper right 3x1 vector "
      "representing the translation component. The matrix can be passed "
      "directly to the sensorT parameter of Reconstruction::addFrame method.")
      .def(nb::init<>(), "Construct calibration object.")
      .def("init", &Calibration::init, "num_sensors"_a,
           "Set up calibration. Needs to be called before any other functions "
           "can be called. Clears previously set markers and images. ")
      .def("set_marker", &Calibration::setMarker, "marked_id"_a,
           "marker_size"_a, "marker_t"_a = nb::none(),
           "Define marker with given ID. Overwrittes previously defined "
           "markers with the same ID.")
      .def("set_image", &Calibration::setImage, "sensor"_a, "img_depth"_a,
           "img_color"_a, "depth_k"_a, "color_k"_a,
           "depth_to_color_t"_a = nb::none(),
           "Set image for given sensor. If the image has been previously set "
           "it is overwritten.")
      .def("calibrate", &Calibration::calibrate,
           "Calibrate sensors using the previously set markers and images. "
           "Before calling this method the marker(s) and the images have to be "
           "specified using setMarker and setImage.")
      .def(
          "get_transformation",
          [](Calibration &calibration, int sensor) -> std::optional<Mat4 *> {
            auto T = new Mat4();
            if (calibration.getTransformation(sensor, *T)) {
              return T;
            } else {
              return {};
            }
          },
          "sensor"_a,
          "Get transformation from specified sensor to first sensor, if "
          "calibration has succeded.")
      // TODO: change get_marker_pose to return the transformation by value?
      .def_static("get_marker_pose", &Calibration::getMarkerPose, "marker_id"_a,
                  "marker_size"_a, "img_color"_a, "color_k"_a, "t"_a,
                  "Get transformation from specified marker to sensor, if transformation is available.");
}
