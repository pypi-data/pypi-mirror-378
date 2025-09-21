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
#include <cmath>

#include "structs.hpp"
#include "byte_util.cpp"
#include "file_util.cpp"
#include "util.cpp"
#include "reader_header.cpp"
#include "reader_values.cpp"






class BigwigReader {
    std::string path;
    uint64_t parallel;
    std::shared_ptr<BufferedFilePool> file;

public:
    MainHeader main_header;
    std::vector<ZoomHeader> zoom_headers;
    TotalSummary total_summary;
    ChrTreeHeader chr_tree_header;
    std::vector<ChrTreeLeaf> chr_tree;
    std::map<std::string, ChrTreeLeaf> chr_map;

    BigwigReader(
        const std::string& path_,
        uint64_t parallel_ = 24
    ) : path(path_), parallel(parallel_) {
        file = std::make_shared<BufferedFilePool>(path, "r", parallel);
    }

    std::future<void> read_headers() {
        return std::async(std::launch::async, [this]() {
            main_header = read_main_header(*file);
            zoom_headers = read_zoom_headers(*file, main_header.zoom_levels);
            total_summary = read_total_summary(*file, main_header.total_summary_offset);
            chr_tree_header = read_chr_tree_header(*file, main_header.chr_tree_offset);
            chr_tree = read_chr_tree(*file, main_header.chr_tree_offset + 32, chr_tree_header.key_size);
            chr_map = convert_chr_tree_to_map(chr_tree);
        });
    }

    int32_t select_zoom_level(uint32_t resolution) {
        int32_t best_level = -1;
        uint32_t best_reduction = 0;
        resolution /= 2;
        for (uint16_t i = 0; i < zoom_headers.size(); ++i) {
            uint32_t reduction = zoom_headers[i].reduction_level;
            if (reduction <= resolution && reduction > best_reduction) {
                best_reduction = reduction;
                best_level = i;
            }
        }
        return best_level;
    }

    ChrTreeLeaf get_chr_entry(const std::string& chr_id) {
        std::string chr_key = chr_id.substr(0, chr_tree_header.key_size);
        auto it = chr_map.find(chr_key);
        if (it == chr_map.end()) {
            if (chr_id.length() >= 3 && chr_id.substr(0, 3) == "chr") {
                chr_key = chr_id.substr(3).substr(0, chr_tree_header.key_size);
            } else {
                chr_key = ("chr" + chr_id).substr(0, chr_tree_header.key_size);
            }
            it = chr_map.find(chr_key);
            if (it == chr_map.end()) {
                std::string available_keys;
                for (const auto& entry : chr_map) {
                    if (!available_keys.empty()) available_keys += ", ";
                    available_keys += entry.first;
                }
                throw std::runtime_error("chr " + chr_id + " not in bigwig (" + available_keys + ")");
            }
        }
        return it->second;
    }

    std::vector<Loc> parse_locs(
        const std::vector<std::string>& chr_ids,
        const std::vector<uint64_t>& starts,
        const std::vector<uint64_t>& ends,
        uint32_t span = 0,
        uint32_t resolution = 1) {

        std::vector<Loc> locs(chr_ids.size());
        uint64_t values_offset = 0;
        for (uint64_t i = 0; i < chr_ids.size(); ++i) {
            auto chr_entry = get_chr_entry(chr_ids[i]);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = starts[i];
            loc.end = span > 0 ? loc.start + span : ends[i];
            loc.input_index = i;
            loc.values_index = values_offset;
            locs[i] = loc;
            values_offset += (loc.end - loc.start) / resolution;
        }
        std::sort(locs.begin(), locs.end(), [](const Loc& a, const Loc& b) {
            return std::tie(a.chr_index, a.start) < std::tie(b.chr_index, b.start);
        });
        return locs;
    }

    uint64_t get_coverage(const std::vector<Loc>& locs) {
        uint64_t coverage = 0;
        for (const auto& loc : locs) {
            coverage += (loc.end - loc.start);
        }
        return coverage;
    }

