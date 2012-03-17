try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='Mow',
    version='0.1.0',
    author='Brandon Ashworth',
    author_email='brandon@brandonashworth.com',
    py_modules=['mow'],
    scripts=['bin/mow'],
    url='https://github.com/brandonvfx/mow',
    license='LICENSE.txt',
    description='Simple tool/framework for automating tasks.',
    long_description='',
    install_requires=['argparse'],
)
