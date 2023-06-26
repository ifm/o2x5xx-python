from setuptools import setup, find_packages

# Workaround for issue
# https://bugs.python.org/issue15881
try:
    import multiprocessing
except ImportError:
    pass

setup(name='o2x5xx',
      version='0.2',
      description='A Python library for ifm O2x5xx (O2D5xx / O2I5xx) devices',
      author='Michael Gann',
      author_email='support.sy@ifm.com',
      license='MIT',
      packages=['o2x5xx'],
      package_dir={'o2x5xx': 'source'},
      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=False)
