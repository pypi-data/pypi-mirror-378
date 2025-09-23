#pragma once
#include "common.h"
#include "species/species_set.h"
#include "outputs/paths.h"

namespace output
{

    void writePolymers(const SimulationPaths &paths, const SpeciesSet &speciesSet, const int &iteration)
    {
        std::string filepath = paths.polymerFile(iteration).string();

        std::ofstream output;
        output.open(filepath.c_str(), std::ios::out);

        const auto polymers = speciesSet.getPolymers();
        for (const auto &polymer : polymers)
        {
            if (polymer->isCompressed())
                continue;
            output << polymer->getSequenceString() << std::endl;
        }

        output.close();
    }
}
