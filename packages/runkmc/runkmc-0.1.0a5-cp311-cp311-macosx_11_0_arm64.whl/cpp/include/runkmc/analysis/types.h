#pragma once
#include <Eigen/Core>

#include "common.h"

namespace analysis
{
    struct SequenceStats
    {
        std::vector<uint64_t> monomerCounts;
        std::vector<uint64_t> sequenceCounts;
        std::vector<uint64_t> sequenceLengths2;

        static size_t numMetrics() { return 3; }

        SequenceStats()
        {
            size_t numMonomers = registry::getNumOf(SpeciesType::MONOMER);
            monomerCounts.resize(numMonomers, 0);
            sequenceCounts.resize(numMonomers, 0);
            sequenceLengths2.resize(numMonomers, 0);
        }
    };

    struct SequenceSummary
    {
        std::vector<Eigen::MatrixXd> sequenceStatsTensor;
        std::vector<SequenceStats> avgPositionalStats;

        SequenceSummary(std::vector<Eigen::MatrixXd> t, std::vector<SequenceStats> a)
            : sequenceStatsTensor(t), avgPositionalStats(a) {}
    };

    struct RawSequenceData
    {
        std::vector<std::vector<SpeciesID>> sequences;
        std::vector<std::vector<SequenceStats>> precomputedStats;
        size_t length;

        RawSequenceData(size_t n)
        {
            sequences.reserve(n);
            precomputedStats.reserve(n);
            length = n;
        }
    };
}