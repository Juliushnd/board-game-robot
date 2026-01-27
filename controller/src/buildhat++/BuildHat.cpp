#include "BuildHat.hpp"

#include "utils/Utilities.hpp"
#include "config.hpp"

#include <thread>
#include <iostream>
#include <array>




#include <string>
#include <sstream>
#include <vector>
#include <utility>


/* singleton implementation */

BuildHat *BuildHat::instance = nullptr;
std::mutex BuildHat::instance_mutex_;
std::recursive_mutex BuildHat::serial_access_mutex_;

BuildHat &BuildHat::getInstance() {
    // Double-Checked Locking optimization
    if (instance == nullptr) {
        std::lock_guard<std::mutex> lock(instance_mutex_);
        if (instance == nullptr) {
            instance = new BuildHat();
        }
    }
    return *instance;
}

/********************* implementation *********************/

BuildHat::BuildHat() :
        serial_stream{SERIAL_DEVICE}, state{HatState::OTHER}, ready{false} {
    ready = true;

    if (!serial_stream.IsOpen() || update_hat_state() != 0) {
        ready = false;
        throw std::runtime_error("BuildHat: error initialising serial");
    }

    // turn echo off
    if (state == HatState::BOOTLOADER) {
        std::cout << "BuildHat: bootloader detected, flashing firmware..." << std::endl;
        if (load_firmware() != 0 || update_hat_state() != 0 && state != HatState::FIRMWARE) {
            ready = false;
            throw std::runtime_error("BuildHat: error loading firmware");
        }
    } else if (state == HatState::OTHER) {
        ready = false;
        throw std::runtime_error("BuildHat: unknown state");
    }

    // if we rebooted, turn echo off again
    serial_write_line("echo 0", false);

    // check voltage reported by BuildHat
    std::cout << "Voltage at buildhat: " << serial_write_read("vin", false) << std::endl;

    // clear any faults
    serial_write_line("clear_faults", false);

    ready = true;
}

BuildHat::~BuildHat() {
    serial_stream.Close();
}

int BuildHat::update_hat_state() {
    // constants used for serial communication parsing
    const std::string FIRMWARE = "Firmware version: ";
    const std::string BOOTLOADER = "BuildHAT bootloader version";

    int inc_data = 0;
    while (true) {
        std::string line = serial_write_read("version", false);

        if (line.find(FIRMWARE) != std::string::npos) {
            std::cout << "BuildHAT has firmware: " << line << std::endl;
            state = HatState::FIRMWARE;
            break;
        } else if (line.find(BOOTLOADER) != std::string::npos) {
            state = HatState::BOOTLOADER;
            break;
        } else {
            inc_data++;
            std::cerr << "Error: unknown data received from BuildHAT: " << line << std::endl;
            if (inc_data > 20) {
                return -1;
            } else {
                // got data we don't understand, try again
                std::this_thread::sleep_for(std::chrono::milliseconds(200));
                continue;
            }
        }
    }

    return 0;
}

