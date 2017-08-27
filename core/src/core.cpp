/*
 * core.cpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */


#include <string>
#include <boost/python.hpp>
#include "http/http_client_proxy.hpp"

BOOST_PYTHON_MODULE(core)
{
    boost::python::class_<core::http_client_proxy, 
        boost::shared_ptr<core::http_client_proxy_wrapper>,
        boost::noncopyable>("http_client_proxy", 
            boost::python::init<const std::string&,
                const std::string&,
                const std::string&,
                const std::string&,
                const std::string&,
                const std::string&,
                int,
                bool,
                bool>())
        .def("start", &core::http_client_proxy::start)
    ;
}

