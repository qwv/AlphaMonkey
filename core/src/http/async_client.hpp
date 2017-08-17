/*
 * async_client.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#pragma once

#include <iostream>
#include <istream>
#include <ostream>
#include <string>
#include <boost/asio.hpp>
#include <boost/bind.hpp>

using boost::asio::ip::tcp;

namespace core
{

class async_client
{

public:
    async_client(boost::asio::io_service& io_service,
                 const std::string& server, const std::string& path,
                 const std::string& method, const std::string& content,
                 int timeout, bool keep_alive);

private:
    void handle_resolve(const boost::system::error_code& err,
                        tcp::resolver::iterator endpoint_iterator);

    void handle_connect(const boost::system::error_code& err);

    void handle_write_request(const boost::system::error_code& err);

    void handle_read_status_line(const boost::system::error_code& err);

    void handle_read_headers(const boost::system::error_code& err);

    void handle_read_content(const boost::system::error_code& err);

    void close_connection(const boost::system::error_code& err);

    tcp::resolver resolver_;
    tcp::socket socket_;
    boost::asio::streambuf request_;
    boost::asio::streambuf response_;
    boost::asio::deadline_timer timer_;
};

} // namespace core

