/*
 * async_client.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#include "async_client.hpp"

#include <glog/logging.h>

namespace core
{

async_client::async_client(boost::asio::io_service& io_service, int timeout, http_callback callback)
: resolver_(io_service),
  socket_(io_service),
  timer_(io_service, boost::posix_time::seconds(timeout)),
  callback_(callback)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
}

void async_client::start(const std::string& server, const std::string& path,
                         const std::string& method, const std::string& content,
                         bool keep_alive)
{
    // Form the request. We specify the "Connection: close" header so that the
    // server will close the socket after transmitting the response. This will
    // allow us to treat all data up until the EOF as the content.
    std::ostream request_stream(&request_);
    request_stream << method << " " << path << " HTTP/1.0\r\n";
    request_stream << "Host: " << server << "\r\n";
    request_stream << "Accept: */*\r\n";
    request_stream << "Connection: " << (keep_alive ? "keep_alive" : "close") << "\r\n\r\n";
    //request_stream << content << "\r\n";

    // Start an asynchronous resolve to translate the server and service names
    // into a list of endpoints.
    tcp::resolver::query query(server, "http");
    resolver_.async_resolve(query,
                            boost::bind(&async_client::handle_resolve, shared_from_this(),
                                        boost::asio::placeholders::error,
                                        boost::asio::placeholders::iterator));
}

void async_client::handle_resolve(const boost::system::error_code& err,
                                  tcp::resolver::iterator endpoint_iterator)
{
    if (!err)
    {
        // Attempt a connection to each endpoint in the list until we
        // successfully establish a connection.
        boost::asio::async_connect(socket_, endpoint_iterator,
                                   boost::bind(&async_client::handle_connect, shared_from_this(),
                                   boost::asio::placeholders::error));
        // Set time out callback.
        timer_.async_wait(boost::bind(&async_client::close_connection, shared_from_this(),
                                      boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
    }
}

void async_client::handle_connect(const boost::system::error_code& err)
{
    if (!err)
    {
        // The connection was successful. Send the request.
        boost::asio::async_write(socket_, request_,
                                 boost::bind(&async_client::handle_write_request, shared_from_this(),
                                 boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
    }
}

void async_client::handle_write_request(const boost::system::error_code& err)
{
    // Recevie a reply cancel time out callback.
    timer_.cancel();

    if (!err)
    {
        // Read the response status line. The response_ streambuf will
        // automatically grow to accommodate the entire line. The growth may be
        // limited by passing a maximum size to the streambuf constructor.
        boost::asio::async_read_until(socket_, response_, "\r\n",
                                      boost::bind(&async_client::handle_read_status_line, shared_from_this(),
                                      boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
    }
}

void async_client::handle_read_status_line(const boost::system::error_code& err)
{
    if (!err)
    {
        // Check that response is OK.
        std::istream response_stream(&response_);
        std::string http_version;
        response_stream >> http_version;
        response_stream >> status_code;
        std::string status_message;
        std::getline(response_stream, status_message);
        if (!response_stream || http_version.substr(0, 5) != "HTTP/")
        {
            DLOG(INFO) << __FUNCTION__ << " Invalid response " << this;
            callback_("invalid response", "", "");
            return;
        }
        if (status_code != 200)
        {
            DLOG(INFO) << __FUNCTION__ << this << " Response returned with status code " << status_code << " " << status_message;
            std::stringstream error_string;
            error_string << "status code " << status_code << " " << status_message;
            callback_(error_string.str(), "", "");
            return;
        }

        // Read the response headers, which are terminated by a blank line.
        boost::asio::async_read_until(socket_, response_, "\r\n\r\n",
                                      boost::bind(&async_client::handle_read_headers, shared_from_this(),
                                      boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
    }
}

void async_client::handle_read_headers(const boost::system::error_code& err)
{
    if (!err)
    {
        // Process the response headers.
        std::istream response_stream(&response_);
        std::string header;
        while (std::getline(response_stream, header) && header != "\r")
            headers << header << "\n";
        headers << "\n";

        // Write whatever content we already have to output.
        if (response_.size() > 0)
            content << &response_;

        // Start reading remaining data until EOF.
        boost::asio::async_read(socket_, response_,
                                boost::asio::transfer_at_least(1),
                                boost::bind(&async_client::handle_read_content, shared_from_this(),
                                boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
    }
}

void async_client::handle_read_content(const boost::system::error_code& err)
{
    if (!err)
    {
        // Write all of the data that has been read so far.
        content << &response_;

        // Continue reading remaining data until EOF.
        boost::asio::async_read(socket_, response_,
                                boost::asio::transfer_at_least(1),
                                boost::bind(&async_client::handle_read_content, shared_from_this(),
                                boost::asio::placeholders::error));
    }
    else if (err != boost::asio::error::eof)
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
    }
    else // EOF.
    {
        callback_("", headers.str(), content.str());
    }
}

void async_client::close_connection(const boost::system::error_code& err)
{
    if (!err)
    {
        socket_.close();
        callback_("request time out", "", "");
    }
    else
    {
        // The handler also be called when cancel the timer, and err is true.
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
    }
}

} // namespace core

