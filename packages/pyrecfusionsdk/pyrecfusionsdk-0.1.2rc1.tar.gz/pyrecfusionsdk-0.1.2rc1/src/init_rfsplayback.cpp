
#include <RecFusion.h>
#include <nanobind/nanobind.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_rfsplayback(nb::module_ &m) {
  nb::class_<RFSPlayback>(m, "RFSPlayback",
                          "Class reading RGB-D sequences in RFS format.")
      .def(nb::init<>(), "Construct reader object.")
      .def("open", &RFSPlayback::open, "filename"_a, "Open sequence.")
      .def("close", &RFSPlayback::close, "Close sequence.")
      .def_prop_ro("frame_count", &RFSPlayback::frameCount,
                   "Get number of frames in sequence.")
      .def("read_image", &RFSPlayback::readImage, "frame"_a, "img_depth"_a,
           "img_color"_a, "Read image from sequence.")
      .def_prop_ro("color_width", &RFSPlayback::colorWidth,
                   "Get width of color image.")
      .def_prop_ro("color_height", &RFSPlayback::colorHeight,
                   "Get height of color image.")
      .def_prop_ro("depth_width", &RFSPlayback::depthWidth,
                   "Get width of depth image.")
      .def_prop_ro("depth_height", &RFSPlayback::depthHeight,
                   "Get height of depth image.")
      .def_prop_ro("intrinsics", &RFSPlayback::intrinsics,
                   "Get depth sensor intrinsics.")
      .def_prop_ro("color_intrinsics", &RFSPlayback::colorIntrinsics,
                   "Get color sensor intrinsics.")
      .def_prop_ro("depth_to_color_t", &RFSPlayback::depthToColorT,
                   "Get transformation between color and depth camera.")
      // New API
      // Alias to intrinsics() method; there is already a specific name like
      // this in Sensor::depthInstrinsics
      .def_prop_ro("depth_intrinsics", &RFSPlayback::intrinsics,
                   "Get depth sensor intrinsics. This is an alias to "
                   "intrinsics property.")
      //
      .def_prop_ro("depth_to_color_transformation", &RFSPlayback::depthToColorT,
                   "Get transformation between color and depth camera. This is "
                   "an alias to depth_to_color_t property.");
}
