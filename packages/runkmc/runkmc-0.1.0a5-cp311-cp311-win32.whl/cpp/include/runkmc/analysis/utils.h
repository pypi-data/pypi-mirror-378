#pragma once
#include "common.h"
#include "analysis/types.h"

namespace analysis
{

    static size_t getBucketIndex(size_t position, size_t chainLength, size_t numBuckets)
    {
        if (chainLength <= 1)
            return 0;

        double normalizedPos = static_cast<double>(position) / (chainLength);

        size_t bucket = static_cast<size_t>(normalizedPos * numBuckets);
        return (bucket == numBuckets) ? numBuckets - 1 : bucket;
    }

    std::vector<SequenceStats> calculatePositionalSequenceStats(const std::vector<SpeciesID> &sequence, const size_t &numBuckets)
    {
        std::vector<SequenceStats> stats(numBuckets);
        if (sequence.empty())
            return stats;

        SpeciesID currentMonomer = 0;
        size_t currentSequenceLength = 0;
        bool inSequence = false;

        for (size_t i = 0; i < sequence.size(); ++i)
        {
            size_t bucket = getBucketIndex(i, sequence.size(), numBuckets);
            SpeciesID id = sequence[i];

            // Skip non-monomer units
            if (!registry::isType(id, SpeciesType::MONOMER))
                continue;

            size_t monomerIndex = registry::getIndex(id, SpeciesType::MONOMER);
            stats[bucket].monomerCounts[monomerIndex]++;

            if (id == currentMonomer)
            {
                currentSequenceLength++;
            }
            else if (inSequence)
            {
                size_t prevIndex = registry::getIndex(currentMonomer, SpeciesType::MONOMER);
                stats[bucket].sequenceCounts[prevIndex] += 1;
                stats[bucket].sequenceLengths2[prevIndex] += currentSequenceLength * currentSequenceLength;
                currentSequenceLength = 1;
            }
            else
            {
                inSequence = true;
                currentSequenceLength = 1;
            }

            currentMonomer = id;
        }

        // Add the stats for the last sequence
        size_t bucket = getBucketIndex(sequence.size() - 1, sequence.size(), numBuckets);
        size_t lastMonomerIdx = registry::getIndex(currentMonomer, SpeciesType::MONOMER);
        stats[bucket].sequenceCounts[lastMonomerIdx] += 1;
        stats[bucket].sequenceLengths2[lastMonomerIdx] += currentSequenceLength * currentSequenceLength;

        return stats;
    }

    template <typename Func>
    void forEachStats(const RawSequenceData &sequenceData, size_t numBuckets, Func callback)
    {
        // Process sequences on-the-fly
        for (size_t i = 0; i < sequenceData.sequences.size(); ++i)
        {
            auto stats = calculatePositionalSequenceStats(sequenceData.sequences[i], numBuckets);
            callback(i, stats);
        }

        // Process precomputed
        for (size_t i = 0; i < sequenceData.precomputedStats.size(); ++i)
        {
            callback(sequenceData.sequences.size() + i, sequenceData.precomputedStats[i]);
        }
    }

    /*
     */
    SequenceSummary calculateSequenceSummary(const analysis::RawSequenceData &sequenceData)
    {
        size_t numPolymers = sequenceData.length;

        size_t numMonomers = registry::getNumOf(SpeciesType::MONOMER);
        size_t numMetrics = SequenceStats::numMetrics();
        size_t numBuckets = NUM_BUCKETS;

        std::vector<SequenceStats> avgPositionalStats(numBuckets);
        std::vector<Eigen::MatrixXd> sequenceStatsTensor(numBuckets); // numBuckets matrices
        for (auto &matrix : sequenceStatsTensor)
            matrix = Eigen::MatrixXd::Zero(numPolymers, numMonomers * numMetrics); // Each matrix is (polymers × stats)

        forEachStats(
            sequenceData,
            numBuckets,
            [&](size_t index, const std::vector<SequenceStats> &allStats)
            {
                for (size_t bucket = 0; bucket < numBuckets; ++bucket)
                {
                    const auto &stats = allStats[bucket];
                    for (size_t monIdx = 0; monIdx < numMonomers; ++monIdx)
                    {
                        size_t colBase = monIdx * numMetrics;
                        sequenceStatsTensor[bucket](index, colBase + 0) = stats.monomerCounts[monIdx];
                        sequenceStatsTensor[bucket](index, colBase + 1) = stats.sequenceCounts[monIdx];
                        sequenceStatsTensor[bucket](index, colBase + 2) = stats.sequenceLengths2[monIdx];

                        avgPositionalStats[bucket].monomerCounts[monIdx] += stats.monomerCounts[monIdx];
                        avgPositionalStats[bucket].sequenceCounts[monIdx] += stats.sequenceCounts[monIdx];
                        avgPositionalStats[bucket].sequenceLengths2[monIdx] += stats.sequenceLengths2[monIdx];
                    }
                }
            });

        return SequenceSummary{sequenceStatsTensor, avgPositionalStats};
    }

    Eigen::MatrixXd calculateSequenceStatsMatrix(const std::vector<Eigen::MatrixXd> &sequenceStatsTensor)
    // Calculate the average sequence statistics (across all buckets) per polymer
    {
        if (sequenceStatsTensor.empty())
            return Eigen::MatrixXd();

        size_t numBuckets = sequenceStatsTensor.size();
        size_t numPolymers = sequenceStatsTensor[0].rows();
        size_t numCols = sequenceStatsTensor[0].cols();

        // Result matrix: polymers × (monomers*fields)
        Eigen::MatrixXd result = Eigen::MatrixXd::Zero(numPolymers, numCols);

        // Get the average stats (across all buckets) for each polymer
        for (size_t i = 0; i < numPolymers; ++i)
        {
            for (size_t bucket = 0; bucket < numBuckets; ++bucket)
            {
                result.row(i) += sequenceStatsTensor[bucket].row(i);
            }
            result.row(i) /= numBuckets;
        }

        return result;
    }
}
