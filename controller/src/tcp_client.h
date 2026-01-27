//
// Created by adam on 21.05.25.
//
#include <arpa/inet.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

#include <cstring>
#include <memory>
#include <string>

#ifndef TCP_CLIENT_H_
#define TCP_CLIENT_H_

constexpr int PORT = 8080;
constexpr int BUFFER_SIZE = 1024;

class TCPClient {
 public:
  TCPClient(const std::string& serverIP, int port);
  virtual ~TCPClient() = default;

  virtual bool connectToServer();
  virtual bool sendMessage(const std::string& message);
  virtual std::string receiveMessage();
  virtual void closeConnection();

 private:
  std::string serverIP;
  int port;
  int sockfd;
  bool connected;
};

#endif  //  TCP_CLIENT_H_
