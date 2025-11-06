#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unistd.h>
#include <vector>
#include <string>
#include "Stopwatch.cpp"

namespace py = pybind11;

std::vector<Stopwatch> run(const int reps = 1000) {
    std::vector<Stopwatch> watches;
    watches.reserve(reps);

    const std::string msg = "ping";

    // Execution loop
    for (int i = 0; i < reps; ++i) {
        int fds[2];
        if (pipe(fds) == -1) continue;

        Stopwatch sw;
        sw.start();

        // Write to the pipe
        write(fds[1], msg.c_str(), msg.size());
        // Read from the pipe
        char buf[16];
        read(fds[0], buf, sizeof(buf));

        sw.stop();
        watches.push_back(sw);

        close(fds[0]);
        close(fds[1]);
    }

    return watches;
}

PYBIND11_MODULE(PipelineMsg, m) {
    py::class_<Stopwatch>(m, "Stopwatch")
        .def("elapsed_seconds", &Stopwatch::elapsed_seconds)
        .def("elapsed_milliseconds", &Stopwatch::elapsed_milliseconds)
        .def("elapsed_microseconds", &Stopwatch::elapsed_microseconds)
        .def("elapsed_nanoseconds", &Stopwatch::elapsed_nanoseconds);

    m.def("run", &run, py::arg("reps") = 1000);
}
