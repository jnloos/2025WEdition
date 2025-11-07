#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <fstream>
#include <vector>
#include <string>
#include "Stopwatch.cpp"

namespace py = pybind11;

std::vector<Stopwatch> run(const int reps = 1000) {
    std::vector<Stopwatch> probes;
    probes.reserve(reps);

    const std::string filename = "tmp.txt";
    const std::string data = "This is a test line for ORWC measurement.\n";

    // Execution loop
    for (int i = 0; i < reps; ++i) {
        Stopwatch sw;
        sw.start();

        // Define local scopes, which destroy the streams after being closed
        {
            std::ofstream ofs(filename, std::ios::trunc);
            ofs << data;
        }
        {
            std::ifstream ifs(filename);
            std::string line;
            std::getline(ifs, line);
        }

        sw.stop();
        probes.push_back(sw);
    }

    std::remove(filename.c_str());
    return probes;
}

PYBIND11_MODULE(ORWC, m) {
    py::class_<Stopwatch>(m, "Stopwatch")
        .def("elapsed_seconds", &Stopwatch::elapsed_seconds)
        .def("elapsed_milliseconds", &Stopwatch::elapsed_milliseconds)
        .def("elapsed_microseconds", &Stopwatch::elapsed_microseconds)
        .def("elapsed_nanoseconds", &Stopwatch::elapsed_nanoseconds);

    m.def("run", &run, py::arg("reps") = 1000);
}
