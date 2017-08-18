/*
 * async_client.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#include "async_client.hpp"

namespace core
{

async_client::async_client(boost::asio::io_service& io_service,
                           const std::string& server, const std::string& path,
                           const std::string& method, const std::string& content,
                           int timeout, bool keep_alive)
: resolver_(io_service),
  socket_(io_service),
  timer_(io_service, boost::posix_time::seconds(timeout))
{
    // Form the request. We specify the "Connection: close" header so that the
    // server will close the socket after transmitting the response. This will
    // allow us to treat all data up until the EOF as the content.
    std::ostream request_stream(&request_);
    request_stream << method << " " << path << " HTTP/1.0\r\n";
    request_stream << "Host: " << server << "\r\n";
    request_stream << "Accept: */*\r\n";
    request_stream << "Connection: " << (keep_alive ? "keep_alive" : "close") << "\r\n\r\n";
    request_stream << content << "\r\n";

    // Start an asynchronous resolve to translate the server and service names
    // into a list of endpoints.
    tcp::resolver::query query(server, "http");
    resolver_.async_resolve(query,
                            boost::bind(&async_client::handle_resolve, this,
                                        boost::asio::placeholders::error,
                                        boost::asio::placeholders::iterator));
    // Set time out callback
    timer_.async_wait(boost::bind(&async_client::close_connection, this,
                                  boost::asio::placeholders::error));
}

void async_client::handle_resolve(const boost::system::error_code& err,
                                  tcp::resolver::iterator endpoint_iterator)
{
    if (!err)
    {
        // Attempt a connection to each endpoint in the list until we
        // successfully establish a connection.
        boost::asio::async_connect(socket_, endpoint_iterator,
                                   boost::bind(&async_client::handle_connect, this,
                                   boost::asio::placeholders::error));
    }
    else
    {
        std::cout << "Error: " << err.message() << "\n";
    }
}

void async_client::handle_connect(const boost::system::error_code& err)
{
    if (!err)
    {
        // The connection was successful. Send the request.
        boost::asio::async_write(socket_, request_,
                                 boost::bind(&async_client::handle_write_request, this,
                                 boost::asio::placeholders::error));
    }
    else
    {
        std::cout << "Error: " << err.message() << "\n";
    }
}

void async_client::handle_write_request(const boost::system::error_code& err)
{
    if (!err)
    {
        // Read the response status line. The response_ streambuf will
        // automatically grow to accommodate the entire line. The growth may be
        // limited by passing a maximum size to the streambuf constructor.
        boost::asio::async_read_until(socket_, response_, "\r\n",
                                      boost::bind(&async_client::handle_read_status_line, this,
                                      boost::asio::placeholders::error));
    }
    else
    {
        std::cout << "Error: " << err.message() << "\n";
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
        unsigned int status_code;
        response_stream >> status_code;
        std::string status_message;
        std::getline(response_stream, status_message);
        if (!response_stream || http_version.substr(0, 5) != "HTTP/")
        {
            std::cout << "Invalid response\n";
            return;
        }
        if (status_code != 200)
        {
            std::cout << "Response returned with status code ";
            std::cout << status_code << "\n";
            return;
        }

        // Read the response headers, which are terminated by a blank line.
        boost::asio::async_read_until(socket_, response_, "\r\n\r\n",
                                      boost::bind(&async_client::handle_read_headers, this,
                                      boost::asio::placeholders::error));
    }
    else
    {
        std::cout << "Error: " << err << "\n";
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
            std::cout << header << "\n";
        std::cout << "\n";

        // Write whatever content we already have to output.
        if (response_.size() > 0)
        std::cout << &response_;

        // Start reading remaining data until EOF.
        boost::asio::async_read(socket_, response_,
                                boost::asio::transfer_at_least(1),
                                boost::bind(&async_client::handle_read_content, this,
                                boost::asio::placeholders::error));
    }
    else
    {
        std::cout << "Error: " << err << "\n";
    }
}

void async_client::handle_read_content(const boost::system::error_code& err)
{
    if (!err)
    {
        // Write all of the data that has been read so far.
        std::cout << &response_;

        // Continue reading remaining data until EOF.
        boost::asio::async_read(socket_, response_,
                                boost::asio::transfer_at_least(1),
                                boost::bind(&async_client::handle_read_content, this,
                                boost::asio::placeholders::error));
    }
    else if (err != boost::asio::error::eof)
    {
        std::cout << "Error: " << err << "\n";
    }
}

void async_client::close_connection(const boost::system::error_code& err)
{
    if (!err)
    {
    }
    else
    {
        std::cout << "Error: " << err.message() << "\n";
    }
}

} // namespace core
