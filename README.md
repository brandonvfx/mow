# Mow

## Overview

**Mow** allows for you to turn python functions into command line tools. It is based on ideas from Rake.


## Mowfiles
Mowfiles are where tasks are defined or loaded; they can be names one of the following names mowfile, Mowfile, mowfile.py, or Mowfile.py .

## Creating a Task
Creating a task is very easy just add a simple decorator to the function giving it a name and namespace. 

####Tasks:

	from mow import task

	@task('print:hello_world')
	def hello_world(*args, **kwargs):
		print 'Hello, World.)
		
	@task()
	def db__migrate(*args, **kwargs):
		print "Migrating"

####Shell commands:

	\> mow print:hello_world
	
	\> mow db:migrate
	
	
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
	
	task(name=None, author=None, version=(0,1,0), help='usage: %prog %name')

	The task decorator that make all this work.
	The decorated function's docstring is used as the description of the task.

	name (str): the name of the task it must be namespaced. 
            The namespace separator is ':' If no name is passed the function name 
            will be used and '__' will be replaced with ':'. ex: db:migrate
	author (str): just the name or email of the author.
	version (tuple): 3 int tuple of the version number.
	help (str): help information for task usage. %prog will be replaced with 'mow'.
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