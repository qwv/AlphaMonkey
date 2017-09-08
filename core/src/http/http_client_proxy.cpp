/*
 * http_client_proxy.cpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#include "http_client_proxy.hpp"

#include <glog/logging.h>

namespace core
{

http_client_proxy::http_client_proxy(const std::string& host,
    const std::string& port,
    const std::string& method,
    const std::string& path,
    const std::string& headers,
    const std::string& content,
    int timeout,
    bool usessl,
    bool keep_alive)
{
	DLOG(INFO) << __FUNCTION__ << " " << this;
    if (usessl)
    {
        boost::asio::ssl::context ctx(boost::asio::ssl::context::sslv23);
        ctx.set_default_verify_paths();
        new_async_client = boost::make_shared<async_client>(io_service, ctx, host,
            boost::bind(&http_client_proxy::callback, this, 
                boost::placeholders::_1,
                boost::placeholders::_2,
                boost::placeholders::_3));
    }
    else
    {
        new_async_client = boost::make_shared<async_client>(io_service,
            boost::bind(&http_client_proxy::callback, this, 
                boost::placeholders::_1,
                boost::placeholders::_2,
                boost::placeholders::_3));
    }

    new_async_client->start(host, port, path, method, headers, content, timeout, keep_alive);
}

http_client_proxy::~http_client_proxy()
{
	DLOG(INFO) << __FUNCTION__ << " " << this;
    new_async_client.reset();
}

void http_client_proxy::start()
{
	DLOG(INFO) << __FUNCTION__ << " " << this;
    io_service.run();
}

void http_client_proxy::callback(const std::string& err, 
    const std::string& headers, 
    const std::string& content)
{
	DLOG(INFO) << __FUNCTION__ << " " << this;
}

http_client_proxy_wrapper::http_client_proxy_wrapper(PyObject *self,
    const std::string& host,
    const std::string& port,
    const std::string& method,
    const std::string& path,
    const std::string& headers,
    const std::string& content,
    const int timeout,
    const bool usessl,
    const bool keep_alive)
: http_client_proxy(host, port, method, path, headers, content, timeout, usessl, keep_alive),
  self_(self)
{
	DLOG(INFO) << __FUNCTION__ << " " << this;
    boost::python::incref(self_);
}

http_client_proxy_wrapper::~http_client_proxy_wrapper()
{
	DLOG(INFO) << __FUNCTION__ << " " << this;
    boost::python::decref(self_);
    self_ = NULL;
}

void http_client_proxy_wrapper::callback(const std::string& err, 
    const std::string& headers, 
    const std::string& content)
{
	DLOG(INFO) << __FUNCTION__ << " " << this;
    BEGIN_CALL_SCRIPT
        if(self_) boost::python::call_method<void>(self_, "callback", err, headers, content);
    END_CALL_SCRIPT
}

} // namespace core
