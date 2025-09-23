#pragma once
#include <filesystem>

#include "common.h"
#include "kmc/config.h"

class SimulationPaths
{
    std::filesystem::path baseDir;

public:
    SimulationPaths() = default;

    SimulationPaths(const std::string &dir, const config::CommandLineConfig &config) : baseDir(dir)
    {
        if (!std::filesystem::exists(baseDir))
            std::filesystem::create_directories(baseDir);

        if (config.reportPolymers && !std::filesystem::exists(polymerOutputDir()))
            std::filesystem::create_directories(polymerOutputDir());

        if (config.reportSequences && !std::filesystem::exists(sequencesFile()))
            std::filesystem::create_directories(sequencesFile().parent_path());

        // Copy input file to output directory for record-keeping
        if (!std::filesystem::exists(inputFile()))
            std::filesystem::copy(config.inputFilepath, inputFile());
    }

    std::filesystem::path baseDirectory() const { return baseDir; }
    std::filesystem::path resultsFile() const { return baseDir / "results.csv"; }
    std::filesystem::path polymerOutputDir() const { return baseDir / "polymers"; }
    std::filesystem::path polymerFile(const int &iteration) const { return polymerOutputDir() / ("poly_" + std::to_string(iteration) + ".dat"); }
    std::filesystem::path sequencesFile() const { return baseDir / "sequences.csv"; }
    std::filesystem::path metadataFile() const { return baseDir / "metadata.yaml"; }
    std::filesystem::path inputFile() const { return baseDir / "input.txt"; }
};