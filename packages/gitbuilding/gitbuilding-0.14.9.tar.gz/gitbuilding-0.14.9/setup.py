'''Setup for the module'''

__author__ = 'Julian Stirling'
__version__ = '0.14.9'

import sys
from os import path
import glob
from setuptools import setup, find_packages

def install():
    '''The installer'''

    if sys.version_info[0] == 2:
        sys.exit("Sorry, Python 2 is not supported")

    #Globbing all of the static files and then removing `gitbuilding/` from the start
    package_data_location = glob.glob('gitbuilding/static/**/*', recursive=True)
    package_data_location = [package[12:] for package in package_data_location]
    licenses = glob.glob('gitbuilding/licenses/*', recursive=True)
    for lic in licenses:
        package_data_location.append(lic[12:])
    templates = glob.glob('gitbuilding/templates/*', recursive=True)
    for template in templates:
        package_data_location.append(template[12:])

    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, 'README.md'), encoding='utf-8') as file_id:
        long_description = file_id.read()
    short_description = ('For documenting hardware projects with minimal effort,'
                         'so you can stop writing and GitBuilding.')

    setup(name='gitbuilding',
          version=__version__,
          license="GPLv3",
          description=short_description,
          long_description=long_description,
          long_description_content_type='text/markdown',
          author=__author__,
          author_email='julian@julianstirling.co.uk',
          packages=find_packages(),
          package_data={'gitbuilding': package_data_location},
          keywords=['Documentation', 'Hardware'],
          zip_safe=False,
          url='https://gitbuilding.io/',
          project_urls={"Bug Tracker": "https://gitlab.com/gitbuilding/gitbuilding/issues",
                        "Source Code": "https://gitlab.com/gitbuilding/gitbuilding"},
          classifiers=['Development Status :: 5 - Production/Stable',
                       'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                       'Programming Language :: Python :: 3.8'],
          install_requires=['argparse',
                            'pyyaml>=5.1',
                            'python-frontmatter',
                            'flask',
                            'flask_cors',
                            'requests',
                            'markdown>=3.2',
                            'latex2mathml',
                            'colorama',
                            'marshmallow>=03.22',
                            'jinja2',
                            'regex>=2022.1.18',
                            'waitress',
                            'defusedxml>=0.7.1',
                            'pygments>=2.14',
                            'pathspec>=0.11',
                            'watchdog>=3.0',
                            'exsource-tools==0.0.6',
                            'weasyprint>=60.1'],
          extras_require={'gui': ['PyQt5',
                                  'PyQtWebEngine'],
                          'dev': ['pylint<=3.1',
                                  'coverage',
                                  'curlylint',
                                  'pydeps',
                                  'twine']},
          python_requires=">=3.8",
          entry_points={'console_scripts': ['gitbuilding = gitbuilding.__main__:main'],
                        'gui_scripts': ['gitbuilding-gui = gitbuilding.gui:main']})

if __name__ == "__main__":
    install()
