#ifndef MODULES_ACTUATORS_MOTOR_HPP
#define MODULES_ACTUATORS_MOTOR_HPP

#include <cstdint>

#include "BuildHat.hpp"

/**
 * @brief abstraction for motor access
 * 
 */
class Motor {
public:
    /**
     * @brief Construct a new Motor object
     *
     * @param id the id on the build hat 0-3; maps to A-D
     * @param inverted whether the motor direction is inverted (robot construction dependant), default: false
     */
    explicit Motor(uint8_t id, bool inverted = false);

    /**
     * @brief hard brake
     *
     */
    void stop();

    /**
     * @brief set motor to coast
     *
     */
    void coast();

    /**
     * @brief set the motor speed via pwm, -1.0 to 1.0
     *
     * @param speed
     */
    void set_speed(double speed);
    void move_torque(int port, double speed, double currentLimit);

private:
    BuildHat &hat = BuildHat::getInstance();

    uint8_t id;
    bool inverted = false;
};

#endif //MODULES_ACTUATORS_MOTOR_HPP
