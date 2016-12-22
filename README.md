master: [![Build Status](https://travis-ci.org/mkorman9/framepy.svg?branch=master)](https://travis-ci.org/mkorman9/framepy),
[![Code Climate](https://codeclimate.com/github/mkorman9/framepy/badges/gpa.svg)](https://codeclimate.com/github/mkorman9/framepy),
[![Test Coverage](https://codeclimate.com/github/mkorman9/framepy/badges/coverage.svg)](https://codeclimate.com/github/mkorman9/framepy/coverage)
release: [![Build Status](https://travis-ci.org/mkorman9/framepy.svg?branch=release)](https://travis-ci.org/mkorman9/framepy)

### Description
Simple Python 3 framework for web applications. It supports:
* Spring-like dependency injection using decorators
* REST APIs exposing with underlying CherryPy framework
* Automatic payloads validation and mapping
* ORM with underlying SQLAlchemy
* AMQP messaging with pika
* Eureka service discovery and registration
* Redis
* REST client with failover
* Modular architecture

### Branching model
All changes and pull requests should be raised against *master* branch. Merging to *release* is done through internal pull request. Changes made in *release* are automatically deployed to PyPI repository.
