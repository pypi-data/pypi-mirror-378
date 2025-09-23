#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/numpy.h>

#include "main.cpp"

namespace py = pybind11;


py::dict py_get_chr_sizes(const std::string& genome) {
    return py::cast(get_chr_sizes(genome));
}


class PyBigwigReader {
    std::shared_ptr<BigwigReader> reader;

public:
    py::dict main_header;
    py::list zoom_headers;
    py::dict total_summary;
    py::dict chr_tree_header;
    py::dict chr_sizes;

    PyBigwigReader(
        const std::string& path,
        uint64_t parallel = 24,
        float zoom_correction = 0.33
    ) {
        reader = std::make_shared<BigwigReader>(path, parallel, zoom_correction);
        auto headers_future = reader->read_headers();
        headers_future.get();

        main_header[py::str("magic")] = reader->main_header.magic;
        main_header[py::str("version")] = reader->main_header.version;
        main_header[py::str("zoom_levels")] = reader->main_header.zoom_levels;
        main_header[py::str("chr_tree_offset")] = reader->main_header.chr_tree_offset;
        main_header[py::str("full_data_offset")] = reader->main_header.full_data_offset;
        main_header[py::str("full_index_offset")] = reader->main_header.full_index_offset;
        main_header[py::str("field_count")] = reader->main_header.field_count;
        main_header[py::str("defined_field_count")] = reader->main_header.defined_field_count;
        main_header[py::str("auto_sql_offset")] = reader->main_header.auto_sql_offset;
        main_header[py::str("total_summary_offset")] = reader->main_header.total_summary_offset;
        main_header[py::str("uncompress_buffer_size")] = reader->main_header.uncompress_buffer_size;
        main_header[py::str("reserved")] = reader->main_header.reserved;

        total_summary[py::str("bases_covered")] = reader->total_summary.bases_covered;
        total_summary[py::str("min_value")] = reader->total_summary.min_value;
        total_summary[py::str("max_value")] = reader->total_summary.max_value;
        total_summary[py::str("sum_data")] = reader->total_summary.sum_data;
        total_summary[py::str("sum_squared")] = reader->total_summary.sum_squared;

        chr_tree_header[py::str("magic")] = reader->chr_tree_header.magic;
        chr_tree_header[py::str("block_size")] = reader->chr_tree_header.block_size;
        chr_tree_header[py::str("key_size")] = reader->chr_tree_header.key_size;
        chr_tree_header[py::str("value_size")] = reader->chr_tree_header.value_size;
        chr_tree_header[py::str("item_count")] = reader->chr_tree_header.item_count;
        chr_tree_header[py::str("reserved")] = reader->chr_tree_header.reserved;

        for (const auto& zoom_header : reader->zoom_headers) {
            py::dict zoom_header_dict;
            zoom_header_dict[py::str("reduction_level")] = zoom_header.reduction_level;
            zoom_header_dict[py::str("reserved")] = zoom_header.reserved;
            zoom_header_dict[py::str("data_offset")] = zoom_header.data_offset;
            zoom_header_dict[py::str("index_offset")] = zoom_header.index_offset;
            zoom_headers.append(zoom_header_dict);
        }
        
        for (const auto& chr : reader->chr_map) {
            chr_sizes[py::str(chr.first)] = chr.second.chr_size;
        }
    }
    
    py::array_t<float> read_values(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        uint32_t span,
        uint32_t resolution = 1,
        float def_value = 0.0f,
        std::string binning = "none",
        int32_t zoom = 0,
        py::object progress = py::none()) {

        std::function<void(uint64_t, uint64_t)> progress_callback = nullptr;
        if (!progress.is_none()) {
            progress_callback = [progress](uint64_t current, uint64_t total) {
                progress(current, total);
            };
        }

        auto values = reader->read_values(
            chr_ids, starts, span, resolution, def_value, binning, zoom, progress_callback
        );
        
        uint64_t bin_count = (span + resolution - 1) / resolution;
        uint64_t row_count = chr_ids.size();
        uint64_t col_count = bin_count;
        std::vector<ssize_t> shape = {static_cast<ssize_t>(row_count), static_cast<ssize_t>(col_count)};
        std::vector<ssize_t> strides = {static_cast<ssize_t>(col_count * sizeof(float)), static_cast<ssize_t>(sizeof(float))};
        return py::array_t<float>(shape, strides, values.data());
    }

