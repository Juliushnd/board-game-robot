#ifndef BUILDHAT_HPP
#define BUILDHAT_HPP

#include <mutex>
#include <string>
#include <fstream>
#include <iostream>

#include <libserial/SerialPort.h>
#include <libserial/SerialStream.h>

using namespace LibSerial;

/**
 * @brief abstraction over the serial communication interface
 * providing both read and write, as well as an internal firmware flashing service
 * 
 */
class BuildHat {
public:
    /**
     * @brief Get the Instance object
     *
     * @return BuildHat&
     */
    static BuildHat &getInstance();

    // Delete the copy constructor and copy assignment operator
    BuildHat(BuildHat const &) = delete;
    BuildHat &operator=(BuildHat const &) = delete;

    /**
     * @brief Write a line to the serial interface
     *
     * @param data the data to write
     * @param log whether or not to log the data
     * @param alt an alternative string to log
     */
    void serial_write_line(std::string const &data = "", bool log = true, std::string const &alt = "");

    /**
     * @brief Read a line from the serial interface
     * This will block until a line is read
     *
     * @param log whether or not to log the data
     * @param alt an alternative string to log
     * @return std::string the data read
     */
    std::string serial_read_line(bool log = false, std::string const &alt = "");
    void read2();
    std::array<std::string, 4> readFourLines();
    std::pair<int, int> isMotorMoving(int port);
    std::pair<int, int> getValueOfPort(int port, int index);
    std::pair<int, int> getIntFromStr(std::string& input, int index);

    /**
     * @brief Write and read a line from the serial interface
     * Reads the immediate response to the write, in one atomic operation
     * Will block until a line is read
     *
     * @param data the data to write
     * @param log whether or not to log the data
     * @param alt an alternative string to log
     * @return std::string the data read
     */
    std::string serial_write_read(std::string const &data, bool log = false, std::string const &alt = "");

private:
    BuildHat();
    ~BuildHat();

    /**
     * @brief HatState, in terms of software flashed
     *
     * OTHER: unknown state
     * FIRMWARE: firmware flashed
     * BOOTLOADER: bootloader flashed
     *
     */
    enum class HatState : u_int8_t {
        OTHER, FIRMWARE, BOOTLOADER
    };

    // flash state of the hat
    HatState state;

    // serial interface handle
    SerialStream serial_stream;

    // whether the hat is ready for use
    bool ready;

    /**
     * @brief Update the hat state by querying the serial interface
     *
     * @return 0 on successful update, else != 0
     */
    int update_hat_state();

    /**
     * @brief flashes the firmware onto the build hat
     *
     * @return 0 on successful flash, else != 0
     */
    int load_firmware();

    /**
     * @brief calculates a checksum of the give data, required for firmware flashing
     *
     * @param data the data to calculate the checksum of
     * @return uint32_t the checksum
     */
    static uint32_t checksum(std::string const &data);

    /**
     * @brief singleton instance
     *
     */
    static BuildHat *instance;

    /**
     * @brief locks access to mutex creation
     *
     */
    static std::mutex instance_mutex_;

    /**
     * @brief locks access to serial interface - recursive mutex to allow chained calls internally
     *
     */
    static std::recursive_mutex serial_access_mutex_;
};

#endif //BUILDHAT_HPP
