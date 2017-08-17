/*
 * core.cpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */


#include <string>
#include <boost/python.hpp>
#include "http/async_client.hpp"

void http_async_client()
{

}

#if OSPLAT == 64
BOOST_PYTHON_MODULE(core_64)
#else
BOOST_PYTHON_MODULE(core)
#endif
{
	//boost::python::def("http_async_client", http_async_client);

}

