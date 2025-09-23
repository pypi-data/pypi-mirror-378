from setuptools import setup,find_packages

setup(
    name='Mypackage-STT',
    version='0.1',
    author='Budhyadeb Bag',
    author_email='budhya03@gmail.com',
    description='this is speech to text package created by budhyadeb bag'
)
packages = find_packages(),
install_requirement = [
    'selenium',
    'webdriver_manager'
]

