# Mow

## Overview

**Mow** is a lightweight Make/Rake alternative. It allows developers to turn python functions into a command line tools.

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
Mowfiles are where tasks are defined or loaded. The mowfile most have one of the following names: mowfile, Mowfile, mowfile.py, or Mowfile.py .
	
## Built-in tasks

####list:
Lists out all the currently available tasks.
	
	\> mow list
	
	Internal Tasks:
	---------------------------------------------------------------------------
	help                     : Get help for a task.
	list                     : List all available tasks.

	Loaded Tasks:
	---------------------------------------------------------------------------
	---------------------------------------------------------------------------
	
####help:
Prints out information about a task.

	\> mow help list
	
	Builtin Task
	Name: list
	Author: brandonvfx
	Version: 0.1.0
	File: mow.py:127
	Function: list_tasks
	Description: List all available tasks.

	usage: mow list [namespace]
	

###Mow help

	\> mow --help

	usage: mow [-h] [-C DIRECTORY] task

	Mow
	
	positional arguments:
  		task                  Task name

	optional arguments:
  	  -h, --help            show this help message and exit
  	  -C DIRECTORY, --directory DIRECTORY
  	  						Directory to find the Mowfile. Default: Current
                        	directory.
                        	
## Task Options
	
	task(name, author=None, version=(0,1,0), usage='%prog %name')                              
                                                                                               
    The task decorator that make all this work.                                                
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
	
	/> mow db:migrate production --host=test_db
	
	Translates to:
	db_migrate(*('production',), **{'host':'test_db'})
	
There is no type casting is done before these values are passed to the task function so they will all be strings. There is only one case where this is not true, for an option without a value it is assumed to be a bool flags and its value will automatically be set to **True**

	/> mow db:migrate production --host=test_db --dry-run
	
	Translates to:
	db_migrate(*('production',), **{'host':'test_db', 'dry-run':True})