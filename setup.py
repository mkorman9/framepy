from setuptools import setup

setup(
    name='framepy',
    packages=['framepy'],
    version='0.19',
    description='Very simple web application framework with support for AMQP and DI',
    author='Michal Korman',
    author_email='m.korman94@gmail.com',
    url='https://github.com/mkorman9/framepy',
    download_url='https://github.com/mkorman9/framepy/tarball/0.18',
    keywords=['web', 'framework', 'amqp', 'di', 'db'],
    classifiers=[],
    install_requires=['CherryPy', 'PyMySQL', 'SQLAlchemy', 'pika'],
    tests_require=['unittest2', 'mock']
)
