#include <RecFusion.h>
#include <nanobind/nanobind.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_vector(nb::module_ &m) {
  // NOTE: _Vec3 and _Vec3i are only non-public base implementation of
  // their respective RecFusion classes. The user-friendly classes, Vec3 and
  // Vec3i, are defined in Python, because it is easier to add some
  // functionality that way.
  //
  // NOTE: _Vec3 and _Vec3i don't implement: data() and operator[]. Instead,
  // they provide direct access to components using .x, .y, or .z properties.
  nb::class_<Vec3>(m, "_Vec3",
                   "Non-public base implementation of the 3D floating-point "
                   "vector. Use Vec3 instead.")
      .def(nb::init<double, double, double>(), "x"_a, "y"_a, "z"_a,
           "Construct 3D vector of floating-point values.")
      .def_prop_rw(
          "x", [](Vec3 &vec) { return vec[0]; },
          [](Vec3 &vec, double value) { vec[0] = value; },
          "Access X, the first vector component.")
      .def_prop_rw(
          "y", [](Vec3 &vec) { return vec[1]; },
          [](Vec3 &vec, double value) { vec[1] = value; },
          "Access Y, the second vector component.")
      .def_prop_rw(
          "z", [](Vec3 &vec) { return vec[2]; },
          [](Vec3 &vec, double value) { vec[2] = value; },
          "Access Z, the third vector component.");

  nb::class_<Vec3i>(m, "_Vec3i",
                    "Non-public base implementation of the 3D integer vector. "
                    "Use Vec3i instead.")
      .def(nb::init<int, int, int>(), "x"_a, "y"_a, "z"_a,
           "Construct 3D vector of integer values.")
      .def_prop_rw(
          "x", [](Vec3i &vec) { return vec[0]; },
          [](Vec3i &vec, int value) { vec[0] = value; },
          "Access X, the first vector component.")
      .def_prop_rw(
          "y", [](Vec3i &vec) { return vec[1]; },
          [](Vec3i &vec, int value) { vec[1] = value; },
          "Access Y, the second vector component.")
      .def_prop_rw(
          "z", [](Vec3i &vec) { return vec[2]; },
          [](Vec3i &vec, int value) { vec[2] = value; },
          "Access Z, the third vector component.");
}
