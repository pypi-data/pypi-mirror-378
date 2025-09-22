#pragma once
#include "common.h"
#include "kmc/state.h"
#include "analysis/utils.h"

namespace analysis
{

    struct AnalysisResults
    {
        AnalysisState analysisState;
        SequenceState sequenceState;
    };

    void analyzeChainLengthDist(Eigen::MatrixXd &sequenceStatsMatrix, const std::vector<Unit> &units, AnalysisState &state)
    {
        if (sequenceStatsMatrix.rows() == 0 || sequenceStatsMatrix.cols() == 0)
            return;

        size_t numMonomers = registry::getNumOf(SpeciesType::MONOMER);

        Eigen::MatrixXd monomerCountDist = sequenceStatsMatrix.leftCols(numMonomers);
        Eigen::VectorXd nAvgChainLengthDist = monomerCountDist.colwise().mean();

        state.nAvgChainLength = nAvgChainLengthDist.mean();

        console::debug("nAvgChainLength: " + std::to_string(state.nAvgChainLength));
        if (state.nAvgChainLength != 0.0)
        {
            state.wAvgChainLength = nAvgChainLengthDist.array().square().mean() / state.nAvgChainLength;
            state.chainLengthDispersity = state.wAvgChainLength / state.nAvgChainLength;
        }
        console::debug("wAvgChainLength: " + std::to_string(state.wAvgChainLength));

        // Weight by molecular weight
        Eigen::MatrixXd weightedMatrix = monomerCountDist;
        auto monomerIDs = registry::getIDsOf(SpeciesType::MONOMER);
        for (auto &id : monomerIDs)
        {
            size_t monIdx = registry::getIndex(id, SpeciesType::MONOMER);
            weightedMatrix.col(monIdx) *= units[id].FW;
        }
        Eigen::VectorXd nAvgMolecularWeightDist = weightedMatrix.rowwise().sum();

        state.nAvgMolecularWeight = nAvgMolecularWeightDist.mean();
        if (state.nAvgMolecularWeight != 0.0)
        {
            console::debug("nAvgMolecularWeight: " + std::to_string(state.nAvgMolecularWeight));
            // console::debug(std::to_string(state.nAvgMolecularWeight));
            state.wAvgMolecularWeight = nAvgMolecularWeightDist.array().square().mean() / state.nAvgMolecularWeight;
            state.molecularWeightDispersity = state.wAvgMolecularWeight / state.nAvgMolecularWeight;
        }
    }

    void analyzeSequenceLengthDist(Eigen::MatrixXd &sequenceStatsMatrix, AnalysisState &state)
    {
        size_t numMetrics = SequenceStats::numMetrics();

        auto monomerIDs = registry::getIDsOf(SpeciesType::MONOMER);
        for (const auto &id : monomerIDs)
        {
            size_t monIdx = registry::getIndex(id, SpeciesType::MONOMER);
            size_t colBase = monIdx * numMetrics;

            if (sequenceStatsMatrix.rows() == 0 || sequenceStatsMatrix.cols() <= colBase + 2)
            {
                state.nAvgSequenceLengths[monIdx] = 0;
                state.wAvgSequenceLengths[monIdx] = 0;
                state.sequenceLengthDispersities[monIdx] = 0;
                // console::warning("No sequence data found.");
                continue;
            }

            auto monomerCount = sequenceStatsMatrix.col(colBase).sum();
            auto sequenceCount = sequenceStatsMatrix.col(colBase + 1).sum();
            auto sequenceLengths2 = sequenceStatsMatrix.col(colBase + 2).sum();

            if (sequenceCount > 0 && monomerCount > 0)
            {
                state.nAvgSequenceLengths[monIdx] = monomerCount / sequenceCount;
                state.wAvgSequenceLengths[monIdx] = sequenceLengths2 / monomerCount;
                state.sequenceLengthDispersities[monIdx] = state.wAvgSequenceLengths[monIdx] / state.nAvgSequenceLengths[monIdx];
            }
            else
            {
                state.nAvgSequenceLengths[monIdx] = 0;
                state.wAvgSequenceLengths[monIdx] = 0;
                state.sequenceLengthDispersities[monIdx] = 0;
            }
        }
    }

    void analyze(const SpeciesSet &speciesSet, SystemState &systemState)
    {
        auto sequenceData = speciesSet.getRawSequenceData();

        auto sequenceSummary = analysis::calculateSequenceSummary(sequenceData);
        auto sequenceStatsMatrix = analysis::calculateSequenceStatsMatrix(sequenceSummary.sequenceStatsTensor);

        SequenceState sequenceState = SequenceState{systemState.kmc, sequenceSummary.avgPositionalStats};

        AnalysisState analysisState;
        analysis::analyzeChainLengthDist(sequenceStatsMatrix, speciesSet.getUnits(), analysisState);
        analysis::analyzeSequenceLengthDist(sequenceStatsMatrix, analysisState);

        systemState.sequence = sequenceState;
        systemState.analysis = analysisState;
    }
}
