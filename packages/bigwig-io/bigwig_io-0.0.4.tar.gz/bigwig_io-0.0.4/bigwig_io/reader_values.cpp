#pragma once

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <deque>
#include <fstream>
#include <functional>
#include <future>
#include <map>
#include <mutex>
#include <string>
#include <tuple>
#include <vector>

#include "structs.hpp"
#include "byte_util.cpp"
#include "file_util.cpp"
#include "util.cpp"
#include "reader_header.cpp"


WigDataHeader read_wig_data_header(const ByteArray& buffer) {
    WigDataHeader header;
    header.chr_index = buffer.read_uint32(0);
    header.chr_start = buffer.read_uint32(4);
    header.chr_end = buffer.read_uint32(8);
    header.item_step = buffer.read_uint32(12);
    header.item_span = buffer.read_uint32(16);
    header.type = buffer.read_uint8(20);
    header.reserved = buffer.read_uint8(21);
    header.item_count = buffer.read_uint16(22);
    return header;
}


ZoomDataRecord read_zoom_data_record(const ByteArray& buffer, uint64_t index) {
    uint64_t offset = index * 32;
    ZoomDataRecord record;
    record.chr_index = buffer.read_uint32(offset);
    record.chr_start = buffer.read_uint32(offset + 4);
    record.chr_end = buffer.read_uint32(offset + 8);
    record.valid_count = buffer.read_uint32(offset + 12);
    record.min_value = buffer.read_float(offset + 16);
    record.max_value = buffer.read_float(offset + 20);
    record.sum_data = buffer.read_float(offset + 24);
    record.sum_squared = buffer.read_float(offset + 28);
    return record;
}


bool fill_values_with_value(
    const std::vector<Loc>& locs,
    std::vector<float>& values,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    uint32_t start, uint32_t end, float value) {

    uint32_t bin_start = start / resolution;
    uint32_t bin_end = end / resolution;
    bool no_more_overlap = true;
    for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
        const Loc& loc = locs[loc_index];
        uint32_t loc_bin_start = loc.start / resolution;
        uint32_t loc_bin_end = loc.end / resolution;
        if (bin_start >= loc_bin_end) continue;
        no_more_overlap = false;
        if (bin_end <= loc_bin_start) break;
        uint32_t overlap_start = std::max(bin_start, loc_bin_start);
        uint32_t overlap_end = std::min(bin_end, loc_bin_end);
        for (uint32_t b = overlap_start; b < overlap_end; ++b) {
            uint64_t value_index = loc.values_index + (b - loc_bin_start);
            values[value_index] = value;
        }
    }
    return no_more_overlap;
}


bool fill_values_stats_with_value(
    const std::vector<Loc>& locs,
    std::vector<ValueStats>& values,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    uint32_t start, uint32_t end, float value) {

    uint32_t bin_start = start / resolution;
    uint32_t bin_end = end / resolution;
    bool no_more_overlap = true;
    for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
        const Loc& loc = locs[loc_index];
        uint32_t loc_bin_start = loc.start / resolution;
        uint32_t loc_bin_end = loc.end / resolution;
        if (bin_start >= loc_bin_end) continue;
        no_more_overlap = false;
        if (bin_end <= loc_bin_start) break;
        uint32_t overlap_start = std::max(bin_start, loc_bin_start);
        uint32_t overlap_end = std::min(bin_end, loc_bin_end);
        for (uint32_t b = overlap_start; b < overlap_end; ++b) {
            uint64_t value_index = loc.values_index + (b - loc_bin_start);
            values[value_index].sum += value;
            values[value_index].count += 1;
        }
    }
    return no_more_overlap;
}


bool fill_stats_with_value(
    const std::vector<Loc>& locs,
    std::vector<ExtendedValueStats>& values,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t start, uint32_t end, float value) {

    bool no_more_overlap = true;
    for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
        const Loc& loc = locs[loc_index];
        if (start >= loc.end) continue;
        no_more_overlap = false;
        if (end <= loc.start) break;
        uint32_t overlap_start = std::max(start, loc.start);
        uint32_t overlap_end = std::min(end, loc.end);
        uint32_t overlap = overlap_end - overlap_start;
        ExtendedValueStats& stats = values[loc_index];
        if (value < stats.min) stats.min = value;
        if (value > stats.max) stats.max = value;
        stats.sum += value * overlap;
        stats.sum_squared += value * value * overlap;
        stats.count += overlap;
    }
    return no_more_overlap;
}


