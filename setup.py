from setuptools import setup, find_packages

# Workaround for issue
# https://bugs.python.org/issue15881
try:
    import multiprocessing
except ImportError:
    pass

setup(name='o2x5xx',
      version='0.1',
      description='A Python library for ifm O2D5xx devices',
      author='Michael Gann',
      author_email='support.sy@ifm.com',
      license='MIT',
      packages=['o2x5xx', 'o2x5xx.pcic', 'o2x5xx.static'],
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
