/*
 * http_client_proxy.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#pragma once

#include <string>
#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/python.hpp>
#include <boost/make_shared.hpp>

#include "async_client.hpp"
#include "../common/python_helper.hpp"

namespace core
{

class http_client_proxy
{
public:
    http_client_proxy(const std::string& host,
        const std::string& port,
        const std::string& method,
        const std::string& path,
        const std::string& headers,
        const std::string& content,
        int timeout,
        bool usessl,
        bool keep_alive);
    
    virtual ~http_client_proxy();

    void start();

    virtual void callback(const std::string& err, 
        const std::string& headers, 
        const std::string& content);

private:
    async_client_ptr new_async_client;

    boost::asio::io_service io_service;
};

class http_client_proxy_wrapper : public http_client_proxy
{
public:
    http_client_proxy_wrapper(PyObject *self,
        const std::string& host,
        const std::string& port,
        const std::string& method,
        const std::string& path,
        const std::string& headers,
        const std::string& content,
        const int timeout,
        const bool usessl,
        const bool keep_alive);

	~http_client_proxy_wrapper();

private:
    void callback(const std::string& err, 
        const std::string& headers, 
        const std::string& content);

private:
	PyObject *self_;
};   

} // namespace core 
