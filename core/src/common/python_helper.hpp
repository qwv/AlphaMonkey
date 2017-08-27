/*
 * python_helper.hpp
 * 
 * Copyright (C) 2017-2031  YuHuan Chow <chowyuhuan@gmail.com>
 */

#pragma once

#include <boost/python.hpp>
#include <string>
#include <pthread.h>
#include <glog/logging.h>

#define BEGIN_CALL_SCRIPT	\
	{			\
	aquire_py_GIL gil;	\
	try	\
	{	

#define BEGIN_CALL_SCRIPT_WITHOUT_GIL	\
	{	\
	try	\
	{	

#define END_CALL_SCRIPT	\
	}	\
	catch(const boost::python::error_already_set &e)	\
	{	\
		PyErr_Print();	\
	}	\
	}

namespace core
{

class aquire_py_GIL
{
public:
    explicit aquire_py_GIL()
	{
		state_ = PyGILState_Ensure();
    }

	~aquire_py_GIL()
	{
        PyGILState_Release(state_);
	}
private:
    PyGILState_STATE state_;
};

} //namespace core

