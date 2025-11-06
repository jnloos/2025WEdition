#ifndef TIME_RESULT_H
#define TIME_RESULT_H

#include <chrono>

class TimeProbe {
public:
    using Duration = std::chrono::nanoseconds;

    TimeProbe() : duration_(Duration::zero()) {}

    explicit TimeProbe(const long long nanoseconds) : duration_(nanoseconds) {}

    explicit TimeProbe(const Duration duration) : duration_(duration) {}

    double toSeconds() const {
        return std::chrono::duration<double>(duration_).count();
    }

    double toMilliseconds() const {
        return std::chrono::duration<double, std::milli>(duration_).count();
    }

    double toMicroseconds() const {
        return std::chrono::duration<double, std::micro>(duration_).count();
    }

    long long toNanoseconds() const {
        return duration_.count();
    }

    static TimeProbe fromSeconds(double seconds) {
        return TimeProbe(std::chrono::duration_cast<Duration>(
            std::chrono::duration<double>(seconds)
        ));
    }

    static TimeProbe fromMilliseconds(const double milliseconds) {
        return TimeProbe(std::chrono::duration_cast<Duration>(
            std::chrono::duration<double, std::milli>(milliseconds)
        ));
    }

    static TimeProbe fromMicroseconds(const double microseconds) {
        return TimeProbe(std::chrono::duration_cast<Duration>(
            std::chrono::duration<double, std::micro>(microseconds)
        ));
    }

    static TimeProbe fromNanoseconds(const long long nanoseconds) {
        return TimeProbe(nanoseconds);
    }

private:
    Duration duration_;
};

#endif // TIME_RESULT_H