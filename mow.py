# std libs
import os
import imp 
import sys
import glob
import inspect
import logging
import argparse
import traceback

__all__ = ['task']
__version__ = '0.1.8'

MOW_FILE_NAMES = ('mowfile', 'Mowfile', 'mowfile.py' , 'Mowfile.py', )

# Where all the tasks are stored for quick lookup.
_tasks = {}
__internal_tasks = {}

# Interal Base logger
__logger = logging.getLogger('Mow')
__logger.setLevel(logging.WARN)

handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
handler.setFormatter(formatter)
__logger.addHandler(handler)

# logger to be used elsewhere
logger = __logger.getChild('task')

def loadMowfile(path=os.getcwd()):
    """
    loadMowfile(path=None)
    Loads a the first Mowfile it finds in a given path. Default path is the 
    current working directory.
    """

    file_path = None
    for mowfile in MOW_FILE_NAMES:
        tmp_path = os.path.join(os.path.abspath(path), mowfile)
        if os.path.exists(tmp_path) and os.path.isfile(tmp_path):
            file_path = tmp_path
            __logger.debug('Found Mowfile: %s', file_path)
            break
        #end if 
    # end for
    if not file_path:
        raise RuntimeError
    # end if 

    # load Mowfile
    # update the sys.path just in case there are relative imports.
    dir = os.path.dirname(file_path)
    sys.path.insert(0, dir)

    if file_path.endswith('.py'):
        # Use the standard import mechanism.
        module_name, ext = os.path.splitext(os.path.basename(file_path))
        __logger.debug('Importing Mowfile...')
        mod = __import__(module_name)
    else:
        # some magic to load Mowfile that don't end in .py
        mod = imp.new_module('mowfile')
        __logger.debug('Reading Mowfile...')
        with open(file_path) as file:
            code = compile(file.read(), file_path, 'exec')
        # end with 
        exec(code, mod.__dict__)
        globals()['mowfile'] = mod
    # end if

    # revert sys.path
    sys.path.pop(0)
    
    # mainly for testing.
    __logger.debug('Mowfile loaded.')
    return mod
# end loadMowfile    
        

# TODO:
# This is a feature I have to decide if I want to turn on. 
# It is on the same lines as .rake files.
def findMowFiles(paths=os.getenv('MOW_PATH', '')):
    """
    Finds all .mow files in the MOW_PATH and load them.
    """
    paths = paths.split(os.path.pathsep)
    paths.insert(0, os.getcwd())
    for path in reversed(paths):
        path = os.path.abspath(os.path.expanduser(os.path.expandvars(path)))
        files = glob.glob(os.path.join(path, '*.mow'))
        for file in files:
            # TODO: update to the mowfile style.
            exec(open(file).read()) # I hate this line
        # end for
    # end for
# end def findMowFiles

def task(name=None, author=None, version=(0,1,0), usage='%prog %name'):
    """
    task(name=None, author=None, version=(0,1,0), usage='%prog %name')
    
    The task decorator that makes all this work.
    The decorated function's docstring is used as the description of the task.
    
    name (str): the name of the task, to namespace the task use a colon (':').  ex: db:migrate
                If no name is given the function name is used and '__' will be converted to ':' to give it a namespace.
    author (str): just the name or email of the author.
    version (tuple): 3 int tuple of the version number.
    usage (str): Usage information. %prog will be replaced with 'mow'.
                %name will be replace with the name of the task.

    """
    def wrapper(func):
        # store the descriptive information
        func._name = name or func.__name__.replace('__', ':')
        func._author = author
        func._version = version
        func._usage = usage.replace('%prog', 'mow').replace('%name', func._name)
        func._description = func.__doc__ or ''

        if func._name in __internal_tasks:
            raise RuntimeError("'%s' is the name of a built-in task, please rename your task" % (func._name))
        # end if
        
        if func._name in _tasks:
            __logger.warn("Task '%s' replaces another task with the same name" %(func._name))
        # end if

        # store for quick lookup.
        _tasks[func._name] = func
        __logger.debug("Added function '%s:%s' as task '%s'", 
                       func.__code__.co_filename, func.__name__, name)
        return func
    # end def wrapper
    return wrapper
# end def task

#
# Commandline 
#
#

