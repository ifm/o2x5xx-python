from setuptools import setup
# Workaround for issue
# https://bugs.python.org/issue15881
try:
    import multiprocessing
except ImportError:
    pass


def read_requires():
    with open("requirements.txt", "r") as r:
        requires = r.readlines()
    return [r.strip() for r in requires]


setup(
    name='o2x5xx',
    version='0.3.2-beta',
    description='A Python library for ifm O2x5xx (O2D5xx / O2I5xx) devices',
    author='Michael Gann',
    author_email='support.efector.object-ident@ifm.com',
    license='MIT',
    packages=['o2x5xx', 'o2x5xx.device', 'o2x5xx.pcic', 'o2x5xx.rpc', 'o2x5xx.static'],
    package_dir={'o2x5xx': './source'},
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False,
    install_requires=read_requires()
    )