    py::array_t<float> quantify(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        uint32_t span,
        uint32_t resolution = 1,
        float def_value = 0.0f,
        std::string reduce = "mean",
        int32_t zoom = 0,
        py::object progress = py::none()) {

        std::function<void(uint64_t, uint64_t)> progress_callback = nullptr;
        if (!progress.is_none()) {
            progress_callback = [progress](uint64_t current, uint64_t total) {
                progress(current, total);
            };
        }

        auto values = reader->quantify(
            chr_ids, starts, span, resolution, def_value, reduce, zoom, progress_callback
        );
        
        std::vector<ssize_t> shape = {static_cast<ssize_t>(values.size())};
        std::vector<ssize_t> strides = {static_cast<ssize_t>(sizeof(float))};
        return py::array_t<float>(shape, strides, values.data());
    }

    py::array_t<float> profile(
        const std::vector<std::string>& chr_ids,
        const std::vector<int64_t>& starts,
        uint32_t span,
        uint32_t resolution = 1,
        float def_value = 0.0f,
        std::string binning = "none",
        std::string reduce = "mean",
        int32_t zoom = 0,
        py::object progress = py::none()) {

        std::function<void(uint64_t, uint64_t)> progress_callback = nullptr;
        if (!progress.is_none()) {
            progress_callback = [progress](uint64_t current, uint64_t total) {
                progress(current, total);
            };
        }

        auto values = reader->profile(
            chr_ids, starts, span, resolution, def_value, binning, reduce, zoom, progress_callback
        );
        
        std::vector<ssize_t> shape = {static_cast<ssize_t>(values.size())};
        std::vector<ssize_t> strides = {static_cast<ssize_t>(sizeof(float))};
        return py::array_t<float>(shape, strides, values.data());
    }

    void to_bedgraph(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom = -1
    ) {
        reader->to_bedgraph(output_path, chr_ids, zoom);
    }
    
    void to_wig(
        const std::string& output_path,
        std::vector<std::string> chr_ids = {},
        int32_t zoom = -1
    ) {
        reader->to_wig(output_path, chr_ids, zoom);
    }

};


PYBIND11_MODULE(bigwig_io, m, py::mod_gil_not_used()) {
    m.doc() = "Python bindings for bigwig_io C++ library";

    m.def("get_chr_sizes", &py_get_chr_sizes, "Get chromosome sizes for a given genome",
        py::arg("genome"));

    py::class_<PyBigwigReader>(m, "BigwigReader")
        .def(py::init<const std::string&, uint64_t>(), "Create a BigWig reader from file path",
            py::arg("path"), py::arg("parallel") = 24)
        .def_readonly("main_header", &PyBigwigReader::main_header)
        .def_readonly("total_summary", &PyBigwigReader::total_summary)
        .def_readonly("chr_tree_header", &PyBigwigReader::chr_tree_header)
        .def_readonly("zoom_headers", &PyBigwigReader::zoom_headers)
        .def_readonly("chr_sizes", &PyBigwigReader::chr_sizes)
        .def("read_values", &PyBigwigReader::read_values,
            "Read values from BigWig file",
            py::arg("chr_ids"), py::arg("starts"), py::arg("span"), 
            py::arg("resolution") = 1, py::arg("def_value") = 0.0f,
            py::arg("binning") = "none",
            py::arg("zoom") = 0,
            py::arg("progress") = py::none())
        .def("quantify", &PyBigwigReader::quantify,
            "Quantify values from BigWig file",
            py::arg("chr_ids"), py::arg("starts"), py::arg("span"), 
            py::arg("resolution") = 1, py::arg("def_value") = 0.0f,
            py::arg("reduce") = "mean",
            py::arg("zoom") = 0,
            py::arg("progress") = py::none())
        .def("profile", &PyBigwigReader::profile,
            "Profile values from BigWig file",
            py::arg("chr_ids"), py::arg("starts"), py::arg("span"),
            py::arg("resolution") = 1, py::arg("def_value") = 0.0f,
            py::arg("binning") = "none",
            py::arg("reduce") = "mean",
            py::arg("zoom") = 0,
            py::arg("progress") = py::none())
        .def("to_bedgraph", &PyBigwigReader::to_bedgraph, 
            "Convert BigWig file to bedGraph format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<std::string>{},
            py::arg("zoom") = -1)
        .def("to_wig", &PyBigwigReader::to_wig,
            "Convert BigWig file to WIG format",
            py::arg("output_path"),
            py::arg("chr_ids") = std::vector<std::string>{},
            py::arg("zoom") = -1);

}
