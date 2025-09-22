#pragma once
#include "common.h"
#include "species/species_set.h"

namespace output
{
    void reportPolymers(const SpeciesSet &speciesSet, std::string outputDir, int iteration)
    {
        std::string filepath = outputDir + "/poly_" + std::to_string(iteration) + ".dat";

        std::ofstream output;
        output.open(filepath.c_str(), std::ios::out);

        const auto polymers = speciesSet.getPolymers();
        for (const auto &polymer : polymers)
        {
            for (size_t j = 0; j < polymer->getDegreeOfPolymerization(); ++j)
                output << +polymer->repeatUnitAtPosition(j) << " ";
            output << std::endl;
        }

        output.close();
    }
}
