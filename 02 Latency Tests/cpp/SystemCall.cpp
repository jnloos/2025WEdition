#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <chrono>
#include <unistd.h>
#include <map>
#include <string>
#include "IncProbeset.cpp"

namespace py = pybind11;

std::map<std::string, double> run(int reps = 1000, const std::string& unit = "us") {
    IncProbeset probeset;

    for (int i = 0; i < 10; ++i) {
        sleep(0);
    }

    for (int i = 0; i < reps; ++i) {
        auto start = std::chrono::high_resolution_clock::now();
        sleep(0);
        auto end = std::chrono::high_resolution_clock::now();
        auto duration_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start).count();
        probeset.probe(duration_ns);
    }

    return probeset.results(unit);
}

PYBIND11_MODULE(SystemCall, m) {
    m.def("run", &run, py::arg("reps") = 1000, py::arg("unit") = "ns");
}