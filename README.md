ecoControl
========
[![Build Status](https://travis-ci.org/SEC-i/ecoControl.svg?branch=master)](https://travis-ci.org/SEC-i/ecoControl)
[![Dokumentation](https://readthedocs.org/projects/ecocontrol/badge/?version=latest)](https://ecocontrol.readthedocs.org/)
[![Dependency Status](https://gemnasium.com/SEC-i/ecoControl.svg)](https://gemnasium.com/SEC-i/ecoControl)
[![Code Climate](https://codeclimate.com/github/SEC-i/ecoControl.png)](https://codeclimate.com/github/SEC-i/ecoControl)
[![Coverage Status](https://coveralls.io/repos/SEC-i/ecoControl/badge.png)](https://coveralls.io/r/SEC-i/ecoControl)
[![Lizenz](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Sprache wechseln](http://img.shields.io/badge/lang-en--de-brightgreen.svg)](https://github.com/SEC-i/ecoControl)

*Obwohl es es eine deutsche Version von ecoControl gibt, findet die Entwicklung überwiegend in Englisch statt. Aus diesem Grund handelt es sich bei dieser Webseite um eine reine Übersetzung.*

Was ist ecoControl?
-------------------
**ecoControl** ist ein Prototype, der demonstrieren soll, wie heterogene Energiesysteme wie Blockheizkraftwerke oder Photovoltaik-Anlagen effizient in Mehrfamilienhäusern betrieben werden können. Dazu stellt **ecoControl** eine einheitliche Programmierschnittstelle sowie geeignete Prognosen zur Verfügung. Es ist möglich, Optimierungsalgorithmen mithilfe von **ecoControl** auszuführen, zu entwickeln und miteinander zu teilen.  
Allerdings unterstützt die Software momentan nur wenige Energiesysteme wie beispielsweise Blockheizkraftwerke, Spitzenlastkessel oder Wärmespeicher. Da sie unter der [MIT Lizenz](http://opensource.org/licenses/MIT) veröffentlich wurde, kann sie von jedem, der Python programmieren kann, um weitere Energiesysteme erweitert werden.


Download
--------
Die aktuellste Version von **ecoControl** können Sie jederzeit unter folgendem Link downloaden:
https://github.com/SEC-i/ecoControl/archive/master.zip


Erste Schritte
--------------
Installieren Sie [PostgreSQL](http://www.postgresql.org/) 9.3 oder neuer:
```bash
$ sudo apt-get update
$ sudo apt-get install postgresql-9.3 postgresql-contrib-9.3
```
Installieren Sie alle benötigten Python Abhängigkeiten und laden Sie alle Javascript Bibliotheken:
```bash
$ cd ecoControl/
$ pip install requirements.txt
$ bower install
```
Legen Sie die Datenbanktabellen für **ecoControl** an:
```bash
$ python manage.py syncdb
```
Starten Sie einen Webserver lokal auf Ihrem Rechner:
```bash
$ python manage.py runserver
```
Öffnen Sie [http://localhost:8000/](http://localhost:8000/) in Ihrem Browser und starten Sie **ecoControl**.

Informationen wie **ecoControl** in Produktion eingesetzt werden kann, finden Sie im [Einrichtungskapitel](http://ecocontrol.readthedocs.org/en/latest/getting_started.html#how-to-deploy-ecocontrol) der [Dokumentation](http://ecocontrol.readthedocs.org/de/latest/).


Dokumentation
-------------
Eine deutsche Dokumentation findet sich unter: http://ecocontrol.readthedocs.org/de/latest/


Mitmachen
------------------
Wenn Sie dieses Projekt unterstützen wollen, machen Sie bei der [Smart Energy Control Initiative](http://www.sec-i.org/) mit!


Herausgeber
-------
**ecoControl** wurde von [Eva-Maria Herbst](https://github.com/samifalcon), [Fabian Maschler](https://github.com/maschler), [Fabio Niephaus](https://github.com/fniephaus), [Max Reimann](https://github.com/MaxReimann) und [Julia Steier](https://github.com/steier) im Rahmen eines Bachelor-Projekts am [Hasso Plattner Institute](http://www.hpi.de/) in Potsdam entwickelt.  
Unterstützt wurden sie von [Tim Felgentreff](https://github.com/timfel), [Jens Lincke](https://github.com/JensLincke) und [Marcel Taeumel](https://github.com/marceltaeumel) vom Fachgebiet [Software-Architekturen](http://www.hpi.uni-potsdam.de/hirschfeld/) von [Prof. Hirschfeld](http://www.hirschfeld.org/).

Lizenz
-------
**ecoControl** ist open-source und unter der [MIT Lizenz](http://opensource.org/licenses/MIT) veröffentlicht.
