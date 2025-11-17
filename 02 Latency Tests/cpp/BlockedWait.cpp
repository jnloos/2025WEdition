#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <semaphore.h>
#include <thread>
#include <chrono>
#include <vector>
#include "Stopwatch.cpp"

namespace py = pybind11;

// Measure time between semaphore release and acquisition using Stopwatch
std::vector<Stopwatch> run(const int reps = 1000) {
    std::vector<Stopwatch> probes;
    probes.reserve(reps);

    for (int i = 0; i < reps; ++i) {
        sem_t sem;
        sem_init(&sem, 0, 0); // start locked (value 0)

        Stopwatch sw;
        bool acquired = false;

        // Thread B: waits (blocked)
        std::thread waiter([&]() {
            sem_wait(&sem); // will block until release
            sw.stop();
            acquired = true;
        });

        // Give waiter time to reach blocking state
        std::this_thread::sleep_for(std::chrono::microseconds(10));

        // Start a timer just before releasing
        sw.start();
        sem_post(&sem);

        // Wait until semaphore acquired
        while (!acquired) std::this_thread::yield();
        waiter.join();

        sem_destroy(&sem);
        probes.push_back(sw);
    }

    return probes;
}

PYBIND11_MODULE(BlockedWait, m) {
    m.def("run", &run, py::arg("reps") = 1000);
}