void fill_values_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    std::vector<float>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset).get();
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    WigDataHeader header = read_wig_data_header(buffer);

    if (header.type == 1) { // bedgraph
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 12);
            uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
            float value = buffer.read_float(24 + i * 12 + 8);
                auto no_more_overlap = fill_values_with_value(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 2) { // variable step wig
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 8);
            uint32_t end = start + header.item_span;
            float value = buffer.read_float(24 + i * 8 + 4);
                auto no_more_overlap = fill_values_with_value(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 3) { // fixed step wig
        if (resolution <= header.item_step) {
            for (uint16_t i = 0; i < header.item_count; ++i) {
                uint32_t start = header.chr_start + i * header.item_step;
                uint32_t end = start + header.item_span;
                float value = buffer.read_float(24 + i * 4);
                auto no_more_overlap = fill_values_with_value(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
                if (no_more_overlap) break;
        }
        } else {
            double span_over_step = static_cast<double>(header.item_span) / header.item_step;
            for (uint64_t loc_index = start_loc_index; loc_index < end_loc_index; ++loc_index) {
                const Loc& loc = locs[loc_index];
                uint32_t start = std::max(loc.start, header.chr_start);
                uint32_t end = std::min(loc.end, header.chr_end);
                uint32_t loc_bin_start = loc.start / resolution;
                for (uint32_t pos = start; pos < end; pos += resolution) {
                    double bin = (static_cast<double>(pos - header.chr_start)) / header.item_step;
                    uint32_t bin_index = static_cast<uint32_t>(bin);
                    if (bin_index >= header.item_count) break;
                    if (bin - bin_index > span_over_step) continue;
                    float value = buffer.read_float(24 + bin_index * 4);
                    uint32_t loc_bin = pos / resolution;
                    values[loc.values_index + (loc_bin - loc_bin_start)] = value;
                }
            }
        }
    } else {
        throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
    }

}


void fill_values_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    std::vector<ValueStats>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset).get();
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    WigDataHeader header = read_wig_data_header(buffer);

    if (header.type == 1) { // bedgraph
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 12);
            uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
            float value = buffer.read_float(24 + i * 12 + 8);
                auto no_more_overlap = fill_values_stats_with_value(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 2) { // variable step wig
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 8);
            uint32_t end = start + header.item_span;
            float value = buffer.read_float(24 + i * 8 + 4);
                auto no_more_overlap = fill_values_stats_with_value(
                    locs, values, start_loc_index, end_loc_index, resolution,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 3) { // fixed step wig
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = header.chr_start + i * header.item_step;
            uint32_t end = start + header.item_span;
            float value = buffer.read_float(24 + i * 4);
            auto no_more_overlap = fill_values_stats_with_value(
                locs, values, start_loc_index, end_loc_index, resolution,
                start, end, value
            );
            if (no_more_overlap) break;
        }
    } else {
        throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
    }

}


void fill_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    std::vector<ExtendedValueStats>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset).get();
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    WigDataHeader header = read_wig_data_header(buffer);

    if (header.type == 1) { // bedgraph
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 12);
            uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
            float value = buffer.read_float(24 + i * 12 + 8);
                auto no_more_overlap = fill_stats_with_value(
                    locs, values, start_loc_index, end_loc_index,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 2) { // variable step wig
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = buffer.read_uint32(24 + i * 8);
            uint32_t end = start + header.item_span;
            float value = buffer.read_float(24 + i * 8 + 4);
                auto no_more_overlap = fill_stats_with_value(
                    locs, values, start_loc_index, end_loc_index,
                    start, end, value
                );
            if (no_more_overlap) break;
        }
    } else if (header.type == 3) { // fixed step wig
        for (uint16_t i = 0; i < header.item_count; ++i) {
            uint32_t start = header.chr_start + i * header.item_step;
            uint32_t end = start + header.item_span;
            float value = buffer.read_float(24 + i * 4);
            auto no_more_overlap = fill_stats_with_value(
                locs, values, start_loc_index, end_loc_index,
                start, end, value
            );
            if (no_more_overlap) break;
        }
    } else {
        throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
    }

}


