#ifndef UTILS_UTILITIES_HPP
#define UTILS_UTILITIES_HPP

#include <string>

/**
 * @brief utility functions
 *
 */
struct Utilities {
    /**
     * @brief trim from start (in place)
     * @param s string to trim
     */
    static void ltrim(std::string &s);

    /**
     * @brief trim from end (in place)
     * @param s string to trim
     */
    static void rtrim(std::string &s);

    /**
     * @brief trim from both ends (in place)
     * @param s string to trim
     */
    static void trim(std::string &s);
};


#endif //UTILS_UTILITIES_HPP
