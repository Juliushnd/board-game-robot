#ifndef MODULES_SENSORS_COLORTYPES_HPP
#define MODULES_SENSORS_COLORTYPES_HPP

#include <string>
#include <iostream>

// TODO: figure out why they need to be here and not in the cpp file

namespace Color {
    struct Color {
        int hue;
        int sat;
        int val;

        /**
         * Print color to output stream.
         */
        friend std::ostream &operator<<(std::ostream &os, Color const &color) {
            return os << "{hue: " << color.hue << ", sat: " << color.sat << ", val: " << color.val << "}";
        }
    };

    struct ColorRange {
        std::string name;
        Color min;
        Color max;

        /**
         * Checks if the given color is in this range.
         * @param color The color to check.
         * @param only_hue If true, only the hue is checked, not the saturation and value.
         * @return True if the color is in this range.
         */
        bool contains(Color color, bool only_hue = false) const {
            return (color.hue >= min.hue && color.hue <= max.hue) &&
                   (only_hue ||
                    (color.sat >= min.sat && color.sat <= max.sat && color.val >= min.val && color.val <= max.val));
        }

        /**
         * Checks if the given range is equal to this range by comparing the names.
         * @param other
         * @return
         */
        bool operator==(ColorRange const &other) const {
            return name == other.name;
        }

        /**
         * Checks if this range is identified by the given name.
         * @param other_name
         * @return
         */
        bool operator==(std::string const &other_name) const {
            return name == other_name;
        }

        /**
         * Print color range to output stream.
         */
        friend std::ostream &operator<<(std::ostream &os, ColorRange const &range) {
            return os << "ColorRange " << range.name
                      << ": {min: " << range.min.hue << ", " << range.min.sat << ", " << range.min.val
                      << ", max: " << range.max.hue << ", " << range.max.sat << ", " << range.max.val << "}";
        }
    };
}

#endif // MODULES_SENSORS_COLORTYPES_HPP
