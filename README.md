ecoControl
========
[![Build Status](https://travis-ci.org/SEC-i/ecoControl.svg?branch=master)](https://travis-ci.org/SEC-i/ecoControl)
[![Documentation](https://readthedocs.org/projects/ecocontrol/badge/?version=latest)](https://ecocontrol.readthedocs.org/)
[![Dependency Status](https://gemnasium.com/SEC-i/ecoControl.svg)](https://gemnasium.com/SEC-i/ecoControl)
[![Code Climate](https://codeclimate.com/github/SEC-i/ecoControl.png)](https://codeclimate.com/github/SEC-i/ecoControl)
[![Coverage Status](https://coveralls.io/repos/SEC-i/ecoControl/badge.png)](https://coveralls.io/r/SEC-i/ecoControl)
[![License](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Switch Language](http://img.shields.io/badge/lang-en--de-brightgreen.svg)](https://github.com/SEC-i/ecoControl/tree/docs-de)

What is ecoControl?
-------------------
**ecoControl** is a prototype that demonstrates how heterogeneous energy systems can be optimized in residential buildings. For this reason, **ecoControl** aims to provide a unifying programming interface as well as suitable forecasts. It makes it possible to execute, develop and share optimization algorithms which can be based on those forecasts.  
However, **ecoControl** currently supports only a few energy systems such as cogeneration units, peak load boilers and heat storages. Since it is released under the [MIT license](http://opensource.org/licenses/MIT), it can easily be extended to support more energy systems by anyone who can write Python code.


Getting Started
--------------
Install [PostgreSQL](http://www.postgresql.org/) 9.3 or later:
```bash
$ sudo apt-get update
$ sudo apt-get install postgresql-9.3 postgresql-contrib-9.3
```
Install all Python dependencies and download all Javascript dependencies:
```bash
$ cd ecoControl/
$ pip install requirements.txt
$ bower install
```
Creates the database tables for **ecoControl**:
```bash
$ python manage.py syncdb
```
Start a lightweight development web server on the local machine:
```bash
$ python manage.py runserver
```
Open [http://localhost:8000/](http://localhost:8000/) in your browser and start **ecoControl**.

If you want to deploy **ecoControl** and use it in production, please read the [development section](http://ecocontrol.readthedocs.org/en/latest/getting_started.html#how-to-deploy-ecocontrol) in the [documentation](http://ecocontrol.readthedocs.org/).


Documentation
-------------
A documentation is available at: https://ecocontrol.readthedocs.org/


Join the Community
------------------
If you are interested in supporting this project, feel free to join the [Smart Energy Control Initiative](http://www.sec-i.org/).


Credits
-------
**ecoControl** was developed by [Eva-Maria Herbst](https://github.com/samifalcon), [Fabian Maschler](https://github.com/maschler), [Fabio Niephaus](https://github.com/fniephaus), [Max Reimann](https://github.com/MaxReimann) and [Julia Steier](https://github.com/steier) during a bachelor's project at [Hasso Plattner Institute](http://www.hpi.de/) in Potsdam. They were supported by [Tim Felgentreff](https://github.com/timfel), [Jens Lincke](https://github.com/JensLincke) and [Marcel Taeumel](https://github.com/marceltaeumel) from the [Software Architecture Group](http://www.hpi.uni-potsdam.de/hirschfeld/) led by [Prof. Hirschfeld](http://www.hirschfeld.org/).

License
-------
**ecoControl** is open-source and licensed under the [MIT license](http://opensource.org/licenses/MIT).
