# Mow
[![Build Status](https://secure.travis-ci.org/brandonvfx/mow.png?branch=master)](http://travis-ci.org/brandonvfx/mow)

## Overview

**Mow** is a lightweight Makefile/Rakefile alternative. It allows developers to turn python functions into a command line tools.


##Example

####Task defined in Mowfile:

	from mow import task

	@task()
	def greet(name, greeting='Hello'):
		print '%s, %s.' % (greeting, name)

####Commandline Usage:

	\> mow greet Bob
	Hello, Bob.
	
	\> mow greet --greeting="Goodbye" Bob
	Goodbye, Bob.
	
## Mowfiles
Mowfiles are where tasks are defined or loaded. The mowfile must have one of the following names: 

`mowfile, Mowfile, mowfile.py, or Mowfile.py`

By default **mow** will search the current directory for the Mowfile but the -C/--directory option can be used to specify another location.

	
## Built-in tasks

####list:
Lists out all the currently available tasks.

Usage: `mow list [namespace]`
	
	\> mow list
	
	Built-in Tasks:
	---------------------------------------------------------------------------
	help                     : Get help for a task.
	list                     : List all available tasks.

	Loaded Tasks:
	---------------------------------------------------------------------------
	test                     : Mow test runner
	---------------------------------------------------------------------------
	
####help:
Prints out information about a task.

Usage: `mow help TASK_NAME`

	\> mow help list
	Built-in Task
	Name: list
	Usage:
	    mow list [namespace]
	Description: List all available tasks.
	
	\> mow help list --extended
	Built-in Task
	Name: list
	Usage:
    	mow list [namespace]
	Description: List all available tasks.
	Author: brandonvfx
	Version: 0.1.0
	File: mow.py:234
	Function: list_tasks

##Mow help

	\> mow --help

	usage: mow [-h] [-v] [-C DIRECTORY] task

	Mow
	
	positional arguments:
	  task                  Task name
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -v                    Prints outs more info. -v = info, -vv = debug
	  -C DIRECTORY, --directory DIRECTORY
	                        Directory to find the Mowfile. Default: Current
	                        directory.
	                        	
## Task Options
	
	task(name=None, author=None, version=(0,1,0), usage='%prog %name')                              
                                                                                                    
    The decorated function's docstring is used as the description of the task.                 
                                                                                               
    name (str): the name of the task, to namespace the task use a colon (':').  ex: db:migrate
                If no name is given the function name is used and '__' will be converted to ':' 
                to give it a namespace.                                                                      
    author (str): just the name or email of the author.                                        
    version (tuple): 3 int tuple of the version number.                                        
    usage (str): Usage information. %prog will be replaced with 'mow'.                         
                 %name will be replace with the name of the task.  

## Commandline Usage
**mow** is pretty simple to use, it only has one required argument (task name) and one optional option (-C/--directory). All other arguments and options are passed into the task function as *arg and **kwargs. 
	
	/> mow db:migrate production --host=localhost
	
	Translates to:
	db_migrate(*('production',), **{'host':'localhost'})
	
There is no type casting is done before these values are passed to the task function so they will all be strings. There is only one case where this is not true, for an option without a value it is assumed to be a bool flags and its value will automatically be set to **True**

	/> mow db:migrate production --host=localhost --dry-run
	
	Translates to:
	db_migrate(*('production',), **{'host':'localhost', 'dry_run':True})