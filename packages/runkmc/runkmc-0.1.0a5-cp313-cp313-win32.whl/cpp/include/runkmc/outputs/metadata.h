
#pragma once
#include <yaml-cpp/yaml.h>

#include "common.h"
#include "kmc/kmc.h"

namespace output
{
    // Forward declarations of helper functions
    namespace detail
    {
        YAML::Node writeRunInfo(const KMC &model);
        YAML::Node writeParameters(const KMC &model);

        YAML::Node writeReaction(const Reaction &reaction);
        YAML::Node writeRateConstant(const RateConstant &rateConstant);
        YAML::Node writeReactionSet(const ReactionSet &reactionSet);

        YAML::Node writeUnit(const Unit &unit);
        YAML::Node writePolymerType(const PolymerType &polyType);
        YAML::Node writePolymerGroup(const PolymerTypeGroup &polyGroup);
        YAML::Node writeSpeciesSet(const SpeciesSet &speciesSet);
    }

    void writeMetadata(const KMC &model)
    {

        auto paths = model.getPaths();

        YAML::Node metadata;

        metadata["run_info"] = detail::writeRunInfo(model);

        metadata["parameters"] = detail::writeParameters(model);

        metadata["species"] = detail::writeSpeciesSet(model.getSpeciesSet());

        metadata["reactions"] = detail::writeReactionSet(model.getReactionSet());

        std::ofstream file(paths.metadataFile());
        file << metadata;
    }

    // Helper function implementations
    namespace detail
    {

        // ----------- Write simulation info -----------

        YAML::Node writeRunInfo(const KMC &model)
        {
            YAML::Node node;
            node["version"] = RUNKMC_VERSION;

            auto now = std::chrono::system_clock::now();
            node["timestamp"] = std::chrono::system_clock::to_time_t(now);
            node["unix_timestamp"] = std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count();

            return node;
        }

        // ----------- Write simulation parameters -----------

        YAML::Node writeParameters(const KMC &model)
        {
            YAML::Node node;
            node["num_particles"] = model.getOptions().numParticles;
            node["termination_time"] = model.getOptions().terminationTime;
            node["analysis_time"] = model.getOptions().analysisTime;
            node["report_sequences"] = model.getConfig().reportSequences;
            node["report_polymers"] = model.getConfig().reportPolymers;
            return node;
        }

        // ----------- Write species information -----------
        YAML::Node writeUnit(const Unit &unit)
        {
            YAML::Node node;
            node["id"] = std::to_string(unit.ID);
            node["name"] = unit.name;
            node["type"] = unit.type;

            node["C0"] = unit.C0;
            node["FW"] = unit.FW;
            node["efficiency"] = unit.efficiency;

            node["init_count"] = unit.getInitialCount();

            return node;
        }

        YAML::Node writePolymerType(const PolymerType &polyType)
        {
            YAML::Node node;
            node["name"] = polyType.name;
            node["end_group"] = polyType.getEndGroup();
            return node;
        }

        YAML::Node writePolymerGroup(const PolymerTypeGroup &polyGroup)
        {
            YAML::Node node;
            node["name"] = polyGroup.name;

            YAML::Node polyTypes;
            std::vector<std::string> polyTypeNames;
            for (auto &polyTypePtr : polyGroup.getPolymerTypes())
                polyTypeNames.push_back(polyTypePtr->name);

            node["polymer_types"] = polyTypeNames;

            return node;
        }

        YAML::Node writeSpeciesSet(const SpeciesSet &speciesSet)
        {
            YAML::Node node;

            YAML::Node units;
            auto unitIDs = registry::getAllUnitIDs();
            for (auto &id : unitIDs)
            {
                YAML::Node unit = writeUnit(speciesSet.getUnits()[id]);
                units.push_back(unit);
            }
            node["units"] = units;

            YAML::Node polymers;
            for (const auto &polyGroup : speciesSet.getPolymerGroupPtrs())
            {
                YAML::Node polyGroupNode = writePolymerGroup(*polyGroup);
                polymers.push_back(polyGroupNode);
            }
            node["polymers"] = polymers;

            return node;
        }

        // ----------- Write reaction information -----------

        YAML::Node writeReaction(const Reaction &reaction)
        {
            YAML::Node node;
            node["type"] = reaction.getType();
            node["rate_constant"] = reaction.rateConstant.name;

            std::vector<std::string> reactantNames = reaction.getReactantNames();
            node["reactants"] = reactantNames;

            std::vector<std::string> productNames = reaction.getProductNames();
            node["products"] = productNames;

            return node;
        }

        YAML::Node writeRateConstant(const RateConstant &rateConstant)
        {
            YAML::Node node;
            node["name"] = rateConstant.name;
            node["value"] = rateConstant.value;
            return node;
        }

        YAML::Node writeReactionSet(const ReactionSet &reactionSet)
        {
            YAML::Node node;

            node["num_reactions"] = reactionSet.getNumReactions();

            YAML::Node reactions;
            YAML::Node rateConstants;
            for (int i = 0; i < reactionSet.getNumReactions(); ++i)
            {
                auto reaction = reactionSet.getReaction(i);
                YAML::Node reactionNode = writeReaction(*reaction);
                reactions.push_back(reactionNode);
            }
            for (const auto &rateConstant : reactionSet.getRateConstants())
                rateConstants.push_back(writeRateConstant(rateConstant));

            node["reactions"] = reactions;
            node["rate_constants"] = rateConstants;

            return node;
        }
    }
}