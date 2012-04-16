try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Mow',
    version='0.3.1',
    author='Brandon Ashworth',
    author_email='brandon@brandonashworth.com',
    py_modules=['mow'],
    entry_points = {
        'console_scripts': [
            'mow = mow:main'
        ]
    },
    url='https://github.com/brandonvfx/mow',
    license='LICENSE.txt',
    description='Simple tool/framework for automating tasks.',
    long_description='Mow is a lightweight Makefile/Rakefile alternative. '\
                     'It allows developers to turn python functions into a command line tools',
    install_requires=['argparse'],
)
