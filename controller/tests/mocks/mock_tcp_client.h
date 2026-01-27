#ifndef MOCK_TCP_CLIENT_H
#define MOCK_TCP_CLIENT_H

#include <gmock/gmock.h>

#include "../../src/tcp_client.h"

class MockTCPClient : public TCPClient {
 public:
  MockTCPClient(const std::string& host, const int port)
      : TCPClient(host, port) {};

  MOCK_METHOD(bool, connectToServer, (), (override));
  MOCK_METHOD(bool, sendMessage, (const std::string& message), (override));
  MOCK_METHOD(std::string, receiveMessage, (), (override));
  MOCK_METHOD(void, closeConnection, (), (override));
};

#endif  // MOCK_TCP_CLIENT_H