int BuildHat::load_firmware() {
    // get the path to the data directory
    std::string path = FIRMWARE_BASE_PATH;

    // get the paths to the firmware, signature, and version files
    std::string path_firm = path + "firmware.bin";
    std::string path_sig = path + "signature.bin";
    std::string path_ver = path + "version";

    // read the version number from the version file
    std::ifstream version_file(path_ver);
    uint32_t version = 0;
    if (version_file.is_open()) {
        version_file >> version;
        version_file.close();
    } else {
        std::cerr << "Failed to open version file: " << path_ver << std::endl;
        return 1;
    }

    // read the firmware file into a std::string
    std::ifstream firm_file(path_firm, std::ios::binary);
    if (!firm_file) {
        std::cerr << "Failed to open firmware file: " << path_firm << std::endl;
        return 1;
    }
    std::string firmware((std::istreambuf_iterator<char>(firm_file)), std::istreambuf_iterator<char>());
    firm_file.close();

    // read the signature file into a std::string
    std::ifstream sig_file(path_sig, std::ios::binary);
    if (!sig_file) {
        std::cerr << "Failed to open signature file: " << path_sig << std::endl;
        return 1;
    }
    std::string signature((std::istreambuf_iterator<char>(sig_file)), std::istreambuf_iterator<char>());
    sig_file.close();

    // clear write buffer
    serial_write_line();
    serial_write_line();

    serial_write_line("version");
    if (serial_stream.IsDataAvailable()) serial_read_line(true);

    // write firmware and signature to serial:
    // first, send clear
    serial_write_line("clear");

    // initiate firmware loading using load command with length and checksum as arguments
    std::string firmware_size = std::to_string(firmware.size());
    std::string firmware_checksum = std::to_string(checksum(firmware));
    std::string load_command = "load " + firmware_size + " " + firmware_checksum;
    serial_write_line(load_command);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    // write firmware bytes to serial
    std::string start_of_frame = "\x02";
    std::string end_of_frame = "\x03";
    std::string firmware_payload = start_of_frame + firmware + end_of_frame;
    std::string signature_payload = start_of_frame + signature + end_of_frame;

    serial_write_line(firmware_payload, true, "--- firmware payload ---");
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    // write signature bytes to serial
    std::string signature_command = "signature " + std::to_string(signature.size());
    serial_write_line(signature_command);
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    // now send signature bytes
    serial_write_line(signature_payload, true, "--- signature payload ---");

    // send reboot command
    serial_write_line("reboot");

    // flush serial buffer, tell user
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    while (serial_stream.IsDataAvailable()) {
        serial_read_line(true);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    std::cout << "Flashed firmware, rebooting..." << std::endl;

    // actually wait for reboot
    std::this_thread::sleep_for(std::chrono::milliseconds(3500));

    // read post reboot data
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    while (serial_stream.IsDataAvailable()) {
        serial_read_line(true);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    std::cout << "Firmware flashed successfully" << std::endl;

    return 0;
}

uint32_t BuildHat::checksum(std::string const &data) {
    uint32_t u = 1;
    for (char c: data) {
        if ((u & 0x80000000) != 0) {
            u = (u << 1) ^ 0x1D872B41; // CRC32 polynomial
        } else {
            u = u << 1;
        }
        u = (u ^ static_cast<uint8_t>(c)) & 0xFFFFFFFF;
    }
    return u;
}

/********* public interface *********/

void BuildHat::serial_write_line(std::string const &data, bool log, std::string const &alt) {
    if (!ready) {
        std::cerr << "Error: BuildHat not ready" << std::endl;
        return;
    }

    {
        std::lock_guard<std::recursive_mutex> lock(serial_access_mutex_);

        serial_stream << data << '\r' << std::flush;
        serial_stream.DrainWriteBuffer();
    }

    if (log) std::cout << "> " << (alt.empty() ? data : alt) << std::endl;
}

std::string BuildHat::serial_read_line(bool log, std::string const &alt) {
    if (!ready) {
        std::cerr << "Error: BuildHat not ready" << std::endl;
        return {};
    }

    std::lock_guard<std::recursive_mutex> lock(serial_access_mutex_);

    std::string line;
    while (line.empty() && std::getline(serial_stream, line)) {
        Utilities::trim(line);
        if (log) std::cout << (alt.empty() ? line : alt) << std::endl;
    }
    return line;
}

void BuildHat::read2(){
        if(!ready){
            std::cerr << "Error: BuildHat not ready" << std::endl;
            return;
        }
        
        std::string s;
        while(serial_stream.IsDataAvailable()){
                if(!ready) continue;
                
                std::lock_guard<std::recursive_mutex> lock(serial_access_mutex_);
                //serial_write_line("")
;                if(std::getline(serial_stream, s)){
                       // std::cout << s << std::endl;
                }
        }
}

// index is the position of numbers after the doublepoint
std::pair<int, int> BuildHat::getIntFromStr(std::string& input, int index) {
    std::string::size_type colon_pos = input.find(':');
    if (colon_pos == std::string::npos) {
        return {-1, -1};
    }

    std::string::size_type pPos = input.find('P');
    std::string::size_type cPos = input.find('C');

    if (pPos == std::string::npos || cPos == std::string::npos || pPos >= cPos) {
        return {-1, -1};
    }

  int prefix_number = 0;
  
  try {
    prefix_number = std::stoi(input.substr(pPos + 1, cPos - pPos - 1));

  }
  catch (const std::invalid_argument& e) {
    std::cerr << "Invalid Argument: " << input << "'\n";
    return {-1, -1};
  }

    // extract numbers after colon
    std::string numbers_part = input.substr(colon_pos + 1);
    std::istringstream iss(numbers_part);
    std::vector<int> numbers;
    int number;

    while (iss >> number) {
        numbers.push_back(number);
    }

    if (index < 0 || index >= static_cast<int>(numbers.size())) {
        return {prefix_number, -1};
    }

    //return port number and number at index after doublepoint
    return {prefix_number, numbers[index]};
}

std::array<std::string, 4> BuildHat::readFourLines(){
    std::array<std::string, 4> s;

    if(!ready){
            std::cerr << "Error: BuildHat not ready" << std::endl;
            return s;
    }

    int num = 0;

    while(serial_stream.IsDataAvailable() && num < 4) {
        if(!ready) continue;
        std::lock_guard<std::recursive_mutex> lock(serial_access_mutex_);
        if(std::getline(serial_stream, s[num])){
        }
    }
    return s;

}

std::string BuildHat::serial_write_read(std::string const &data, bool log, std::string const &alt) {
    std::lock_guard<std::recursive_mutex> lock(serial_access_mutex_);
    serial_write_line(data, log, alt);
    return serial_read_line(log, alt);
}
// gets as input a string from the serial interface
// returns the port of the input, and the speed of the motor
// -1 means: error/not found
std::pair<int, int> BuildHat::isMotorMoving(int port) {
    if (!ready) {
        std::cerr << "BuildHat not ready" << std::endl;
        return {-1, -1};
    }

    std::string curr = "";
    int count = 0;

    while(true) {
        curr =  serial_write_read("port "+ std::to_string(port) + "; combi 0 1 0 2 0 3 0; selonce 0", false);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));

            if (!curr.empty()) {
                std::pair<int, int> num2 = getIntFromStr(curr, 0);

                if (count == 50) break;
                count++;

                if (num2.first == port) return num2;
                curr = "";
            }
    }

    return {-1,-1};
}

// gets as input a string from the serial interface
// returns the port of the input, and a value at the index:
// index 0: speed, index 1: absolute degree, index 2 : relative degree
// -1 means: error/not found
std::pair<int, int> BuildHat::getValueOfPort(int port, int index) {
    if (!ready) {
        std::cerr << "BuildHat not ready" << std::endl;
        return {-1,-1};
    }

    std::string curr = "";

    int count = 0;

    while(true) {
        std::lock_guard<std::recursive_mutex> lock(serial_access_mutex_);
        serial_write_line("port "+ std::to_string(port) + "; combi 0 1 0 2 0 3 0; selonce 0", false);
        std::this_thread::sleep_for(std::chrono::milliseconds(20));

        if (std::getline(serial_stream, curr)) {
            if (!curr.empty()) {
                std::pair<int, int> num2 = getIntFromStr(curr, index);

                if (count == 50) break;
                count++;

                if (num2.first == port) return num2;
                curr = "";
            }
        }
    }

    return {-1,-1};
}

