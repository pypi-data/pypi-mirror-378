#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/ndarray.h>
#include <nanobind/stl/tuple.h>

using std::make_tuple;
namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;

void init_mesh(nb::module_ &m) {
  nb::class_<Mesh>(m, "Mesh")
      .def(nb::init<>())
      // static Mesh* create()
      // TODO: this doesn't work :(
      // .def_static("create", "vertex_count"_a, "vertices"_a,
      // "triangle_count"_a,
      //             "triangle_indices"_a, "colors"_a = nb::none(),
      //             "normals"_a = nb::none(), "volume_resolution"_a = 512,
      //             &Mesh::create)
      .def_prop_ro("vertex_count", &Mesh::vertexCount)
      .def_prop_ro("triangle_count", &Mesh::triangleCount)
      .def(
          "vertex",
          [](Mesh &mesh, int idx) {
            auto coord = mesh.vertex(idx);
            return make_tuple(coord.x, coord.y, coord.z);
          },
          "idx"_a)
      .def(
          "set_vertex",
          [](Mesh &mesh, int idx, double x, double y, double z) {
            mesh.setVertex(idx, {x, y, z});
          },
          "idx"_a, "x"_a, "y"_a, "z"_a)
      .def(
          "normal",
          [](Mesh &mesh, int idx) {
            auto normal = mesh.normal(idx);
            return make_tuple(normal.x, normal.y, normal.z);
          },
          "idx"_a)
      .def(
          "set_normal",
          [](Mesh &mesh, int idx, double nx, double ny, double nz) {
            mesh.setNormal(idx, {nx, ny, nz});
          },
          "idx"_a, "nx"_a, "ny"_a, "nz"_a)
      .def(
          "color",
          [](Mesh &mesh, int idx) {
            auto color = mesh.color(idx);
            return make_tuple(color.r, color.g, color.b);
          },
          "idx"_a)
      .def(
          "set_color",
          [](Mesh &mesh, int idx, double r, double g, double b) {
            mesh.setNormal(idx, {r, g, b});
          },
          "idx"_a, "r"_a, "g"_a, "b"_a)
      .def_prop_ro("center",
                   [](Mesh &mesh) {
                     auto center = mesh.center();
                     return make_tuple(center[0], center[1], center[2]);
                   })
      .def_prop_ro("vertices", [](Mesh &mesh) {
        double *data = new double[mesh.vertexCount() * 3];
        for (int i = 0, j = 0; i < mesh.vertexCount(); ++i, j += 3) {
          auto v = mesh.vertex(i);
          data[j] = v.x;
          data[j + 1] = v.y;
          data[j + 2] = v.z;
        }
        // nb::capsule owner(data, [](void *p) noexcept {
        //       delete[] (double *) p;
        //    });
        return nb::ndarray<nb::numpy, double, nb::ndim<2>>(
            /* data = */ data,
            /* shape = */ {(size_t)mesh.vertexCount(), 3});
      });
  // .def(
  //     "triangle",
  //     [](Mesh &mesh, int idx) {
  //       auto triangle = mesh.triangle(idx);
  //       return make_tuple(triangle.i1, triangle.i2, triangle.i3);
  //     },
  //     "idx"_a);
  // .def("add_triangle");
  //
}
