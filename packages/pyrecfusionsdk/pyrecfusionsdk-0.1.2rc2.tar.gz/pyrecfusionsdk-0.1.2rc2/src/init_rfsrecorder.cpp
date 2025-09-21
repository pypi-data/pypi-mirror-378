#include <RecFusion.h>
#include <nanobind/nanobind.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_rfsrecorder(nb::module_ &m) {
  nb::class_<RFSRecorder>(
      m, "RFSRecorder",
      "Class saving RGB-D sequences in RFS format.\nThe recorder uses a ring "
      "buffer to store the passed in images. In the background a thread is "
      "writing the images to disk. To start the thread call start(), to stop "
      "it call stop(). If the thread is not running images will be dropped "
      "when the ring buffer is full. Frames will also be dropped when the "
      "frames cannot be written fast enough to disk. Whether a frame was "
      "dropped is indicated by the return value of addFrame().")
      .def(nb::init<const char *>(), "filename"_a, "Construct recorder object.")
      .def("init", &RFSRecorder::init, "color_width"_a, "color_height"_a,
           "depth_width"_a, "depth_height"_a, "depth_k"_a,
           "color_k"_a = nb::none(), "depth_to_color_t"_a = nb::none(),
           "Initialize image recorder.")
      .def("cleanup", &RFSRecorder::cleanup, "Free image recorder internal data and close output file.")
      .def("start", &RFSRecorder::start, "Start recording thread. Needs to be called before adding frames.")
      .def("stop", &RFSRecorder::stop, "Stop recording thread. Will return after all images in the queue have been written.")
      .def("add_frame", &RFSRecorder::addFrame, "img_depth"_a, "img_color"_a,
           "Add frame to file. The images must have the same size passed to "
           "initialize().")
      // New API
      .def("init_from_sensor", [](RFSRecorder &recorder, Sensor &sensor) {
        recorder.init(sensor.colorWidth(), sensor.colorHeight(),
                      sensor.depthWidth(), sensor.depthHeight(),
                      sensor.depthIntrinsics());
      }, "Initialize image recorder using properties of the given sensor.");
}
