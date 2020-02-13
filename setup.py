""" Scripts to pull Tradier Data 


See:
https://github.com/flyrok/lotto_scrape
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

PROJECT_NAME="lotto_scrape"
versionpy=here + "/" + PROJECT_NAME + "/" + "version.py"
exec(open(versionpy).read())
VERSION=__version__
DESCRIPTION="Compute psds using ObsPy"
URL="https://github.com/flyrok/lotto_scrape"
AUTHOR="A Ferris"
EMAIL="aferris@flyrok.org"
CLASSIFIERS=['Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
     'Programming Language :: Python :: 3']
KEYWORDS="lotto yolo yacht"     

INSTALL_REQUIRES = [
    'pathlib',
    'bs4',
    ]


#    packages=find_packages(exclude=['doc','examples']),
setup(
    name=PROJECT_NAME,  # Required
    version=VERSION,  # Required
    description=DESCRIPTION,  # Optional
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url=URL,  # Optional
    author=AUTHOR,  # Optional
    author_email=EMAIL,  # Optional
    classifiers=CLASSIFIERS ,
    keywords=KEYWORDS,  # Optional
    python_requires='>=3.6',
    include_package_data=True,
    packages=find_packages(exclude=['examples','doc']),
    install_requires=INSTALL_REQUIRES,  # Optional
    entry_points={  # Optional
        'console_scripts': [
            'lotto_scrape=lotto_scrape.__main__:main',
        ],
    },
    extras_require={  # Optional
    },
    package_data={ },
    project_urls={  # Optional
        'Source': URL,
    },
)

