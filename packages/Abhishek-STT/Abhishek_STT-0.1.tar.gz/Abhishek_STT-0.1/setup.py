from setuptools import setup, find_packages

setup(
    name='Abhishek_STT',
    version='0.1',
    author='PAL ABHISHEK ',
    author_email= 'palabhishek5710@gmail.com',
    description='This is speech to text package which created by abhishek'
)
packages = find_packages(),
install_requirements = [
    'selenium',
    'webdriver_manager'
]
