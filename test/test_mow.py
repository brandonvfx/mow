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
        'def test_task():\n','    print("hello")\n'
    ]
    fd = open(file_path, 'w')
    fd.writelines(new_code or code)
    fd.close()


class TestLoadMowfile(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_no_file(self):
        self.assertRaises(RuntimeError, mow.loadMowfile, tempfile.tempdir)

    def test_load_mowfile(self):
        dirname = tempfile.mkdtemp()
        
        for filename in mow.MOW_FILE_NAMES[:2]:
            testfile = os.path.join(dirname, filename)
            mk_mowfile(testfile)
            mod = mow.loadMowfile(dirname)
            self.assertNotEqual(None, mod)
            os.unlink(testfile)
            if os.path.exists(testfile+'c'):
                os.unlink(testfile+'c')
            del mod
        os.rmdir(dirname)

    def test_load_mowfile_py(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'mowfile.py')
        mk_mowfile(testfile)
        mod = mow.loadMowfile(dirname)
        self.assertNotEqual(None, mod)
        os.unlink(testfile)
        if os.path.exists(testfile+'c'):
            os.unlink(testfile+'c')
        del mod
        os.rmdir(dirname)

class TestTask(unittest.TestCase):
    def setUp(self):
        mow._tasks = {}

    def test_task_added(self):
        @mow.task('test')
        def test_task(*arg, **kwargs):
            pass
        self.assertEquals(test_task, mow._tasks['test'])

    def test_task_name(self):
        @mow.task('test')
        def test_task(*arg, **kwargs):
            pass
        self.assertEquals(test_task._name, 'test')
        self.assertTrue('test' in mow._tasks)

    def test_task_function_name(self):
        @mow.task()
        def test_task(*arg, **kwargs):
            pass
        self.assertEquals(test_task._name, 'test_task')
        self.assertTrue('test_task' in mow._tasks)

    def test_task_function_namespace(self):
        @mow.task()
        def test__task(*arg, **kwargs):
            pass
        self.assertEquals(test__task._name, 'test:task')
        self.assertTrue('test:task' in mow._tasks)

    def test_task_override_internal_task(self):
        dec = mow.task('list')

        def test_task(*arg, **kwargs):
            pass
        self.assertRaises(RuntimeError, dec, test_task)

    def test_task_author(self):
        @mow.task('test', author='brandonvfx')
        def test_task(*arg, **kwargs):
            pass                                                      
        self.assertEquals(test_task._author, 'brandonvfx')

    def test_task_version(self):
        @mow.task('test', version=(1,0,0))
        def test_task(*arg, **kwargs):
            pass
        self.assertEquals(test_task._version, (1,0,0))

    def test_task_description(self):
        @mow.task('test')
        def test_task(*arg, **kwargs):
            """DESCRIPTION"""
            pass
        self.assertEquals(test_task._description, "DESCRIPTION")

    def test_task_usage(self):
        @mow.task('test', usage='%prog %name usage')
        def test_task(*arg, **kwargs):
            """DESCRIPTION"""
            pass
        self.assertEquals(test_task._usage, 'mow test usage')

class TestParseArgs(unittest.TestCase):
    def test_args(self):
        args = ['arg1', 'arg2']
        self.assertEquals((['arg1', 'arg2'], {}), mow.parseArgs(args))

    def test_kwargs(self):
        args = ['arg1', '--test=1']
        self.assertEquals((['arg1'], {'test': '1'}), mow.parseArgs(args))

    def test_kwargs_multi(self):
        args = ['arg1', '--test=1', '--test=2', '--test=3']
        self.assertEquals((['arg1'], {'test': ['1', '2', '3']}), mow.parseArgs(args))
        
    def test_kwargs_flag(self):
        args = ['arg1', '--test=1', '--dry-run']
        self.assertEquals(
            (['arg1'], {'test':'1', 'dry_run':True}), mow.parseArgs(args)
        )

class TestMain(unittest.TestCase):
    # TODO: come up with a good way to do this test, now that mow
    #       searches a list of paths.
    # def test_missing_Mowfile(self):
    #     args = ['list', '-C', tempfile.tempdir]
    #     self.assertEquals(1, mow.main(args))
        
    def test_bad_Mowfile(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        code = [
            'import mow\n', '\n', "@mow.task('test:task')\n", 
            'def test_task():\n','    print("hello)\n'
        ]
        mk_mowfile(testfile, code)
        args = ['list', '-C', dirname]
        self.assertEquals(1, mow.main(args))
        os.unlink(testfile)
        os.rmdir(dirname)

    def test_missing_task(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        mk_mowfile(testfile)
        args = ['no_task', '-C', dirname]
        self.assertEquals(1, mow.main(args))
        os.unlink(testfile)
        if os.path.exists(testfile+'c'):
            os.unlink(testfile+'c')
        os.listdir(dirname)
        os.rmdir(dirname)

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
        if os.path.exists(testfile+'c'):
            os.unlink(testfile+'c')
        os.rmdir(dirname)

    def test_valid_task(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        mk_mowfile(testfile)
        args = ['testing', '-C', dirname]
        self.assertEquals(0, mow.main(args))
        os.unlink(testfile)
        if os.path.exists(testfile+'c'):
            os.unlink(testfile+'c')
        os.rmdir(dirname)

    def test_valid_internal_task(self):
        dirname = tempfile.mkdtemp()
        testfile = os.path.join(dirname, 'Mowfile')
        mk_mowfile(testfile)
        args = ['list', '-C', dirname]
        self.assertEquals(0, mow.main(args))
        os.unlink(testfile)
        if os.path.exists(testfile+'c'):
            os.unlink(testfile+'c')
        os.rmdir(dirname)

if __name__ == '__main__':
    unittest.main()
