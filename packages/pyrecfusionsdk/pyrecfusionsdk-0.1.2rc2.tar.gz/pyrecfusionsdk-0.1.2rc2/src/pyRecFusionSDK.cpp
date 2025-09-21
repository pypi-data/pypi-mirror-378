#include <RecFusion.h>
#include <nanobind/nanobind.h>

namespace nb = nanobind;

void init_calibration(nb::module_ &);
void init_image(nb::module_ &);
void init_matrix(nb::module_ &);
void init_mesh(nb::module_ &);
void init_meshviewer(nb::module_ &);
void init_recfusionsdk(nb::module_ &);
void init_reconstruction(nb::module_ &);
void init_rfsplayback(nb::module_ &);
void init_rfsrecorder(nb::module_ &);
void init_sensor(nb::module_ &);
void init_sensormanager(nb::module_ &);
void init_vector(nb::module_ &);

NB_MODULE(_pyRecFusionSDK_impl, m) {
  init_calibration(m);
  init_image(m);
  init_matrix(m);
  init_mesh(m);
  init_meshviewer(m);
  init_recfusionsdk(m);
  init_reconstruction(m);
  init_rfsplayback(m);
  init_rfsrecorder(m);
  init_sensor(m);
  init_sensormanager(m);
  init_vector(m);
}
