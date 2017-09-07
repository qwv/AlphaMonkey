/*
 * socket_wrapper.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#pragma once

#include <boost/asio.hpp>
#include <boost/asio/ssl.hpp>
#include <boost/make_shared.hpp>

namespace core
{

class socket_wrapper
{
public:
    typedef boost::asio::ip::tcp::socket socket;

    typedef boost::asio::ssl::stream<socket> ssl_socket;

    typedef boost::shared_ptr<socket> socket_ptr;

    typedef boost::shared_ptr<ssl_socket> ssl_socket_ptr;

    typedef typename socket::lowest_layer_type lowest_layer_type;

    socket_wrapper(boost::asio::io_service& io_service)
    {
        socket_ = boost::make_shared<socket>(socket(io_service));
        usessl_ = false;
    }

    socket_wrapper(boost::asio::io_service& io_service, boost::asio::ssl::context& ctx)
    {
        // Can not use make_shared, because ssl_socket inherit nocopyable and its constructor is protected.
        //ssl_socket_ = boost::make_shared<ssl_socket>(ssl_socket(io_service, ctx));
        ssl_socket_ = ssl_socket_ptr(new ssl_socket(io_service, ctx));
        usessl_ = true;
    }

    ~socket_wrapper() {}

    lowest_layer_type& lowest_layer()
    {
        return usessl_ ? ssl_socket_->lowest_layer() : socket_->lowest_layer();
    }

    template <typename MutableBufferSequence>
    std::size_t read_some(const MutableBufferSequence& buffers)
    {
        return usessl_ ? ssl_socket_->read_some(buffers) : socket_->read_some(buffers);
    }

    template <typename MutableBufferSequence>
    std::size_t read_some(const MutableBufferSequence& buffers, boost::system::error_code& ec)
    {
        return usessl_ ? ssl_socket_->read_some(buffers, ec) : socket_->read_some(buffers, ec);
    }

    template <typename MutableBufferSequence, typename ReadHandler>
    void async_read_some(const MutableBufferSequence& buffers, BOOST_ASIO_MOVE_ARG(ReadHandler) handler)
    {
        return usessl_ ? ssl_socket_->async_read_some(buffers, handler) : socket_->async_read_some(buffers, handler);
    }

    template <typename ConstBufferSequence>
    std::size_t write_some(const ConstBufferSequence& buffers)
    {
        return usessl_ ? ssl_socket_->write_some(buffers) : socket_->write_some(buffers);
    }

    template <typename ConstBufferSequence>
    std::size_t write_some(const ConstBufferSequence& buffers, boost::system::error_code& ec)
    {
        return usessl_ ? ssl_socket_->write_some(buffers, ec) : socket_->write_some(buffers, ec);
    }

    template <typename MutableBufferSequence, typename ReadHandler>
    void async_write_some(const MutableBufferSequence& buffers, BOOST_ASIO_MOVE_ARG(ReadHandler) handler)
    {    
        return usessl_ ? ssl_socket_->async_write_some(buffers, handler) : socket_->async_write_some(buffers, handler);
    }

private:
    bool usessl_;

    union
    {
        socket_ptr socket_;
        ssl_socket_ptr ssl_socket_;
    };
};

typedef boost::shared_ptr<socket_wrapper> socket_wrapper_ptr;

} // namespace core
