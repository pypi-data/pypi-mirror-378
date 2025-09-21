#include <RecFusion.h>
#include <nanobind/nanobind.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_meshviewer(nb::module_ &m) {
  nb::class_<MeshViewer>(m, "MeshViewer", "3D mesh viewer.")
      .def(nb::init<>(), "Constructs the MeshViewer instance.")
      .def("show_mesh", &MeshViewer::showMesh, "mesh"_a,
           "Display mesh in 3D viewer window.");
}
