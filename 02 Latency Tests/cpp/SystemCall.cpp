#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unistd.h>
#include <vector>
#include "Stopwatch.cpp"

namespace py = pybind11;

std::vector<Stopwatch> run(const int reps = 1000) {
    std::vector<Stopwatch> probes;
    probes.reserve(reps);

    // Execution loop
    for (int i = 0; i < reps; ++i) {
        Stopwatch sw;
        sw.start();
        sleep(0);
        sw.stop();
        probes.push_back(sw);
    }

    return probes;
}

PYBIND11_MODULE(SystemCall, m) {
    m.def("run", &run, py::arg("reps") = 1000);
}
