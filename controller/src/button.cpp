//
// Created by adam on 21/06/25.
//

#include "button.h"

#include <string>

void Button::init() {
  if (initialized) return;  // Already initialized

  chip = gpiod_chip_open_by_name(chipName.c_str());
  if (!chip) throw std::runtime_error("Failed to open GPIO chip");

  line = gpiod_chip_get_line(chip, lineNum);
  if (!line) {
    gpiod_chip_close(chip);
    throw std::runtime_error("Failed to get GPIO line");
  }

  if (gpiod_line_request_input_flags(
          line, "limit-switch", GPIOD_LINE_REQUEST_FLAG_BIAS_PULL_UP) < 0) {
    gpiod_chip_close(chip);
    throw std::runtime_error("Failed to request line as input with pull-up");
  }

  initialized = true;
}

Button::Button(const std::string& chipName, unsigned int lineNum)
    : chipName(chipName), lineNum(lineNum), chip(nullptr), line(nullptr) {}

Button::~Button() {
  if (line) gpiod_line_release(line);
  if (chip) gpiod_chip_close(chip);
}

bool Button::isPressed() const {
  if (!initialized) throw std::runtime_error("Button not initialized");
  int value = gpiod_line_get_value(line);
  if (value < 0) throw std::runtime_error("Failed to read GPIO value");
  return value == 0;  // LOW = pressed (with pull-up)
}
