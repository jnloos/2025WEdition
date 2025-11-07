#include <chrono>

class Stopwatch {
public:
    Stopwatch()
        : accumulated_time_(Duration::zero()), running_(false) { }

    explicit Stopwatch(const long long nanoseconds)
        : accumulated_time_(Duration(nanoseconds)), running_(false) { }

    void start() {
        if (!running_) {
            start_time_ = Clock::now();
            last_lap_time_ = start_time_;
            running_ = true;
        }
    }

    void stop() {
        if (running_) {
            accumulated_time_ += Clock::now() - start_time_;
            running_ = false;
        }
    }

    void reset() {
        accumulated_time_ = Duration::zero();
        running_ = false;
    }

    double elapsed_seconds() const {
        const auto duration = get_elapsed_duration();
        return std::chrono::duration<double>(duration).count();
    }

    double elapsed_milliseconds() const {
        const auto duration = get_elapsed_duration();
        return std::chrono::duration<double, std::milli>(duration).count();
    }

    double elapsed_microseconds() const {
        const auto duration = get_elapsed_duration();
        return std::chrono::duration<double, std::micro>(duration).count();
    }

    long long elapsed_nanoseconds() const {
        return get_elapsed_duration().count();
    }

    bool is_running() const {
        return running_;
    }

private:
    using Clock = std::chrono::high_resolution_clock;
    using TimePoint = std::chrono::time_point<Clock>;
    using Duration = std::chrono::nanoseconds;

    TimePoint start_time_;
    TimePoint last_lap_time_;
    Duration accumulated_time_;
    bool running_;

    Duration get_elapsed_duration() const {
        if (running_) {
            return accumulated_time_ + (Clock::now() - start_time_);
        }
        return accumulated_time_;
    }
};