def parseArgs(args):
    """                                                                            
    parseArgs(args)                                                                
    parses the left over args and converts them to kwargs to be passed             
    to tasks.                                                                      
    """
    func_args = []
    func_kwargs = {}

    for arg in args:
        if arg.startswith('--'):
            arg = arg.replace('--', '')
            key, eq, value = arg.partition('=')
            key = key.replace('-', '_')
            if not value:
                func_kwargs[key] = True
            else:
                func_kwargs[key] = value
            # end if
        else:
            func_args.append(arg)
        # end if
    # end for
    return func_args, func_kwargs
# end def parseArgs

def main(cmd_args=sys.argv[1:]):
    """
    main()
    main function for loading a Mowfile and executing a task.
    """
    parser = argparse.ArgumentParser(description='Mow')
    parser.add_argument('task', help='Task name')
    parser.add_argument('-v', dest='verbose', action='count', default=0, 
                        help = 'Prints outs more info. -v = info, -vv = debug')
    parser.add_argument('-C', '--directory', default=os.getcwd(),
                        help = 'Directory to find the Mowfile. Default: Current di\
rectory.')

    # parse the args the are defined.
    known_args, unknown_args = parser.parse_known_args(cmd_args)
    # parse the args that aren't defined.
    args, kwargs = parseArgs(unknown_args)
    if known_args.verbose == 1:
        __logger.setLevel(logging.INFO)
        logger.setLevel(logging.INFO)
    elif known_args.verbose == 2:
        __logger.setLevel(logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    # end if

    try:
        loadMowfile(known_args.directory)
    except RuntimeError as exp:
        # raised if not file was found
        msg = "Could not find Mowfile in '%s'.\nValid filenames: " % (known_args.directory) + \
              ', '.join(MOW_FILE_NAMES)
        __logger.error(msg)
        return 1
    except Exception as exp:
        __logger.exception('Error Loading Mowfile:')
        return 1
    # end try

    task = __internal_tasks.get(known_args.task) or _tasks.get(known_args.task)
    if not task:
        __logger.error('Task not found: %s', known_args.task)
        return 1
    else:
        try:
            __logger.debug("Executing task '%s'", known_args.task)
            task(*args, **kwargs)
            __logger.debug('Task complete.')
            return 0
        except Exception as exp:
            __logger.exception('Task Error:')
            print('For help type: mow help %s' % known_args.task)
            return 1
        # end if
    # end if
# end def main


#
# Tasks
#
# Internal tasks don't use the task decorator so that they don't require a namespace
#

def list_tasks(namespace=None):
    """
    List all available tasks.
    """
    if not namespace:
        print('Built-in Tasks:')
        print('-'*75)
        for task_name in sorted(__internal_tasks):
            task = __internal_tasks[task_name]
            print('%-25s: %s' % (task_name, task._description.strip()))
        # end def for
    # end if
    print('\nLoaded Tasks:')
    print('-'*75)
    for task_name in sorted(_tasks):
        if namespace and not task_name.startswith(namespace):
            continue
        # end if
        task = _tasks[task_name]
        print('%-25s: %s' % (task_name, task._description.strip()))
    # end def for
    print('-'*75)
# end def list_tasks
list_tasks.__internal = True
list_tasks._name = 'list'
list_tasks._author = 'brandonvfx'
list_tasks._version = (0,1,0)
list_tasks._usage = 'mow list [namespace]'
list_tasks._description = list_tasks.__doc__ or ''
__internal_tasks['list'] = list_tasks

def print_task_help(task_name, extended=False):
    """
    Get help for a task.
    """
    task = __internal_tasks.get(task_name) or _tasks.get(task_name)
    if task:
        if getattr(task, '__internal', False):
            print('Built-in Task')
        # end if
        print('Name: %s' % (task._name))
        print('Usage:\n    %s' % (task._usage))
        print('Description: %s' % (task._description.strip()))
        if extended:
            print('Author: %s' % (task._author))
            print('Version: %d.%d.%d' % (task._version))
            print('File: %s:%d' % (task.__code__.co_filename, task.__code__.co_firstlineno))
            print('Function: %s' % (task.__name__))
        # end if
        return
    # end if
    print('Task not found: %s' % (task_name))
# end def print_task_help
print_task_help.__internal = True
print_task_help._name = 'help'
print_task_help._author = 'brandonvfx'
print_task_help._version = (0,1,0)
print_task_help._usage = 'mow help task'
print_task_help._description = print_task_help.__doc__ or ''
__internal_tasks['help'] = print_task_help
    
