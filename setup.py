from setuptools import setup, find_packages
from pathlib import Path


BASE_DIR = Path(__file__).parent
README_DIR = BASE_DIR / 'readme.md'
REQUIREMENTS_DIR = BASE_DIR / 'requirements.txt'

long_description = README_DIR.read_text()
requirements = [line for line in REQUIREMENTS_DIR.read_text().split('\n') if line and not line.startswith('#')]


setup(
    name='scraperai',
    version='0.0.1',
    description='Auto-parsing library for Python',
    url='https://github.com/iakov-kaiumov/scraperai',
    author='Iakov Kaiumov',
    author_email='kaiumov.iag@phystech.edu',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT License',
    packages=find_packages(),
    package_dir={'scraperai': 'scraperai'},
    install_requires=requirements
)
