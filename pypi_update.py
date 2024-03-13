import os
import dotenv

dotenv.load_dotenv('.env')

username = os.getenv('pypi_username')
password = os.getenv('pypi_password')

os.system('python setup.py sdist')
os.system('python setup.py bdist_wheel --universal ')
os.system(f'twine upload --skip-existing dist/* -u {username} -p {password}')
