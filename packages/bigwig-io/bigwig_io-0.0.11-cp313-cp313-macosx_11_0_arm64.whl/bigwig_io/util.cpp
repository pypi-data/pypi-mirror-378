#pragma once

#include <condition_variable>
#include <functional>
#include <iostream>
#include <mutex>
#include <thread>
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <stdexcept>


class Semaphore {
    std::mutex mtx;
    std::condition_variable cv;
    int count;

public:
    explicit Semaphore(int initial) : count(initial) {}

    void acquire() {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [&] { return count > 0; });
        --count;
    }

    void release() {
        std::unique_lock<std::mutex> lock(mtx);
        ++count;
        lock.unlock();
        cv.notify_one();
    }
};


class SemaphoreGuard {
    Semaphore& sem;
    bool owns;

public:
    explicit SemaphoreGuard(Semaphore& s) : sem(s), owns(true) {
        sem.acquire();
    }

    ~SemaphoreGuard() {
        if (owns) sem.release();
    }

    // non-copyable and non-move-assignable
    SemaphoreGuard(const SemaphoreGuard&) = delete;
    SemaphoreGuard& operator=(const SemaphoreGuard&) = delete;
    SemaphoreGuard& operator=(SemaphoreGuard&&) = delete;

    // movable (constructor only)
    SemaphoreGuard(SemaphoreGuard&& other) noexcept : sem(other.sem), owns(other.owns) {
        other.owns = false;
    }
};


class ProgressTracker {
    uint64_t total;
    std::function<void(uint64_t, uint64_t)> callback;
    double report_interval;
    double last_reported;

public:
    ProgressTracker(uint64_t t, std::function<void(uint64_t, uint64_t)> cb, double ri = 0.01)
        : total(t), callback(cb), report_interval(ri), last_reported(0) {}

    void update(uint64_t current) {
        double progress = (total > 0) ? static_cast<double>(current) / total : 0.0;
        if (callback && progress > last_reported + report_interval) {
            last_reported = progress;
            callback(current, total);
        }
    }

    void done() {
        if (callback && last_reported < 1.0) {
            last_reported = 1.0;
            callback(total, total);
        }
    }

};


uint64_t get_available_threads() {
    unsigned int n = std::thread::hardware_concurrency();
    return (n == 0) ? 1 : n;
}


template <typename Map>
std::vector<typename Map::key_type> get_map_keys(const Map& m) {
    std::vector<typename Map::key_type> result;
    result.reserve(m.size());
    for (const auto& kv : m) {
        result.push_back(kv.first);
    }
    return result;
}


void print_progress(uint64_t current, uint64_t total) {
    uint64_t percent = (total > 0) ? (current * 100) / total : 100;
    if (percent == 100) {
        std::cout << "\rProgress: 100% " << std::endl;
    } else {
        std::cout << "\rProgress: " << percent << "% " << std::flush;
    }
}


template<typename T>
std::string fstring_tostr(T&& value) {
    if constexpr (std::is_same_v<std::decay_t<T>, std::string>) {
        return std::forward<T>(value);
    } else if constexpr (std::is_same_v<std::decay_t<T>, const char*>) {
        return std::string(value);
    } else if constexpr (std::is_arithmetic_v<std::decay_t<T>>) {
        return std::to_string(std::forward<T>(value));
    } else {
        std::ostringstream oss;
        oss << std::forward<T>(value);
        return oss.str();
    }
}

template<typename... Args>
std::string fstring(const std::string& fmt, Args&&... args) {
    if constexpr (sizeof...(args) == 0) {
        return fmt;
    } else {
        std::ostringstream result;
        std::vector<std::string> arg_strings = {fstring_tostr(std::forward<Args>(args))...};
        size_t arg_index = 0;
        size_t pos = 0;
        size_t found = 0;
        while ((found = fmt.find("{}", pos)) != std::string::npos) {
            if (arg_index >= arg_strings.size()) {
                throw std::runtime_error("not enough arguments for format string");
            }
            result << fmt.substr(pos, found - pos);
            result << arg_strings[arg_index++];
            pos = found + 2;
        }
        if (arg_index < arg_strings.size()) {
            throw std::runtime_error("too many arguments for format string");
        }
        result << fmt.substr(pos);
        return result.str();
    }
}


std::string lowercase(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(),
                   [](unsigned char c) { return std::tolower(c); });
    return result;
}

std::string uppercase(const std::string& str) {
    std::string result = str;
    std::transform(result.begin(), result.end(), result.begin(),
                   [](unsigned char c) { return std::toupper(c); });
    return result;
}

