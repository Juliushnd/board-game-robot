#include <thread>
#include "Drive.hpp"

#include "config.hpp"

Drive &Drive::getInstance() {
    // since there doesn't need to be only a single instance, we don't need to use a thread-safe singleton implementation
    static Drive instance;
    return instance;
}

Drive::Drive() :
        left{PORT_MOTOR_LEFT, INVERT_MOTOR_LEFT},
        right{PORT_MOTOR_RIGHT, INVERT_MOTOR_RIGHT} {}

Drive::~Drive() {
    coast();
}

void Drive::stop() {
    left.stop();
    right.stop();
}

void Drive::coast() {
    left.coast();
    right.coast();
}

void Drive::set_speed(double s) {
    if (std::abs(s) > 1.0) {
        std::cerr << "Drive: speed must be between -1.0 and 1.0" << std::endl;
        return;
    }
    this->speed = s;
}

void Drive::move_forward(double angle) {
    if (std::abs(angle) > 180.0) {
        std::cerr << "Drive: angle must be between -180.0 and 180.0" << std::endl;
        return;
    }

    // calculate effective speed, which is a function of the angle
    double effective_speed = (1 - this->speed) / (FORWARD_ANGLE / 2.0) * std::abs(angle) + this->speed;

    // limit effective speed to 90% to avoid drawing to much current
    if (effective_speed > .9) {
        effective_speed = .9;
    }

    double adapted_speed;
    if (std::abs(angle) < FORWARD_ANGLE) {
        // if the angle is considered "forward", use regular calculation for turning
        adapted_speed = (FORWARD_SCALE_FACTOR * std::abs(angle) + 1) * effective_speed;
    } else {
        // otherwise, turn in place
        adapted_speed = -effective_speed;
    }

    if (angle < 0) {
        // turn left
        left.set_speed(adapted_speed);
        right.set_speed(effective_speed);
    } else {
        // turn right
        left.set_speed(effective_speed);
        right.set_speed(adapted_speed);
    }
}

void Drive::move_backward() {
    left.set_speed(-this->speed);
    right.set_speed(-this->speed);
}

void Drive::turn(bool _left) {
    // save previous speed
    double prev_speed = this->speed;

    double angle = (_left ? -180 : 180);

    static const int wind_up_time_ms = 1000;
    static const int step_size_ms = 5;
    static const double start_speed = 0.2;
    static const double target_speed = 0.9;

    // time to turn - about 1.5 seconds, this is what our robot took for a 90-degree turn
    static const int turn_time_ms = 1433;

    // set both motors to coast
    coast();
    std::this_thread::sleep_for(std::chrono::milliseconds{200});

    // wind up motors
    WindUp(start_speed,
           target_speed,
           wind_up_time_ms,
           wind_up_time_ms / step_size_ms);

    // take start time
    auto start = std::chrono::system_clock::now();
    auto lap = std::chrono::system_clock::now();

    while (std::chrono::duration_cast<std::chrono::milliseconds>(lap - start).count() < turn_time_ms) {
        lap = std::chrono::system_clock::now();
        // drive forward
        move_forward(angle);
        std::this_thread::sleep_for(std::chrono::milliseconds{static_cast<int>(step_size_ms / 2.0)});
    }

    // restore speed
    this->speed = prev_speed;
}

void Drive::turn_left() {
    turn(true);
}

void Drive::turn_right() {
    turn(false);
}

void Drive::WindUp(double start_speed, double target_speed, int time_ms, int steps) {
    std::thread([start_speed, target_speed, time_ms, steps]() {
        Drive &drive = Drive::getInstance();
        drive.set_speed(start_speed);
        uint16_t wind_sleep = time_ms / steps;
        double stepSize = (target_speed - start_speed) / ((double) steps);
        for (int step = 0; step <= steps; ++step) {
            double value = start_speed + (step * stepSize);
            drive.set_speed(value);
            std::this_thread::sleep_for(std::chrono::milliseconds(wind_sleep));
        }
    }).detach();
}

void Drive::WindDown(double start_speed, double target_speed, int time_ms, int steps) {
    std::thread([start_speed, target_speed, time_ms, steps]() {
        Drive &drive = Drive::getInstance();
        drive.set_speed(start_speed);
        uint16_t wind_sleep = time_ms / steps;
        double stepSize = (target_speed - start_speed) / ((double) steps);
        for (int step = 0; step <= steps; ++step) {
            double value = target_speed - (step * stepSize);
            std::this_thread::sleep_for(std::chrono::milliseconds(wind_sleep));
            drive.set_speed(value);
        }
    }).detach();
}
