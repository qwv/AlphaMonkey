/*
 * http_client_proxy.cpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#include "http_client_proxy.hpp"

namespace core
{

http_client_proxy::http_client_proxy() {}

void http_client_proxy::__init__(const std::string& host,
                                 const std::string& port,
                                 const std::string& method,
                                 const std::string& path,
                                 const std::string& headers,
                                 const std::string& content,
                                 int timeout,
                                 bool usessl,
                                 bool keep_alive)
{
    this->host = host;
    this->port = port;
    this->method = method;
    this->path = path;
    this->headers = headers;
    this->content = content;
    this->timeout = timeout;
    this->usessl = usessl;
    this->keep_alive = keep_alive;

    // port headers usessl not support yet
    async_client c(io_service, this->host, this->path, this->method, this->content,
                   this->timeout, this->keep_alive,
                   std::bind(&http_client_proxy::callback, this, std::placeholders::_1,
                                                                 std::placeholders::_2,
                                                                 std::placeholders::_3));
}

void http_client_proxy::start()
{
    io_service.run();
}

} // namespace core
