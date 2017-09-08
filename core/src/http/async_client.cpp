/*
 * async_client.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#include "async_client.hpp"

#include <glog/logging.h>

namespace core
{

async_client::async_client(boost::asio::io_service& io_service,
    const http_callback& callback)
: resolver_(io_service),
  deadline_(io_service),
  callback_(callback)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    socket_ = socket_wrapper_ptr(new socket_wrapper(io_service));
}

async_client::async_client(boost::asio::io_service& io_service,
    boost::asio::ssl::context& ctx,
    const std::string& host,
    const http_callback& callback)
: resolver_(io_service),
  deadline_(io_service),
  callback_(callback)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    socket_ = socket_wrapper_ptr(new socket_wrapper(io_service, ctx));
    socket_->get_ssl_socket().set_verify_mode(boost::asio::ssl::verify_none);
    socket_->get_ssl_socket().set_verify_callback(boost::asio::ssl::rfc2818_verification(host));
}

void async_client::start(const std::string& host, const std::string& port,
    const std::string& path, const std::string& method,
    const std::string& headers, const std::string& content,
    const int timeout, bool keep_alive)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    // Form the request. We specify the "Connection: close" header so that the
    // server will close the socket after transmitting the response. This will
    // allow us to treat all data up until the EOF as the content.
    std::ostream request_stream(&request_);
    request_stream << method << " " << path << " HTTP/1.0\r\n";
    request_stream << "Host: " << host << "\r\n";
    request_stream << "Accept: */*\r\n";
    request_stream << "Connection: " << (keep_alive ? "keep_alive" : "close") << "\r\n";
    if (headers.size() != 0)
    {
        request_stream << headers << "\r\n";
    }
    if (content.size() != 0)
    {
        request_stream << "Content-Length: " << content.size() << "\r\n";
        // May be assign in headers.
        //request_stream << "Content-Type: " << "application/json" << "\r\n";
    }
    request_stream << "\r\n";
    request_stream << content;

    // Start an asynchronous resolve to translate the server and service names
    // into a list of endpoints.
    boost::asio::ip::tcp::resolver::query query(host, port);
    resolver_.async_resolve(query,
        boost::bind(&async_client::handle_resolve, shared_from_this(),
            boost::asio::placeholders::error,
            boost::asio::placeholders::iterator));

    // Set a deadline for the connect operation.
    deadline_.expires_from_now(boost::posix_time::seconds(timeout));
}

// This function terminates all the actors to shut down the connection.
void async_client::stop()
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    boost::system::error_code err;
    socket_->lowest_layer().close(err);
    deadline_.cancel();
}

void async_client::handle_resolve(const boost::system::error_code& err,
    boost::asio::ip::tcp::resolver::iterator endpoint_iterator)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    if (!err)
    {
        // Attempt a connection to each endpoint in the list until we
        // successfully establish a connection.
        boost::asio::async_connect(socket_->lowest_layer(), endpoint_iterator,
            boost::bind(&async_client::handle_connect, shared_from_this(),
                boost::asio::placeholders::error));

        // Start the deadline actor. You will note that we're not setting any
        // particular deadline here. Instead, the connect and input actors will
        // update the deadline prior to each asynchronous operation.
        deadline_.async_wait(boost::bind(&async_client::check_deadline, shared_from_this()));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
        stop();
    }
}

void async_client::handle_connect(const boost::system::error_code& err)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    if (!socket_->lowest_layer().is_open())
    {
        stop();
        callback_("request time out", "", "");
    }
    else if (!err)
    {
        if (socket_->usessl_)
        {
            // SSL need handshake.
            socket_->get_ssl_socket().async_handshake(boost::asio::ssl::stream_base::client,
                boost::bind(&async_client::handle_handshake, shared_from_this(),
                    boost::asio::placeholders::error));
        }
        else
        {
            on_connect();
        }
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
        stop();
    }
}

void async_client::handle_handshake(const boost::system::error_code& err)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    if (!err)
    {
        // Handshake successful.
        on_connect();
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
        stop();
    }
}

void async_client::on_connect()
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    // The connection was successful. Send the request.
    boost::asio::async_write(*socket_, request_,
        boost::bind(&async_client::handle_write_request, shared_from_this(),
            boost::asio::placeholders::error));
}

void async_client::handle_write_request(const boost::system::error_code& err)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    // Set a deadline for the read operation.
    deadline_.expires_from_now(boost::posix_time::seconds(READ_TIMEOUT));

    if (!err)
    {
        // Read the response status line. The response_ streambuf will
        // automatically grow to accommodate the entire line. The growth may be
        // limited by passing a maximum size to the streambuf constructor.
        boost::asio::async_read_until(*socket_, response_, "\r\n",
            boost::bind(&async_client::handle_read_status_line, shared_from_this(),
                boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
        stop();
    }
}

void async_client::handle_read_status_line(const boost::system::error_code& err)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    if (!err)
    {
        // Check that response is OK.
        std::istream response_stream(&response_);
        std::string http_version;
        unsigned int status_code;
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
            DLOG(INFO) << __FUNCTION__ << this << " Response returned with status code " 
                << status_code << " " << status_message;
            std::stringstream error_string;
            error_string << "status code " << status_code << " " << status_message;
            callback_(error_string.str(), "", "");
            return;
        }

        // Read the response headers, which are terminated by a blank line.
        boost::asio::async_read_until(*socket_, response_, "\r\n\r\n",
            boost::bind(&async_client::handle_read_headers, shared_from_this(),
                boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
        stop();
    }
}

void async_client::handle_read_headers(const boost::system::error_code& err)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    if (!err)
    {
        // Process the response headers.
        std::istream response_stream(&response_);
        std::string header;
        while (std::getline(response_stream, header) && header != "\r")
            headers_ << header << "\n";
        headers_ << "\n";

        // Write whatever content we already have to output.
        if (response_.size() > 0)
            content_ << &response_;

        // Start reading remaining data until EOF.
        boost::asio::async_read(*socket_, response_,
            boost::asio::transfer_all(),
            boost::bind(&async_client::handle_read_content, shared_from_this(),
                boost::asio::placeholders::error));
    }
    else
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
        stop();
    }
}

void async_client::handle_read_content(const boost::system::error_code& err)
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    if (!err)
    {
        // Write all of the data that has been read so far.
        content_ << &response_;

        // Continue reading remaining data until EOF.
        boost::asio::async_read(*socket_, response_,
            boost::asio::transfer_at_least(64),
            boost::bind(&async_client::handle_read_content, shared_from_this(),
                boost::asio::placeholders::error));
    }
    else if (err != boost::asio::error::eof)
    {
        DLOG(ERROR) << __FUNCTION__ << " " << this << " Error: " << err << " " << err.message();
        stop();
    }
    else // EOF.
    {
        stop();
        callback_("", headers_.str(), content_.str());
    }
}

void async_client::check_deadline()
{
    DLOG(INFO) << __FUNCTION__ << " " << this;
    // The handler also be called when cancel the timer, and err is true.
    // Check whether the deadline has passed. We compare the deadline against
    // the current time since a new asynchronous operation may have moved the
    // deadline before this actor had a chance to run.
    if (deadline_.expires_at() <= boost::asio::deadline_timer::traits_type::now())
    {
        // The deadline has passed. The socket is closed so that any outstanding
        // asynchronous operations are cancelled.
        socket_->lowest_layer().close();

        // There is no longer an active deadline. The expiry is set to positive
        // infinity so that the actor takes no action until a new deadline is set.
        deadline_.expires_at(boost::posix_time::pos_infin);
    }
}

} // namespace core

