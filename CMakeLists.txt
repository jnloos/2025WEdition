cmake_minimum_required(VERSION 4.0)
project(2025WEdition)

set(CMAKE_CXX_STANDARD 14)

add_executable(2025WEdition
        "02 Latency Tests/cpp/IncProbeset.cpp"
        "02 Latency Tests/cpp/TimeProbe.cpp"
        "02 Latency Tests/cpp/SystemCall.cpp"
        "02 Latency Tests/cpp/ORWC.cpp")
