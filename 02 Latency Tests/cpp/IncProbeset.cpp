#include <vector>
#include <cmath>
#include <algorithm>
#include <limits>
#include <map>
#include <string>
#include "TimeProbe.cpp"

class IncProbeset {
private:
    size_t size = 0;
    long long min = std::numeric_limits<long long>::max();
    long long max = std::numeric_limits<long long>::min();
    long long mean = 0;
    long long M2 = 0;  // For variance calculation

    // P-Square algorithm for approximate median (5 markers only)
    long long q[5]{};      // marker heights (quantile estimates)
    int n[5]{};            // marker positions
    double np[5]{};        // desired marker positions
    double dn[5]{};        // desired position increments

    void initializePSquare(const long long val) {
        q[0] = q[1] = q[2] = q[3] = q[4] = val;
        n[0] = 0; n[1] = 1; n[2] = 2; n[3] = 3; n[4] = 4;
        np[0] = 0; np[1] = 1; np[2] = 2; np[3] = 3; np[4] = 4;
        dn[0] = 0; dn[1] = 0.25; dn[2] = 0.5; dn[3] = 0.75; dn[4] = 1;
    }

    long long parabolic(const int i, const int d) const {
        const double result = static_cast<double>(q[i]) +
            static_cast<double>(d) / static_cast<double>(n[i + 1] - n[i - 1]) * (
                (n[i] - n[i-1] + d) * static_cast<double>(q[i+1] - q[i]) / static_cast<double>(n[i+1] - n[i]) +
                (n[i+1] - n[i] - d) * static_cast<double>(q[i] - q[i-1]) / static_cast<double>(n[i] - n[i-1])
            );
        return static_cast<long long>(result);
    }

    void updatePSquare(const long long val) {
        // Find cell k
        int k;
        if (val < q[0]) {
            q[0] = val;
            k = 0;
        } else {
            for (k = 1; k < 5; k++) {
                if (val < q[k]) break;
            }
            k--;
            if (k == 4) q[4] = val;
        }

        // Increment positions
        for (int i = k + 1; i < 5; i++) {
            n[i]++;
        }
        for (int i = 0; i < 5; i++) {
            np[i] += dn[i];
        }

        // Adjust heights of markers 1-3
        for (int i = 1; i < 4; i++) {
            const double d = np[i] - static_cast<double>(n[i]);
            if ((d >= 1.0 && n[i+1] - n[i] > 1) || (d <= -1.0 && n[i-1] - n[i] < -1)) {
                const int sign = (d >= 0) ? 1 : -1;
                const long long qNew = parabolic(i, sign);

                if (q[i-1] < qNew && qNew < q[i+1]) {
                    q[i] = qNew;
                } else {
                    // Linear formula fallback
                    q[i] += sign * (q[i+sign] - q[i]) / (n[i+sign] - n[i]);
                }
                n[i] += sign;
            }
        }
    }

public:
    IncProbeset() = default;

    void probe(const long long val) {
        size++;

        // Update min/max
        if (val < min) min = val;
        if (val > max) max = val;

        // Welford's online algorithm for mean and variance
        const long long delta = val - mean;
        mean += delta / static_cast<long long>(size);
        const long long delta2 = val - mean;
        M2 += delta * delta2;

        // Update median estimate using P-Square
        if (size <= 5) {
            if (size == 1) {
                initializePSquare(val);
            } else {
                q[size-1] = val;
                if (size == 5) {
                    std::sort(q, q + 5);
                }
            }
        } else {
            updatePSquare(val);
        }
    }

    void probe(const TimeProbe probe) {
        this->probe(probe.toNanoseconds());
    }

    // Getters for the 6 core statistics
    TimeProbe getMin() const {
        return size > 0 ? TimeProbe::fromNanoseconds(min) : TimeProbe::fromNanoseconds(0);
    }

    TimeProbe getMax() const {
        return size > 0 ? TimeProbe::fromNanoseconds(max) : TimeProbe::fromNanoseconds(0);
    }

    TimeProbe getMean() const {
        return TimeProbe::fromNanoseconds(mean);
    }

    TimeProbe getMedian() const {
        if (size == 0) return TimeProbe::fromNanoseconds(0);
        if (size <= 5) {
            std::vector<long long> temp(q, q + size);
            std::sort(temp.begin(), temp.end());
            const long long median_ns = (size % 2 == 0)
                ? (temp[size/2 - 1] + temp[size/2]) / 2
                : temp[size/2];
            return TimeProbe::fromNanoseconds(median_ns);
        }
        return TimeProbe::fromNanoseconds(q[2]);  // Middle marker is median
    }

    TimeProbe getStdDev() const {
        if (size <= 1) return TimeProbe::fromNanoseconds(0);
        const long long variance = getVariance();
        const auto stddev = static_cast<long long>(std::sqrt(static_cast<double>(variance)));
        return TimeProbe::fromNanoseconds(stddev);
    }

    long long getVariance() const {
        return size > 1 ? M2 / static_cast<long long>(size - 1) : 0;
    }

    std::map<std::string, double> results(const std::string& unit) const {
        auto convert = [&](const TimeProbe& probe) -> double {
            if (unit == "ns") return static_cast<double>(probe.toNanoseconds());
            if (unit == "us") return probe.toMicroseconds();
            if (unit == "ms") return probe.toMilliseconds();
            if (unit == "s") return probe.toSeconds();
            return probe.toMicroseconds();
        };

        std::map<std::string, double> results;
        results["size"] = static_cast<double>(this->getSize());
        results["min"] = convert(this->getMin());
        results["max"] = convert(this->getMax());
        results["mean"] = convert(this->getMean());
        results["median"] = convert(this->getMedian());
        results["std_dev"] = convert(this->getStdDev());

        return results;
    }

    size_t getSize() const { return size; }
};