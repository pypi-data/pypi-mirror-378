#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_matrix(nb::module_ &m) {
  // NOTE: _Mat3 and _Mat4 are only non-public base implementation of their
  // respective RecFusion classes. The user-friendly classes, Mat3 and Mat4, are
  // defined in Python, because it is easier to add some functionality that way.
  //
  // NOTE: _Mat3 and _Mat4 implement numpy `data` read-write property for
  // accessing matrix elements.
  nb::class_<Mat3>(
      m, "_Mat3",
      "Non-public base implementation of the 3x3 matrix. Use Mat3 instead.")
      .def(
          "__init__",
          [](Mat3 *t, const nb::ndarray<double, nb::shape<3, 3>> &array) {
            new (t) Mat3(array.data());
          },
          "Construct matrix from 3x3 Numpy array.")
      .def_prop_rw(
          "data",
          [](Mat3 &matrix) {
            return nb::ndarray<nb::numpy, double, nb::shape<3, 3>>(
                matrix.data());
          },
          [](Mat3 &matrix, const nb::ndarray<double, nb::shape<3, 3>> &array) {
            for (int r = 0; r < 3; ++r) {
              for (int c = 0; c < 3; ++c) {
                matrix(r, c) = array(r, c);
              }
            }
          },
          "Access matrix values as Numpy array.")
      .def(
          "__matmul__", [](Mat3 &self, Mat3 &other) { return self * other; },
          "Multiply two 3x3 matrices.");

  nb::class_<Mat4>(
      m, "_Mat4",
      "Non-public base implementation of the 4x4 matrix. Use Mat4 instead.")
      .def(
          "__init__",
          [](Mat4 *t, const nb::ndarray<double, nb::shape<4, 4>> &array) {
            new (t) Mat4(array.data());
          },
          "Construct matrix from 4x4 Numpy array.")
      .def_prop_rw(
          "data",
          [](Mat4 &matrix) {
            return nb::ndarray<nb::numpy, double, nb::shape<4, 4>>(
                matrix.data());
          },
          [](Mat4 &matrix, const nb::ndarray<double, nb::shape<4, 4>> &array) {
            for (int r = 0; r < 4; ++r) {
              for (int c = 0; c < 4; ++c) {
                matrix(r, c) = array(r, c);
              }
            }
          },
          "Access matrix values as Numpy array.")
      .def(
          "__matmul__", [](Mat4 &self, Mat4 &other) { return self * other; },
          "Multiply two 4x4 matrices.")
      .def("inverse", &Mat4::inverse, "Compute inverse matrix.")
      .def_static("from_euler", &Mat4::fromEuler, "rx"_a, "ry"_a, "rz"_a,
                  "Convert Euler angles in degrees to a homogeneous "
                  "transformation matrix.");
}
