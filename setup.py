from setuptools import setup
from atexit import register
from shutil import rmtree

setup(
                name = 'demal',
             version = '1.2.0',    
         description = 'MAL (Meta Attack Language) to JSON decoding library and command-line tool.',
                 url = 'https://github.com/victorazzam/demal',
              author = 'Victor Azzam',
             license = 'MIT',
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