void fill_zoom_values_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    std::vector<float>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset).get();
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    uint64_t record_count = node.data_size / 32;
    for (uint64_t i = 0; i < record_count; ++i) {
        ZoomDataRecord record = read_zoom_data_record(buffer, i);
        if (record.valid_count > 0) {
            float mean_value = record.sum_data / record.valid_count;
            auto no_more_overlap = fill_values_with_value(
                locs, values, start_loc_index, end_loc_index, resolution,
                record.chr_start, record.chr_end, mean_value
            );
            if (no_more_overlap) break;
        }
    }
}


void fill_zoom_values_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    uint32_t resolution,
    std::vector<ValueStats>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset).get();
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    uint64_t record_count = node.data_size / 32;
    for (uint64_t i = 0; i < record_count; ++i) {
        ZoomDataRecord record = read_zoom_data_record(buffer, i);
        if (record.valid_count > 0) {
            float mean_value = record.sum_data / record.valid_count;
            auto no_more_overlap = fill_values_stats_with_value(
                locs, values, start_loc_index, end_loc_index, resolution,
                record.chr_start, record.chr_end, mean_value
            );
            if (no_more_overlap) break;
        }
    }
}


void fill_zoom_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    const DataTreeLeaf& node,
    uint64_t start_loc_index,
    uint64_t end_loc_index,
    std::vector<ExtendedValueStats>& values) {

    ByteArray buffer = file.read(node.data_size, node.data_offset).get();
    if (uncompress_buffer_size > 0) buffer = buffer.decompress(uncompress_buffer_size);
    uint64_t record_count = node.data_size / 32;
    for (uint64_t i = 0; i < record_count; ++i) {
        ZoomDataRecord record = read_zoom_data_record(buffer, i);
        if (record.valid_count > 0) {
            float mean_value = record.sum_data / record.valid_count;
            auto no_more_overlap = fill_stats_with_value(
                locs, values, start_loc_index, end_loc_index,
                record.chr_start, record.chr_end, mean_value
            );
            if (no_more_overlap) break;
        }
    }
}


std::vector<float> read_values_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodeGenerator& tree_nodes,
    uint32_t span,
    uint32_t resolution,
    float default_value,
    int32_t zoom_level,
    uint64_t parallel,
    ProgressTracker& tracker) {
    
    uint32_t bin_count = span / resolution;
    std::vector<float> values(locs.size() * bin_count, default_value);

    std::deque<std::future<void>> futures;
    Semaphore parallel_semaphore(parallel);
    TreeNodeGeneratorNext result;
    while (!(result = tree_nodes.next()).done) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, result, resolution, &values, &parallel_semaphore, zoom_level]() {
            SemaphoreGuard guard(parallel_semaphore);
            if (zoom_level < 0) {
                fill_values_at_locs(
                    file,
                    uncompress_buffer_size,
                    locs,
                    result.node,
                    result.start_loc_index,
                    result.end_loc_index,
                    resolution,
                    values
                );
            } else {
                fill_zoom_values_at_locs(
                    file,
                    uncompress_buffer_size,
                    locs,
                    result.node,
                    result.start_loc_index,
                    result.end_loc_index,
                    resolution,
                    values
                );
            }
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    return values;
}


std::vector<float> read_values_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodeGenerator& tree_nodes,
    uint32_t span,
    uint32_t resolution,
    float default_value,
    int32_t zoom_level,
    uint64_t parallel,
    ProgressTracker& tracker) {

    std::map<uint32_t, std::unique_ptr<std::mutex>> chr_mutexes;
    for (const Loc& loc : locs) {
        if (chr_mutexes.find(loc.chr_index) == chr_mutexes.end()) {
            chr_mutexes[loc.chr_index] = std::make_unique<std::mutex>();
        }
    }
    auto lock_chrs = [&chr_mutexes](uint32_t start_chr_index, uint32_t end_chr_index) {
        std::vector<std::unique_lock<std::mutex>> locks;
        locks.reserve(end_chr_index - start_chr_index + 1);
        for (uint32_t i = start_chr_index; i <= end_chr_index; ++i) {
            if (chr_mutexes.find(i) != chr_mutexes.end()) {
                locks.emplace_back(*chr_mutexes[i]);
            }
        }
        return locks;
    };
    
    uint32_t bin_count = span / resolution;
    std::vector<ValueStats> values_stats(locs.size() * bin_count);

    std::deque<std::future<void>> futures;
    Semaphore parallel_semaphore(parallel);
    TreeNodeGeneratorNext result;
    while (!(result = tree_nodes.next()).done) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, result, resolution, &values_stats, &parallel_semaphore, zoom_level, &lock_chrs]() {
            auto locks = lock_chrs(result.node.start_chr_index, result.node.end_chr_index);
            SemaphoreGuard guard(parallel_semaphore);
            if (zoom_level < 0) {
                fill_values_stats_at_locs(
                    file,
                    uncompress_buffer_size,
                    locs,
                    result.node,
                    result.start_loc_index,
                    result.end_loc_index,
                    resolution,
                    values_stats
                );
            } else {
                fill_zoom_values_stats_at_locs(
                    file,
                    uncompress_buffer_size,
                    locs,
                    result.node,
                    result.start_loc_index,
                    result.end_loc_index,
                    resolution,
                    values_stats
                );
            }
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    std::vector<float> values(locs.size() * bin_count, default_value);
    for (uint64_t i = 0; i < values_stats.size(); ++i) {
        if (values_stats[i].count > 0) {
            values[i] = values_stats[i].sum / values_stats[i].count;
        }
    }

    return values;
}


