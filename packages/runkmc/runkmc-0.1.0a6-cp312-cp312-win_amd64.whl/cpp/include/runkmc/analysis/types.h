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

        const static size_t NUM_METRICS = 3;

        SequenceStats()
        {
            monomerCounts.resize(registry::NUM_MONOMERS, 0);
            sequenceCounts.resize(registry::NUM_MONOMERS, 0);
            sequenceLengths2.resize(registry::NUM_MONOMERS, 0);
        }

        static size_t SIZE()
        {
            return registry::NUM_MONOMERS * NUM_METRICS;
        }

        SequenceStats &operator+=(const SequenceStats &other)
        {
            for (size_t i = 0; i < registry::NUM_MONOMERS; ++i)
            {
                monomerCounts[i] += other.monomerCounts[i];
                sequenceCounts[i] += other.sequenceCounts[i];
                sequenceLengths2[i] += other.sequenceLengths2[i];
            }
            return *this;
        }

        Eigen::VectorXd toEigen() const
        {
            Eigen::VectorXd result(SIZE());
            for (size_t i = 0; i < registry::NUM_MONOMERS; ++i)
            {
                result(i * NUM_METRICS + 0) = static_cast<double>(monomerCounts[i]);
                result(i * NUM_METRICS + 1) = static_cast<double>(sequenceCounts[i]);
                result(i * NUM_METRICS + 2) = static_cast<double>(sequenceLengths2[i]);
            }
            return result;
        }
    };

    struct _SequenceSummary
    {
        std::vector<Eigen::MatrixXd> sequenceStatsTensor;
        std::vector<SequenceStats> avgPositionalStats;

        _SequenceSummary(std::vector<Eigen::MatrixXd> t, std::vector<SequenceStats> a)
            : sequenceStatsTensor(t), avgPositionalStats(a) {}
    };

    struct SequenceSummary
    {
        Eigen::MatrixXd sequenceStatsMatrix;        // (polymers x (SequenceStats))
        std::vector<SequenceStats> positionalStats; // (buckets x (monomers*fields))
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