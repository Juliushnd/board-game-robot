#ifndef BUILDHAT_CONFIG_HPP
#define BUILDHAT_CONFIG_HPP

#include <cmath>

// serial device for the build hat
constexpr char SERIAL_DEVICE[] = "/dev/serial0";

// path to the firmware files on the pi / can be relative to the executable, or absolute
constexpr char FIRMWARE_BASE_PATH[] = "/home/pi/BuildHat/firmware/";

// port for the color sensor (ports translate A-D to 0-3)
constexpr uint8_t PORT_COLOR_SENSOR = 1;

// constants for the color sensor
constexpr int MIN_CALIBRATION_OFFSET = 3;

// ports for the motors
constexpr uint8_t PORT_MOTOR_LEFT = 0;
constexpr uint8_t PORT_MOTOR_RIGHT = 1;

// whether to "invert" the motors, i.e. when it is mounted backwards
constexpr bool INVERT_MOTOR_LEFT = false;
constexpr bool INVERT_MOTOR_RIGHT = false;

// drive calculations:
//  FORWARD_ANGLE describes up to which angle is considered a forward movement
constexpr double FORWARD_ANGLE = 180;
//  FORWARD_SCALE_FACTOR is used to calculate the speed for a given angle, based on the forward angle
constexpr double FORWARD_SCALE_FACTOR = (-1.0 / (FORWARD_ANGLE / 2.0));

// helpful math constants
constexpr double DEG_2_RAD = M_PI / 180.0;
constexpr double RAD_2_DEG = 180.0 / M_PI;

#endif //BUILDHAT_CONFIG_HPP
