import os
import sys
import StringIO
import tempfile
import unittest

sys.path.insert(0, '..')

import mow


def mk_mowfile(file_path):
    code = [
        'import mow\n', '\n', "@mow.task('test:task')\n", 
        'def test_task():\n','    print "hello"\n'
    ]
    fd = open(file_path, 'w')
    fd.writelines(code)
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
        self.assertRaises(RuntimeError, mow.loadMowfile)
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
        mow.tasks = {}
    # end def 

    def test_task_added(self):
        @mow.task('test:test')
        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test_task, mow.tasks['test:test'])
    # end def test_task_added

    def test_task_name(self):
        @mow.task('test:test')
        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test_task._name, 'test:test')
    # end def test_task_name

    def test_task_name(self):
        @mow.task()
        def test__task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test__task._name, 'test:task')
    # end def test_task_name

    def test_task_no_namepsace(self):
        dec = mow.task('test')

        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertRaises(RuntimeError, dec, test_task)
    # end def test_task_name

    def test_task_author(self):
        @mow.task('test:test', author='brandonvfx')
        def test_task(*arg, **kwargs):
            pass
        # end def test_task                                                        

        self.assertEquals(test_task._author, 'brandonvfx')
    # end def test_task_author

    def test_task_version(self):
        @mow.task('test:test', version=(1,0,0))
        def test_task(*arg, **kwargs):
            pass
        # end def test_task

        self.assertEquals(test_task._version, (1,0,0))
    # end def test_task_version

    def test_task_description(self):
        @mow.task('test:test')
        def test_task(*arg, **kwargs):
            """DESCRIPTION"""
            pass
        # end def test_task

        self.assertEquals(test_task._description, "DESCRIPTION")
    # end def test_task_description

    def test_task_help(self):
        @mow.task('test:test', help='help')
        def test_task(*arg, **kwargs):
            """DESCRIPTION"""
            pass
        # end def test_task

        self.assertEquals(test_task._help, 'help')
    # end def test_task_help
# end class TestTask

if __name__ == '__main__':
    unittest.main()