    std::vector<float> read_values(
        const std::vector<std::string>& chr_ids,
        const std::vector<uint64_t>& starts,
        uint32_t span,
        uint32_t resolution = 1,
        float default_value = 0.0f,
        std::string binning = "none",
        bool use_zoom = true,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {
        
        auto locs = parse_locs(chr_ids, starts, {}, span, resolution);
        ProgressTracker tracker(get_coverage(locs), progress);

        if (resolution == 0) resolution = span;
        int32_t zoom_level = use_zoom ? select_zoom_level(resolution) : -1;
        uint64_t tree_offset = (zoom_level < 0) ? 
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_level].index_offset + 48;
        TreeNodeGenerator tree_nodes(*file, locs, tree_offset);

        if (binning == "none") {
            return read_values_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                span,
                resolution,
                default_value,
                zoom_level,
                tracker
            );
        } else if (binning == "mean") {
            return read_values_stats_at_locs(
                *file,
                main_header.uncompress_buffer_size,
                locs,
                tree_nodes,
                span,
                resolution,
                default_value,
                zoom_level,
                tracker
            );
        } else {
            throw std::runtime_error("binning " + binning + " invalid");
        }

    }

    std::vector<float> quantify(
        const std::vector<std::string>& chr_ids,
        const std::vector<uint64_t>& starts,
        uint32_t span,
        uint32_t resolution = 1,
        float default_value = 0.0f,
        std::string reduce = "mean",
        bool use_zoom = true,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {
        
        auto locs = parse_locs(chr_ids, starts, {}, span, resolution);
        ProgressTracker tracker(get_coverage(locs), progress);

        if (resolution == 0) resolution = span;
        int32_t zoom_level = use_zoom ? select_zoom_level(resolution) : -1;
        uint64_t tree_offset = (zoom_level < 0) ? 
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_level].index_offset + 48;
        TreeNodeGenerator tree_nodes(*file, locs, tree_offset);

        return read_stats_at_locs(
            *file,
            main_header.uncompress_buffer_size,
            locs,
            tree_nodes,
            default_value,
            reduce,
            zoom_level,
            tracker
        );

    }

    std::vector<float> profile(
        const std::vector<std::string>& chr_ids,
        const std::vector<uint64_t>& starts,
        uint32_t span,
        uint32_t resolution = 1,
        float default_value = 0.0f,
        std::string binning = "none",
        std::string reduce = "mean",
        bool use_zoom = true,
        std::function<void(uint64_t, uint64_t)> progress = nullptr) {
        
        auto values = read_values(
            chr_ids, starts, span, resolution, default_value, binning, use_zoom, progress
        );

        uint32_t bin_count = values.size() / chr_ids.size();
        std::vector<float> profile(bin_count, std::nan(""));
        for (uint32_t col = 0; col < bin_count; ++col) {
            uint64_t count = 0;
            for (uint64_t row = 0; row < chr_ids.size(); ++row) {
                auto value = values[row * bin_count + col];
                if (std::isnan(value)) continue;
                count += 1;
                if (reduce == "mean" || reduce == "sum") {
                    profile[col] += value;
                } else if (reduce == "min") {
                    if (value < profile[col] || row == 0) {
                        profile[col] = value;
                    }
                } else if (reduce == "max") {
                    if (value > profile[col] || row == 0) {
                        profile[col] = value;
                    }
                } else {
                    throw std::runtime_error("reduce " + reduce + " invalid");
                }
            }
            if (reduce == "mean" && count > 0) {
                profile[col] /= count;
            }
        }
        return profile;

    }

    void to_bedgraph(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom_level = -1
    ) {
        std::vector<Loc> locs;
        if (chr_ids.empty()) chr_ids = get_map_keys(chr_map);
        for (std::string chr_id : chr_ids) {
            auto chr_entry = get_chr_entry(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.end = chr_entry.chr_size;
            locs.push_back(loc);
        }

        uint64_t tree_offset = (zoom_level < 0) ? 
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_level].index_offset + 48;
        TreeNodeGenerator generator(*file, locs, tree_offset);

        auto output_file = open_file(output_path, "w");
        auto write_line = [&](std::string chr_id, uint32_t start, uint32_t end, float value) {
            std::string line =
                chr_id + "\t" +
                std::to_string(start) + "\t" +
                std::to_string(end) + "\t" +
                std::to_string(value) + "\n";
            output_file->write_string(line);
        };

        TreeNodeGeneratorNext result;
        while (!(result = generator.next()).done) {
            DataTreeLeaf node = result.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            if (zoom_level >= 0) {
                uint64_t record_count = node.data_size / 32;
                for (uint64_t i = 0; i < record_count; ++i) {
                    ZoomDataRecord record = read_zoom_data_record(buffer, i);
                    std::string chr_id = chr_tree[record.chr_index].key;
                    if (record.valid_count > 0) {
                        float value = record.sum_data / record.valid_count;
                        write_line(chr_id, record.chr_start, record.chr_end, value);
                    }
                }
                continue;
            }
            WigDataHeader header = read_wig_data_header(buffer);
            std::string chr_id = chr_tree[header.chr_index].key;
            if (header.type == 1) { // bedgraph
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 12);
                    uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
                    float value = buffer.read_float(24 + i * 12 + 8);
                    write_line(chr_id, start, end, value);
                }
            } else if (header.type == 2) { // variable step wig
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 8);
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 8 + 4);
                    write_line(chr_id, start, end, value);
                }
            } else if (header.type == 3) { // fixed step wig
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = header.chr_start + i * header.item_step;
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 4);
                    write_line(chr_id, start, end, value);
                }
            } else {
                throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
            }
        }
    }

    void to_wig(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom_level = -1
    ) {
        std::vector<Loc> locs;
        if (chr_ids.empty()) chr_ids = get_map_keys(chr_map);
        for (std::string chr_id : chr_ids) {
            auto chr_entry = get_chr_entry(chr_id);
            Loc loc;
            loc.chr_index = chr_entry.chr_index;
            loc.start = 0;
            loc.end = chr_entry.chr_size;
            locs.push_back(loc);
        }

        uint64_t tree_offset = (zoom_level < 0) ? 
            main_header.full_index_offset + 48 : 
            zoom_headers[zoom_level].index_offset + 48;
        TreeNodeGenerator generator(*file, locs, tree_offset);

        auto output_file = open_file(output_path, "w");
        auto write_header_line = [&](std::string chr_id, uint32_t start, int64_t span) {
            std::string line =
                "fixedStep chrom=" + chr_id +
                " start=" + std::to_string(start + 1) +
                " step=" + std::to_string(span) +
                " span=" + std::to_string(span) + "\n";
            output_file->write_string(line);
        };
        
        TreeNodeGeneratorNext result;
        while (!(result = generator.next()).done) {
            DataTreeLeaf node = result.node;
            ByteArray buffer = file->read(node.data_size, node.data_offset).get();
            if (main_header.uncompress_buffer_size > 0) buffer = buffer.decompress(main_header.uncompress_buffer_size);
            int64_t span = -1;
            if (zoom_level >= 0) {
                uint64_t record_count = node.data_size / 32;
                for (uint64_t i = 0; i < record_count; ++i) {
                    ZoomDataRecord record = read_zoom_data_record(buffer, i);
                    std::string chr_id = chr_tree[record.chr_index].key;
                    if (record.valid_count > 0) {
                        float value = record.sum_data / record.valid_count;
                        if (record.chr_end - record.chr_start != span) {
                            span = record.chr_end - record.chr_start;
                            write_header_line(chr_id, record.chr_start, span);
                        }
                        output_file->write_string(std::to_string(value) + "\n");
                    }
                }
                continue;
            }
            WigDataHeader header = read_wig_data_header(buffer);
            std::string chr_id = chr_tree[header.chr_index].key;
            if (header.type == 1) { // bedgraph
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 12);
                    uint32_t end = buffer.read_uint32(24 + i * 12 + 4);
                    float value = buffer.read_float(24 + i * 12 + 8);
                    if (end - start != span) {
                        span = end - start;
                        write_header_line(chr_id, start, span);
                    }
                    output_file->write_string(std::to_string(value) + "\n");
                }
            } else if (header.type == 2) { // variable step wig
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = buffer.read_uint32(24 + i * 8);
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 8 + 4);
                    if (end - start != span) {
                        span = end - start;
                        write_header_line(chr_id, start, span);
                    }
                    output_file->write_string(std::to_string(value) + "\n");
                }
            } else if (header.type == 3) { // fixed step wig
                for (uint16_t i = 0; i < header.item_count; ++i) {
                    uint32_t start = header.chr_start + i * header.item_step;
                    uint32_t end = start + header.item_span;
                    float value = buffer.read_float(24 + i * 4);
                    if (end - start != span) {
                        span = end - start;
                        write_header_line(chr_id, start, span);
                    }
                    output_file->write_string(std::to_string(value) + "\n");
                }
            } else {
                throw std::runtime_error("wig data type " + std::to_string(header.type) + " invalid");
            }
        }
    }


};
