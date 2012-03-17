# std libs
import os
import imp 
import sys
import glob
import inspect

__all__ = ['task']

MOW_FILE_NAMES = ('mowfile', 'Mowfile', 'mowfile.py' , 'Mowfile.py', )

# Where all the tasks are sorted for quick lookup.
tasks = {}
INTERNAL_TASKS = {}

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
            break
        #end if 
    # end for
    if not file_path:
        msg = 'Could not find Mowfile. Valid filenames:\n' + \
              ', '.join(MOW_FILE_NAMES)
        raise RuntimeError(msg)
    # end if 

    # load Mowfile
    # update the sys.path just in case there are relative imports.
    dir = os.path.dirname(file_path)
    sys.path.insert(0, dir)

    if file_path.endswith('.py'):
        # Use the standard import mechanism.
        module_name, ext = os.path.splitext(os.path.basename(file_path))
        mod = __import__(module_name)
    else:
        # some magic to load Mowfile that don't end in .py
        mod = imp.new_module('mowfile')
        with open(file_path) as file:
            code = compile(file.read(), file_path, 'exec')
        # end with 
        exec(code, mod.__dict__)
    # end if

    # revert sys.path
    sys.path.pop(0)
    
    # mainly for testing.
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

def task(name, author=None, version=(0,1,0), help='usage: %prog %name'):
    """
    task(name, author=None, version=(0,1,0), help='usage: %prog %name')
    
    The task decorator that make all this work.
    The decorated function's docstring is used as the description of the task.
    
    name (str): the name of the task it must be namespaced. 
                The namespace separator is ':' . ex: db:migrate
    author (str): just the name or email of the author.
    version (tuple): 3 int tuple of the version number.
    help (str): help information for task usage. %prog will be replaced with 'mow'.
                %name will be replace with the name of the task.

    """
    def wrapper(func):
        # Tasks that are not part of mow are required to have a namespace.
        if name and (':' not in name or name.startswith(':')):
            print('Function: %s' % func.__name__)
            print('File: %s:%s' % (func.__code__.co_filename, func.__code__.co_firstlineno))
            print
            raise RuntimeError("'%s' - Task name must be namespaced." % (name))
        # end if

        # store the descriptive information
        func._name = name
        func._author = author
        func._version = version
        func._help = help 
        func._description = func.__doc__ or ''

        # store for quick lookup.
        tasks[name] = func
        # end if
        return func
    # end def wrapper
    return wrapper
# end def task

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
        print('Internal Tasks:')
        print('-'*75)
        for task_name in sorted(INTERNAL_TASKS):
            task = INTERNAL_TASKS[task_name]
            print('%-25s: %s' % (task_name, task._description.strip()))
        # end def for
    # end if
    print
    print('Loaded Tasks:')
    print('-'*75)
    for task_name in sorted(tasks):
        if namespace and not task_name.startswith(namespace):
            continue
        # end if
        task = tasks[task_name]
        print('%-25s: %s' % (task_name, task._description.strip()))
    # end def for
    print('-'*75)
# end def list_tasks
list_tasks.__internal = True
list_tasks._name = 'list'
list_tasks._author = 'brandonvfx'
list_tasks._version = (0,1,0)
list_tasks._help = 'usage: %prog %name [namespace]'
list_tasks._description = list_tasks.__doc__ or ''
INTERNAL_TASKS['list'] = list_tasks

def print_task_help(task_name):
    """
    Get help for a task.
    """
    task = INTERNAL_TASKS.get(task_name) or tasks.get(task_name)
    if task:
        if getattr(task, '__internal', False):
            print('Builtin Task')
        # end if
        print('Name: %s' % (task._name))
        print('Author: %s' % (task._author))
        print('Version: %d.%d.%d' % (task._version))
        print('File: %s:%d' % (task.__code__.co_filename, task.__code__.co_firstlineno))
        print('Function: %s' % (task.__name__))
        print('Description: %s' % (task._description.strip()))
        print
        print(task._help.replace('%prog', 'mow').replace('%name', task._name))
        return
    # end if
    print('Task not found: %s' % (task_name))
# end def print_task_help
print_task_help.__internal = True
print_task_help._name = 'help'
print_task_help._author = 'brandonvfx'
print_task_help._version = (0,1,0)
print_task_help._help = 'usage: %prog %name task'
print_task_help._description = print_task_help.__doc__ or ''
INTERNAL_TASKS['help'] = print_task_help
    
