#ifndef FUNCTIONS_DRIVE_HPP
#define FUNCTIONS_DRIVE_HPP

#include "modules/actuators/Motor.hpp"

/**
 * @brief abstraction for drive access
 *
 */
class Drive {
private:
    /**
     * @brief Construct a new Drive object
     *
     */
    Drive();

    Motor left;
    Motor right;

    // the internal speed for the whole drive
    double speed = 1.0;

    void turn(bool left);

    static void
    WindUp(double wind_start_speed, double wind_target_speed, int wind_time_milliseconds, int wind_step_count);

    static void
    WindDown(double start_speed, double target_speed, int time_ms, int steps);

public:
    static Drive &getInstance();

    ~Drive();

    /**
     * @brief set the drive speed, -1.0 to 1.0
     *
     * @param speed
     */
    void set_speed(double speed);

    /**
     * @brief hard brake
     *
     */
    void stop();

    /**
    * @brief set drive to coast
    *
    */
    void coast();

    /**
     * @brief drive the robot forward along a given angle
     *
     * @param angle the angle in degrees
     */
    void move_forward(double angle);

    /**
     * @brief drive the robot backward
     */
    void move_backward();

    /**
     * @brief turn left
     */
    void turn_left();

    /**
     * @brief turn right
     */
    void turn_right();
};

#endif //FUNCTIONS_DRIVE_HPP
