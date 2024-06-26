from setuptools import setup, find_packages
from pathlib import Path


BASE_DIR = Path(__file__).parent
README_DIR = BASE_DIR / 'readme.md'
REQUIREMENTS_DIR = BASE_DIR / 'requirements.txt'

long_description = README_DIR.read_text()
requirements = [line for line in REQUIREMENTS_DIR.read_text().split('\n') if line and not line.startswith('#')]


setup(
    name='scraperai',
    version='0.0.3',
    description='ScraperAI is an open-source, AI-powered tool designed to simplify web scraping for users of all skill levels.',
    url='https://github.com/scraperai/scraperai',
    author='Iakov Kaiumov',
    author_email='help@scraper-ai.com',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPL-3.0 license',
    packages=find_packages(),
    package_dir={'scraperai': 'scraperai'},
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'scraperai = scraperai.cli.app:main',
        ],
    },
)