std::vector<float> read_stats_at_locs(
    BufferedFilePool& file,
    uint32_t uncompress_buffer_size,
    const std::vector<Loc>& locs,
    TreeNodeGenerator& tree_nodes,
    float default_value,
    std::string reduce,
    int32_t zoom_level,
    uint64_t parallel,
    ProgressTracker& tracker) {

    std::vector<std::unique_lock<std::mutex>> locs_mutexes;
    locs_mutexes.reserve(locs.size());
    for (uint64_t i = 0; i < locs.size(); ++i) {
        locs_mutexes.push_back(std::unique_lock<std::mutex>());
    }
    auto lock_locs = [&locs_mutexes](uint32_t start_loc_index, uint32_t end_loc_index) {
        std::vector<std::unique_lock<std::mutex>> locks;
        locks.reserve(end_loc_index - start_loc_index + 1);
        for (uint32_t i = start_loc_index; i <= end_loc_index; ++i) {
            locks.emplace_back(std::move(locs_mutexes[i]));
        }
        return locks;
    };
    
    std::vector<ExtendedValueStats> values_stats(locs.size());

    std::deque<std::future<void>> futures;
    Semaphore parallel_semaphore(parallel);
    TreeNodeGeneratorNext result;
    while (!(result = tree_nodes.next()).done) {
        tracker.update(tree_nodes.coverage);
        auto future = std::async(std::launch::async, [&file, uncompress_buffer_size, &locs, result, &values_stats, &parallel_semaphore, zoom_level, &lock_locs]() {
            auto locks = lock_locs(result.start_loc_index, result.end_loc_index);
            SemaphoreGuard guard(parallel_semaphore);
            if (zoom_level < 0) {
                fill_stats_at_locs(
                    file,
                    uncompress_buffer_size,
                    locs,
                    result.node,
                    result.start_loc_index,
                    result.end_loc_index,
                    values_stats
                );
            } else {
                fill_zoom_stats_at_locs(
                    file,
                    uncompress_buffer_size,
                    locs,
                    result.node,
                    result.start_loc_index,
                    result.end_loc_index,
                    values_stats
                );
            }
        });
        futures.push_back(std::move(future));
        while (!futures.empty()) {
            auto &future = futures.front();
            if (future.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                future.get();
                futures.pop_front();
            } else {
                break;
            }
        }
    }
    for (auto& future : futures) future.get();
    tracker.done();

    std::vector<float> values(locs.size(), default_value);
    for (uint64_t i = 0; i < values_stats.size(); ++i) {
        if (values_stats[i].count > 0) {
            if (reduce == "mean") {
                values[i] = values_stats[i].sum / values_stats[i].count;
            } else if (reduce == "std") {
                float mean = values_stats[i].sum / values_stats[i].count;
                float variance = (values_stats[i].sum_squared / values_stats[i].count) - (mean * mean);
                values[i] = std::sqrt(variance);
            } else if (reduce == "min") {
                values[i] = values_stats[i].min;
            } else if (reduce == "max") {
                values[i] = values_stats[i].max;
            } else {
                throw std::runtime_error("reduce " + reduce + " invalid");
            }
        }
    }

    return values;
}



