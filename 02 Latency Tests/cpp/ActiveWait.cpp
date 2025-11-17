#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <atomic>
#include <thread>
#include <chrono>
#include <vector>
#include "Stopwatch.cpp"

namespace py = pybind11;

// Measure time between spinlock release and acquisition using Stopwatch
std::vector<Stopwatch> run(const int reps = 1000) {
    std::vector<Stopwatch> probes;
    probes.reserve(reps);

    for (int i = 0; i < reps; ++i) {
        std::atomic_flag lock = ATOMIC_FLAG_INIT;
        lock.test_and_set(std::memory_order_release); // initially locked

        Stopwatch sw;
        bool acquired = false;

        // Thread B: waiting thread
        std::thread waiter([&]() {
            while (lock.test_and_set(std::memory_order_acquire)) {
                lock.clear(std::memory_order_release);
            }
            // Stop as soon as it observes unlock
            sw.stop();
            acquired = true;
        });

        // Give waiter time to start spinning
        std::this_thread::sleep_for(std::chrono::microseconds(10));

        // Start timer just before releasing lock
        sw.start();
        lock.clear(std::memory_order_release);

        // Wait for acquisition
        while (!acquired) std::this_thread::yield();
        waiter.join();

        probes.push_back(sw);
    }

    return probes;
}

PYBIND11_MODULE(ActiveWait, m) {
    m.def("run", &run, py::arg("reps") = 1000);
}
