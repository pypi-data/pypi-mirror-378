#include <RecFusion.h>
#include <nanobind/nanobind.h>
#include <nanobind/stl/string.h>
#include <string>

namespace nb = nanobind;
using namespace nb::literals;
using namespace RecFusion;
using std::to_string;

void init_recfusionsdk(nb::module_ &m) {
  auto sdk =
      m.def_submodule("sdk", "Submodule with the SDK related functionality "
                             "(e.g. version, lincese...).");
  sdk.def("init", &RecFusionSDK::init, "log_filename"_a = "",
          "Initialize the SDK.");
  sdk.def("deinit", &RecFusionSDK::deinit, "Deinitialize the SDK.");
  sdk.def("activate", &RecFusionSDK::activate, "key"_a, "code"_a = "",
          "Activate the SDK license.");
  sdk.def("valid_license", &RecFusionSDK::validLicense,
          "Check validity of the SDK license.");
  sdk.def("token", &RecFusionSDK::token,
          "Get machine token needed for the offline acivation.");
  sdk.def("major_version", &RecFusionSDK::majorVersion,
          "Get SDK major version.");
  sdk.def("minor_version", &RecFusionSDK::minorVersion,
          "Get SDK minor version.");
  sdk.def("build_version", &RecFusionSDK::buildVersion,
          "Get SDK build version.");
  // New API
  sdk.def(
      "version",
      []() {
        return to_string(RecFusionSDK::majorVersion()) + "." +
               to_string(RecFusionSDK::minorVersion()) + "." +
               to_string(RecFusionSDK::buildVersion());
      },
      "Get SDK full version string.");
}
