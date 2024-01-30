from setuptools import setup

setup(
    name='pymdp',
    version='1.0.1',
    description='mdpr.jp image list',
    author='qmaru',
    url='https://github.com/qmaru/pymdp',
    py_modules=['pymdp'],
    python_requires='>=3.10.0',
    install_requires=['lxml', 'aiohttp'],
)
