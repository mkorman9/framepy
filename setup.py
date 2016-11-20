from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

setup(
    name='framepy',
    packages=find_packages(exclude=('tests',)),
    version='0.45',
    description='Very simple web application framework with support for AMQP and DI',
    author='Michal Korman',
    author_email='m.korman94@gmail.com',
    url='https://github.com/mkorman9/framepy',
    download_url='https://github.com/mkorman9/framepy/tarball/0.45',
    keywords=['web', 'framework', 'amqp', 'di', 'db'],
    classifiers=[],
    install_requires=[requirement for requirement in requirements if len(requirement) > 0]
)
