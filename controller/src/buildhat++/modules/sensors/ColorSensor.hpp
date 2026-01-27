#ifndef MODULES_SENSORS_COLORSENSOR_HPP
#define MODULES_SENSORS_COLORSENSOR_HPP

#include <cstdint>

#include "config.hpp"

#include "BuildHat.hpp"
#include "ColorTypes.hpp"

/**
 * @brief abstraction for color sensor access
 * remember to calibrate the sensor before use and retrieve the calibration file for later use
 *
 */
class ColorSensor {
public:
    explicit ColorSensor(uint8_t port = PORT_COLOR_SENSOR);
    ~ColorSensor();

    /**
     * @brief store calibration file:
     *    - read color from sensor
     *    - write color +- first standard deviation or +- 5% (whichever is larger) to file
     *    - repeat for all (four) colors
     */
    void calibrate();

    /**
     * @brief parse the calibration file
     *
     * @return std::vector<ColorRange>
     */
    static std::vector<Color::ColorRange> parse_calibration_file();

    /**
     * @brief get the color of the object in front of the sensor
     *
     * @return Color
     */
    Color::Color get_color();

private:
    bool available = false;
    uint8_t port{};

    static std::string get_calibration_file_path();

    BuildHat &buildHat = BuildHat::getInstance();
};

#endif //MODULES_SENSORS_COLORSENSOR_HPP
