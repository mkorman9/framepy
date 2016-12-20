from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.readlines()

version = '3.62'

setup(
    name='framepy',
    packages=find_packages(exclude=('tests',)),
    version=version,
    description='Very simple web application framework with support for AMQP and DI',
    author='Michal Korman',
    author_email='m.korman94@gmail.com',
    url='https://github.com/mkorman9/framepy',
    download_url='https://github.com/mkorman9/framepy/tarball/{}'.format(version),
    keywords=['web', 'framework', 'amqp', 'di', 'db'],
    classifiers=[],
    install_requires=[requirement for requirement in requirements if len(requirement) > 0]
)
