#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/tuple.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;
using std::make_tuple;

void init_reconstruction(nb::module_ &m) {
  nb::class_<ReconstructionParams>(
      m, "ReconstructionParams",
      "Class representing reconstruction parameters. Currently only sensors "
      "with equal depth and color image sizes and intrinsics are supported.")
      .def(nb::init<int>(), "sensors"_a = 1,
           "Construct reconstruction parameters. By default a cubic volume of "
           "side length 1 m with a resolution of 256, 1 m in front of the "
           "sensor is defined. The image size and intrinsics for each sensor "
           "must be set prior to running the reconstruction.")
      .def_prop_ro("sensors", &ReconstructionParams::sensors,
                   "Get number of sensors.")
      // TODO: Convert this to ro prop
      .def("set_image_size", &ReconstructionParams::setImageSize,
           "color_width"_a, "color_height"_a, "depth_width"_a, "depth_height"_a,
           "sensor"_a = 0, "Set image size for sensor.")
      .def(
          "image_size",
          [](ReconstructionParams &params, int sensor = 0) {
            int color_width, color_height, depth_width, depth_height;
            params.imageSize(color_width, color_height, depth_width,
                              depth_height, sensor);
            return make_tuple(color_width, color_height, depth_width,
                              depth_height);
          },
          "Get image size for sensor.")
      // TODO: change to ro props
      .def("set_intrinsics", &ReconstructionParams::setIntrinsics, "K"_a,
           "sensor"_a = 0, "Set depth image intrinsics for sensor.")
      .def("set_color_intrinsics", &ReconstructionParams::setColorIntrinsics,
           "K"_a, "sensor"_a = 0)
      .def("set_depth_to_color_transformation",
           &ReconstructionParams::setDepthToColorTransformation, "T"_a,
           "sensor"_a = 0)
      // New API
      .def("set_depth_intrinsics", &ReconstructionParams::setIntrinsics, "K"_a,
           "sensor"_a = 0,
           "Set depth image intrinsics for sensor. This is just an alias to "
           "set_intrinsics.");

  nb::class_<Reconstruction>(
      m, "Reconstruction",
      "Class performing colored surface reconstruction from depth data.")
      .def(nb::init<ReconstructionParams>(),
           "Construct surface reconstruction object. To check whether the "
           "object was created successfully call good() after object creation.")
      .def_prop_ro("good", &Reconstruction::good,
                   "Get reconstruction object status.")
      // TODO: unify add_frame and add_frame2
      .def(
          "add_frame2",
          [](Reconstruction &reconstruction, int sensor, DepthImage &imgDepth,
             ColorImage &imgColor) {
            return reconstruction.addFrame(sensor, imgDepth, imgColor);
          },
          "sensor"_a, "img_depth"_a, "img_color"_a,
          "Add frame to reconstruction.")
      .def("add_frame", &Reconstruction::addFrame, "sensor"_a, "img_depth"_a,
           "img_color"_a, "tracking_status"_a = 0, "img_scene"_a = 0, "T"_a = 0,
           "sensor_T"_a = 0, "tracked_t"_a = 0,
           "dont_force_first_frame"_a = false, "Add frame to reconstruction.")
      .def(
          "get_mesh",
          [](Reconstruction &reconstruction) {
            auto mesh = new Mesh();
            reconstruction.getMesh(mesh);
            return mesh;
          },
          "Return reconstructed mesh.");
}
