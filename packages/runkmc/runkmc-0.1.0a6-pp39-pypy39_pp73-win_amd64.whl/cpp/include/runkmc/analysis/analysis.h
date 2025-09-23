#pragma once
#include "common.h"
#include "kmc/state.h"
#include "analysis/utils.h"

namespace analysis
{
    void analyzeChainLengthDist(Eigen::MatrixXd &sequenceStatsMatrix, const std::vector<double> &monomerFWs, AnalysisState &state)
    {
        if (sequenceStatsMatrix.rows() == 0 || sequenceStatsMatrix.cols() == 0)
            return;

        // Extract monomer count distribution (shape: numPolymers x numMonomers)
        Eigen::MatrixXd monomerCountDist = sequenceStatsMatrix.leftCols(registry::NUM_MONOMERS);

        // Chain length calculations (Get chain lengths by summing monomer counts)
        Eigen::VectorXd chainLengths = monomerCountDist.rowwise().sum();
        state.nAvgChainLength = chainLengths.mean();
        if (state.nAvgChainLength != 0.0)
        {
            state.wAvgChainLength = chainLengths.array().square().mean() / state.nAvgChainLength;
            state.chainLengthDispersity = state.wAvgChainLength / state.nAvgChainLength;
        }

        // If any monomer has FW of 0, skip molecular weight calculations
        // and set molecular weight averages to chain length averages
        Eigen::VectorXd FWs = Eigen::Map<const Eigen::VectorXd>(monomerFWs.data(), monomerFWs.size());
        if ((FWs.array() == 0.0).any())
        {
            state.nAvgMolecularWeight = state.nAvgChainLength;
            state.wAvgMolecularWeight = state.wAvgChainLength;
            state.molecularWeightDispersity = state.chainLengthDispersity;
        }

        // Molecular weight calculations
        Eigen::MatrixXd weightedMonomerCountDist = monomerCountDist.array().rowwise() * FWs.transpose().array();
        Eigen::VectorXd molecularWeights = weightedMonomerCountDist.rowwise().sum();
        state.nAvgMolecularWeight = molecularWeights.mean();
        if (state.nAvgMolecularWeight != 0.0)
        {
            state.wAvgMolecularWeight = molecularWeights.array().square().mean() / state.nAvgMolecularWeight;
            state.molecularWeightDispersity = state.wAvgMolecularWeight / state.nAvgMolecularWeight;
        }
    }

    void analyzeSequenceLengthDist(Eigen::MatrixXd &sequenceStatsMatrix, AnalysisState &state)
    {

        if (sequenceStatsMatrix.rows() == 0 || sequenceStatsMatrix.cols() < SequenceStats::SIZE())
            return;

        // Sum stats over all polymers
        auto totalStats = sequenceStatsMatrix.colwise().sum();
        double totalMonomerCounts = totalStats.leftCols(registry::NUM_MONOMERS).sum();

        for (size_t i = 0; i < registry::NUM_MONOMERS; ++i)
        {
            size_t base = i * SequenceStats::NUM_METRICS;
            auto monomerCounts = totalStats(base + 0);
            auto sequenceCounts = totalStats(base + 1);
            auto sequenceLengths2 = totalStats(base + 2);

            if (sequenceCounts > 0 && monomerCounts > 0)
            {
                state.nAvgComposition[i] = monomerCounts / totalMonomerCounts;
                state.nAvgSequenceLengths[i] = monomerCounts / sequenceCounts;
                state.wAvgSequenceLengths[i] = sequenceLengths2 / monomerCounts;
                state.sequenceLengthDispersities[i] = state.wAvgSequenceLengths[i] / state.nAvgSequenceLengths[i];
            }
        }
    }

    void analyze(const SpeciesSet &speciesSet, SystemState &systemState)
    {
        auto sequenceData = speciesSet.getRawSequenceData();
        auto summary = analysis::calculateSequenceSummary(sequenceData);

        SequenceState sequenceState = SequenceState{systemState.kmc, summary.positionalStats};

        AnalysisState analysisState;
        analysis::analyzeChainLengthDist(summary.sequenceStatsMatrix, speciesSet.getMonomerFWs(), analysisState);
        analysis::analyzeSequenceLengthDist(summary.sequenceStatsMatrix, analysisState);

        systemState.sequence = sequenceState;
        systemState.analysis = analysisState;
    }
}
