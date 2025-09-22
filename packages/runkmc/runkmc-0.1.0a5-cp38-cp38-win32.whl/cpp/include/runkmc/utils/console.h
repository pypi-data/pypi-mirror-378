#pragma once
#include <vector>
#include <string>
#include <iostream>
#include <iomanip>

#define BLK "\x1b[0;30m"
#define RED "\x1b[0;31m"
#define GRN "\x1b[0;32m"
#define YLW "\x1b[0;33m"
#define BLU "\x1b[0;34m"
#define MAG "\x1b[0;35m"
#define CYN "\x1b[0;36m"
#define WHT "\x1b[0;37m"
#define NRM "\x1b[0m"
#define UBLU "\x1b[4;34m"

namespace console
{
    static void debug_rxn(std::string message)
    {
        std::cout << MAG << "[ DEBUG ] : ";
        std::cout << message << NRM << std::endl;
    }

    static void debug(std::string message)
    {
        std::cout << BLU << "[ DEBUG ] : ";
        std::cout << message << NRM << std::endl;
    }

    static void debug_msg(std::string message)
    {
        std::cout << UBLU << "[ DEBUG ] : ";
        std::cout << message << NRM << std::endl;
    }

    template <typename T>
    static void debug_value(std::string name, T variable)
    {
        std::cout << BLU << "[ DEBUG ] : ";
        std::cout << name << ": " << variable << NRM << std::endl;
    }

    static void log(std::string message)
    {
        std::cout << GRN << "[ LOG ] : ";
        std::cout << message << NRM << std::endl;
    }
    static void warning(std::string message)
    {
        std::cout << YLW << "[ WARNING ] : ";
        std::cout << message << NRM << std::endl;
    }
    static void input_warning(std::string message)
    {
        std::cout << YLW << "[ INPUT WARNING ] : ";
        std::cout << message << NRM << std::endl;
    }
    static void error(std::string message)
    {
        std::cout << RED << "[ ERROR ] : ";
        std::cout << message << NRM << std::endl;
        exit(EXIT_FAILURE);
    }
    static void input_error(std::string message)
    {
        std::cout << RED << "[ INPUT ERROR ] : ";
        std::cout << message << NRM << std::endl;
        exit(EXIT_FAILURE);
    }
};

namespace print
{
    template <typename T1, typename A1>
    static void printWithIndex(std::vector<T1, A1> &toPrint)
    {
        for (int i = 0; i < toPrint.size(); i++)
        {
            std::cout << "(" << i << ")=" << toPrint[i] << " ";
        }
        std::cout << std::endl;
    }

    template <typename T1, typename A1, typename T2, typename A2>
    static void printWithIndex(std::vector<T1, A1> &toPrint, std::vector<T2, A2> &index)
    {
        assert(toPrint.size() == index.size());
        for (int i = 0; i < toPrint.size(); i++)
        {
            std::cout << "(" << index[i] << ")=" << toPrint[i] << " ";
        }
        std::cout << std::endl;
    }
};

namespace table
{
    const std::string columnString = " | ";

    void setPrecision(const int &precision)
    {
        std::cout << std::fixed << std::setprecision(precision);
    }

    template <typename T>
    void printTableElement(T t, const size_t &padding)
    {
        std::cout << std::left << std::setw(padding) << t << columnString;
    }

    template <typename T>
    void printTableElement(T t, const size_t &padding, const std::string &colString)
    {
        std::cout << std::left << std::setw(padding) << t << colString;
    }
}
