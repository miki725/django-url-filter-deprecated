"""
Based entirely on Django's own ``setup.py``.
"""
import os
import sys
from distutils.command.install_data import install_data
from distutils.command.install import INSTALL_SCHEMES
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup  # NOQA

from url_filter import __version__, __author__


class osx_install_data(install_data):
    # On MacOS, the platform-specific lib dir is at:
    #   /System/Library/Framework/Python/.../
    # which is wrong. Python 2.5 supplied with MacOS 10.5 has an Apple-specific
    # fix for this in distutils.command.install_data#306. It fixes install_lib
    # but not install_data, which is why we roll our own install_data class.

    def finalize_options(self):
        # By the time finalize_options is called, install.install_lib is set to
        # the fixed directory, so we set the installdir to install_lib. The
        # install_data class uses ('install_data', 'install_dir') instead.
        self.set_undefined_options('install', ('install_lib', 'install_dir'))
        install_data.finalize_options(self)


if sys.platform == "darwin":
    cmdclasses = {'install_data': osx_install_data}
else:
    cmdclasses = {'install_data': install_data}


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Tell distutils to put the data_files in platform-specific installation
# locations. See here for an explanation:
# http://groups.google.com/group/comp.lang.python/browse_thread/thread/35ec7b2fed36eaec/2105ee4d9e8042cb
for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
extensions_dir = 'url_filter'

for dirpath, dirnames, filenames in os.walk(extensions_dir):
    # Ignore dirnames that start with '.'
    if os.path.basename(dirpath).startswith("."):
        continue
    if '__init__.py' in filenames:
        packages.append('.'.join(fullsplit(dirpath)))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f)
                          for f in filenames]])


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="django-url-filter",
    version=__version__,
    author=__author__,
    author_email="miroslav@miki725.com",
    description=("Generic Django filter system with easy URL interface. "
                 "Useful for APIs such as http://django-rest-framework.org/."),
    long_description = read('README.rst') + read('LICENSE.rst'),
    license = "MIT",
    keywords = "django",
    url = "https://github.com/miki725/django-url-filter",
    packages = packages,
    cmdclass = cmdclasses,
    data_files = data_files,
    install_requires = [
        'django',
        'djangorestframework',
        'django-auxilium==dev',
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        "Topic :: Utilities",
        'Topic :: Internet :: WWW/HTTP',
        "License :: OSI Approved :: MIT License",
    ],
)
