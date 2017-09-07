/*
 * async_client.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#pragma once

#include <string>
#include <istream>
#include <ostream>
#include <boost/bind.hpp>
#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/function.hpp>
#include <boost/enable_shared_from_this.hpp>

#include "socket_wrapper.hpp"

namespace core
{

typedef boost::function<void(const std::string&, const std::string&, const std::string&)> http_callback;

class async_client : public boost::enable_shared_from_this<async_client>
{

public:
    async_client(boost::asio::io_service& io_service,
                 const int timeout,
                 const http_callback& callback);

    async_client(boost::asio::io_service& io_service,
                 boost::asio::ssl::context& ctx,
                 const int timeout,
                 const http_callback& callback);

    void start(const std::string& server, const std::string& path,
               const std::string& method, const std::string& content,
               bool keep_alive);

    void stop();

private:
    void handle_resolve(const boost::system::error_code& err,
                        boost::asio::ip::tcp::resolver::iterator endpoint_iterator);
    void handle_connect(const boost::system::error_code& err);
    void handle_write_request(const boost::system::error_code& err);
    void handle_read_status_line(const boost::system::error_code& err);
    void handle_read_headers(const boost::system::error_code& err);
    void handle_read_content(const boost::system::error_code& err);
    void check_deadline();

    boost::asio::ip::tcp::resolver resolver_;
    socket_wrapper_ptr socket_;
    boost::asio::streambuf request_;
    boost::asio::streambuf response_;
    boost::asio::deadline_timer deadline_;

    std::stringstream headers_;
    std::stringstream content_;
    http_callback callback_;

    const int READ_TIMEOUT = 600;
};

typedef boost::shared_ptr<async_client> async_client_ptr;

} // namespace core

