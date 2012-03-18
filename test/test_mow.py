import os
import sys
import logging
import tempfile
import unittest

sys.path.insert(0, '..')

import mow

mow.__logger.setLevel(logging.FATAL)


def mk_mowfile(file_path, new_code=None):
    code = [
        'import mow\n', '\n', "@mow.task('testing')\n", 
        'def test_task():\n','    print "hello"\n'
    ]
    fd = open(file_path, 'w')
    fd.writelines(new_code or code)
    fd.close()
# end def mk_test_file


class TestLoadMowfile(unittest.TestCase):
    def setUp(self):
        pass
    # end def setUp

    def tearDown(self):
        pass
    # end def tearDown

    
    def test_no_file(self):
        self.assertRaises(RuntimeError, mow.loadMowfile, tempfile.tempdir)
    # end def test_no_file

    def test_load_mowfile(self):
        dirname = tempfile.mkdtemp()
        
        for filename in mow.MOW_FILE_NAMES[:2]:
            testfile = os.path.join(dirname, filename)
            mk_mowfile(testfile)
            mod = mow.loadMowfile(dirname)
            self.assertNotEqual(None, mod)
            os.unlink(testfile)
            del mod
        # end for
        os.rmdir(dirname)
    # end def test_load_mowfile

    def test_load_mowfile_py(self):
        dirname = tempfile.mkdtemp()
        
        testfile = os.path.join(dirname, 'mowfile.py')
        mk_mowfile(testfile)
        mod = mow.loadMowfile(dirname)
        self.assertNotEqual(None, mod)
        #os.unlink(testfile)
        del mod
        #os.rmdir(dirname)
    # end def test_load_mowfile_py
# end class TestLoadMowfile

class TestTask(unittest.TestCase):
    def setUp(self):
        mow._tasks = {}
    # end def 

    def test_task_added(self):
        @mow.task('test')
        def test_task(*arg, **kwargs):
            pass
        # end def test_task
        self.assertEquals(test_task, mow._tasks['test'])
    # end def test_task_added

    def test_task_name(self):
        @mow.task('test')
        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test_task._name, 'test')
        self.assertTrue('test' in mow._tasks)
    # end def test_task_name

    def test_task_function_name(self):
        @mow.task()
        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test_task._name, 'test_task')
        self.assertTrue('test_task' in mow._tasks)
    # end def test_task_function_name

    def test_task_function_namespace(self):
        @mow.task()
        def test__task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test__task._name, 'test:task')
        self.assertTrue('test:task' in mow._tasks)
    # end def test_task_function_namespace

    def test_task_override_internal_task(self):
        dec = mow.task('list')

        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertRaises(RuntimeError, dec, test_task)
    # end def test_task_override_internal_task

    def test_task_author(self):
        @mow.task('test', author='brandonvfx')
        def test_task(*arg, **kwargs):
            pass
        # end def test_task                                                        

        self.assertEquals(test_task._author, 'brandonvfx')
    # end def test_task_author

    def test_task_version(self):
        @mow.task('test', version=(1,0,0))
        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test_task._version, (1,0,0))
    # end def test_task_version

    def test_task_description(self):
        @mow.task('test')
        def test_task(*arg, **kwargs):
            """DESCRIPTION"""
            pass
        # end def test_task

        self.assertEquals(test_task._description, "DESCRIPTION")
    # end def test_task_description

    def test_task_usage(self):
        @mow.task('test', usage='%prog %name usage')
        def test_task(*arg, **kwargs):
            """DESCRIPTION"""
            pass
        # end def test_task

        self.assertEquals(test_task._usage, 'mow test usage')
    # end def test_task_usage
# end class TestTask

class TestParseArgs(unittest.TestCase):
    def test_args(self):
        args = ['arg1', 'arg2']
        self.assertEquals((['arg1', 'arg2'], {}), mow.parseArgs(args))
    # end def test_args
        
    def test_kwargs(self):
        args = ['arg1', '--test=1']
        self.assertEquals((['arg1'], {'test': '1'}), mow.parseArgs(args))
    # end def test_kwargs
        
    def test_kwargs_flag(self):
        args = ['arg1', '--test=1', '--dry-run']
        self.assertEquals(
            (['arg1'], {'test':'1', 'dry_run':True}), mow.parseArgs(args)
        )
    # end def test_kwargs_flag
# end class TestParseArgs

class TestMain(unittest.TestCase):
    def test_missing_Mowfile(self):
        args = ['list', '-C', tempfile.tempdir]
        self.assertEquals(1, mow.main(args))
    # def main test_argparse
        
    def test_bad_Mowfile(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        code = [
            'import mow\n', '\n', "@mow.task('test:task')\n", 
            'def test_task():\n','    print "hello\n'
        ]
        mk_mowfile(testfile, code)
        args = ['list', '-C', dirname]
        self.assertEquals(1, mow.main(args))
        os.unlink(testfile)
        os.rmdir(dirname)
    # end def test_bad_Mowfile

    def test_missing_task(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        mk_mowfile(testfile)
        args = ['no_task', '-C', dirname]
        self.assertEquals(1, mow.main(args))
        os.unlink(testfile)
        os.rmdir(dirname)
    # end def test_missing_task

    def test_task_error(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        code = [
            'import mow\n', '\n', "@mow.task('test:task')\n", 
            'def test_task():\n','    raise RuntimeError("Error")\n'
        ]
        mk_mowfile(testfile, code)
        args = ['test:task', '-C', dirname]
        self.assertEquals(1, mow.main(args))
        os.unlink(testfile)
        os.rmdir(dirname)
    # end def test_task_error

    def test_valid_task(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        mk_mowfile(testfile)
        args = ['testing', '-C', dirname]
        self.assertEquals(0, mow.main(args))
        os.unlink(testfile)
        os.rmdir(dirname)
    # end def test_valid_task

    def test_valid_internal_task(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        mk_mowfile(testfile)
        args = ['list', '-C', dirname]
        self.assertEquals(0, mow.main(args))
        os.unlink(testfile)
        os.rmdir(dirname)
    # end def test_valid_internal_task
# end class TestMain

        
if __name__ == '__main__':
    unittest.main()
