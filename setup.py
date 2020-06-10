# type: ignore
from pathlib import Path
from setuptools import setup

CWD = Path(__file__).parent
README = (CWD / 'README.md').read_text()

setup(
    name='pyku',
    version='1.0.0',
    description='CLI for helping with Roku/brightscript development.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/CCecilia/PyKu',
    author='Christian Cecilia',
    author_email='christian.cecilia1@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8'
        'Topic :: Software Development'
    ],
    packages=['pyku'],
    include_package_data=True,
    install_requires=[
        'click'
    ],
    entry_points={
        'console_scripts': [
            'pyku=pyku.__main__.cli'
        ]
    }
)
