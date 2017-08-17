/*
 * http_client_proxy.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#pragma once

#include <string>
#include <boost/asio.hpp>

#include "async_client.hpp"

namespace core
{

class http_client_proxy
{
public:
    http_client_proxy();

    void __init__(const std::string& host,
                  const std::string& port,
                  const std::string& method,
                  const std::string& path,
                  const std::string& headers,
                  const std::string& content,
                  int timeout,
                  bool usessl,
                  bool keep_alive);

    void start();

private:
    std::string host;
    std::string port;
    std::string method;
    std::string path;
    std::string headers;
    std::string content;

    int timeout;
    bool usessl;
    bool keep_alive;

    boost::asio::io_service io_service;
};

} // namespace core 
