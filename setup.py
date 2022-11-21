from setuptools import setup
from atexit import register
from shutil import rmtree

setup(
                           name = 'demal',
                         author = 'Victor Azzam',
                    description = 'MAL (Meta Attack Language) to JSON decoding library and command-line tool.',
               long_description = open('README.md').read().strip(),
  long_description_content_type = "text/markdown",
                        license = 'MIT',
                            url = 'https://github.com/victorazzam/demal',
                   download_url = "https://github.com/victorazzam/demal/releases",
                        version = '1.2.2',
                python_requires = '>=3.8',
                       packages = ['demal'],
                   entry_points = {
                                    'console_scripts': ['demal = demal.demal:main'],
                                  },
                    classifiers = [
                                    'Development Status :: 5 - Production/Stable',
                                    'Intended Audience :: Information Technology',
                                    'Intended Audience :: Developers',
                                    'License :: OSI Approved :: MIT License',
                                    'Operating System :: Microsoft :: Windows',
                                    'Operating System :: POSIX :: Linux',
                                    'Operating System :: MacOS',
                                    'Programming Language :: Python :: 3.8',
                                    'Programming Language :: Python :: 3.9',
                                    'Programming Language :: Python :: 3.10',
                                    'Programming Language :: Python :: 3.11'
                                 ]
)

# Remove installation residue
register(lambda: [rmtree(x) for x in ('build', 'demal.egg-info')])
