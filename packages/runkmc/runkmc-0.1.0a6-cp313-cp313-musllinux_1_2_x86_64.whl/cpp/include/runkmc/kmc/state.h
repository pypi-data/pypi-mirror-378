#pragma once
#include "common.h"
struct KMCState
{
    uint64_t iteration = 0;
    uint64_t kmcStep = 0;
    double kmcTime = 0;
    double simulationTime = 0;
    double simulationTimePer1e6Steps = 0;
    double NAV = 0;

    static std::vector<std::string> getTitles()
    {
        return {"Iteration", "KMC Step", "KMC Time", "Simulation Time", "Simulation Time per 1e6 KMC Steps", "NAV"};
    }

    std::vector<std::string> getDataAsVector() const
    {
        std::vector<std::string> output;
        output.push_back(std::to_string(iteration));
        output.push_back(std::to_string(kmcStep));
        output.push_back(std::to_string(kmcTime));
        output.push_back(std::to_string(simulationTime));
        output.push_back(std::to_string(simulationTimePer1e6Steps));
        output.push_back(std::to_string(NAV));
        return output;
    }
};

struct SpeciesState
{
    std::vector<double> unitConversions;
    std::vector<uint64_t> unitCounts;
    std::vector<uint64_t> polymerCounts;
    double totalConversion;

    static std::vector<std::string> getTitles()
    {
        std::vector<std::string> names;

        auto unitNames = registry::getAllUnitNames();
        auto polymerGroupNames = registry::getNamesOf(SpeciesType::POLYMER);

        // Unit conversions
        for (const auto &name : unitNames)
            names.push_back(name + " Conversion");
        names.push_back("Total Conversion");

        // Unit counts
        for (const auto &name : unitNames)
            names.push_back(name + " Count");

        // Polymer counts
        for (const auto &name : polymerGroupNames)
            names.push_back(name + " Count");

        return names;
    }

    std::vector<std::string> getDataAsVector() const
    {
        std::vector<std::string> output;

        // Unit conversions
        for (const auto &conv : unitConversions)
            output.push_back(std::to_string(conv));
        output.push_back(std::to_string(totalConversion));

        // Unit counts
        for (const auto &count : unitCounts)
            output.push_back(std::to_string(count));

        // Polymer counts
        for (const auto &count : polymerCounts)
            output.push_back(std::to_string(count));

        return output;
    }
};

struct AnalysisState
{
    double nAvgChainLength = 0;
    double wAvgChainLength = 0;
    double chainLengthDispersity = 0;

    double nAvgMolecularWeight = 0;
    double wAvgMolecularWeight = 0;
    double molecularWeightDispersity = 0;

    // Sequence statistics for each monomer type
    std::vector<double> nAvgComposition;
    std::vector<double> nAvgSequenceLengths;
    std::vector<double> wAvgSequenceLengths;
    std::vector<double> sequenceLengthDispersities;

    AnalysisState()
    {
        nAvgComposition.resize(registry::NUM_MONOMERS, 0);
        nAvgSequenceLengths.resize(registry::NUM_MONOMERS, 0);
        wAvgSequenceLengths.resize(registry::NUM_MONOMERS, 0);
        sequenceLengthDispersities.resize(registry::NUM_MONOMERS, 0);
    }

    static std::vector<std::string> getTitles()
    {

        std::vector<std::string> names = {
            "nAvgChainLength",
            "wAvgChainLength",
            "chainLengthDispersity",
            "nAvgMolecularWeight",
            "wAvgMolecularWeight",
            "molecularWeightDispersity",
        };

        auto monomerNames = registry::getNamesOf(SpeciesType::MONOMER);

        for (const auto &monomerName : monomerNames)
        {
            names.push_back("nAvgComposition_" + monomerName);
            names.push_back("nAvgSequenceLength_" + monomerName);
            names.push_back("wAvgSequenceLength_" + monomerName);
            names.push_back("sequenceLengthDispersity_" + monomerName);
        }

        return names;
    }

    std::vector<std::string> getDataAsVector() const
    {
        std::vector<std::string> output;

        output.push_back(std::to_string(nAvgChainLength));
        output.push_back(std::to_string(wAvgChainLength));
        output.push_back(std::to_string(chainLengthDispersity));

        output.push_back(std::to_string(nAvgMolecularWeight));
        output.push_back(std::to_string(wAvgMolecularWeight));
        output.push_back(std::to_string(molecularWeightDispersity));

        for (size_t i = 0; i < registry::NUM_MONOMERS; ++i)
        {
            output.push_back(std::to_string(nAvgComposition[i]));
            output.push_back(std::to_string(nAvgSequenceLengths[i]));
            output.push_back(std::to_string(wAvgSequenceLengths[i]));
            output.push_back(std::to_string(sequenceLengthDispersities[i]));
        }

        return output;
    }
};

struct SequenceState
{
    KMCState kmcState;
    std::vector<analysis::SequenceStats> stats;

    static std::vector<std::string> getTitles()
    {
        std::vector<std::string> names = {"Iteration", "KMC Time", "Bucket"};
        for (const auto &monomerName : registry::getNamesOf(SpeciesType::MONOMER))
        {
            names.push_back("MonomerCount_" + monomerName);
            names.push_back("SequenceCount_" + monomerName);
            names.push_back("SequenceLengths2" + monomerName);
        }
        return names;
    }

    std::vector<std::string> getDataAsVector(size_t bucket) const
    {
        std::vector<std::string> output;
        output.push_back(std::to_string(kmcState.iteration));
        output.push_back(std::to_string(kmcState.kmcTime));
        output.push_back(std::to_string(bucket));

        auto numMonomers = registry::getNumOf(SpeciesType::MONOMER);
        for (size_t i = 0; i < numMonomers; ++i)
        {
            output.push_back(std::to_string(stats[bucket].monomerCounts[i]));
            output.push_back(std::to_string(stats[bucket].sequenceCounts[i]));
            output.push_back(std::to_string(stats[bucket].sequenceLengths2[i]));
        }
        return output;
    }
};

struct SystemState
{
    KMCState kmc;
    SpeciesState species;
    AnalysisState analysis;
    SequenceState sequence;
};