import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = 'ldsorg'
DESCRIPTION = 'Access LDS.org unit information'
URL = 'https://github.com/brian-petersen/ldsorg-python'
EMAIL = 'spambrianp@gmail.com'
AUTHOR = 'Brian Petersen'
REQUIRES_PYTHON = '>=3.7.0'
VERSION = None

# What packages are required for this module to be executed?
REQUIRED = [
    'requests',
]

# What packages are optional?
EXTRAS = {
    # 'fancy feature': ['django'],
}

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        LONG_DESCRIPTION = '\n' + f.read()
except FileNotFoundError:
    LONG_DESCRIPTION = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
ABOUT = {}
if not VERSION:
    with open(os.path.join(here, NAME, '__version__.py')) as f:
        exec(f.read(), ABOUT)
else:
    ABOUT['__version__'] = VERSION

setup(
    name=NAME,
    version=ABOUT['__version__'],
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    py_modules=[NAME],
    # entry_points={
    #     'console_scripts': ['mycli=mymodule:cli'],
    # },
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True,
    license='MIT',
    classifiers=[],
)
