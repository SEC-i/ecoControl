ecoControl
========
[![Build Status](http://img.shields.io/travis/SEC-i/ecoControl/master.svg?style=flat-square)](https://travis-ci.org/SEC-i/ecoControl)
[![Documentation](http://img.shields.io/badge/docs-latest-blue.svg?style=flat-square)](https://ecocontrol.readthedocs.org/)
[![Dependency Status](http://img.shields.io/gemnasium/SEC-i/ecoControl.svg?style=flat-square)](https://gemnasium.com/SEC-i/ecoControl)
[![Code Climate](http://img.shields.io/codeclimate/github/SEC-i/ecoControl.svg?style=flat-square)](https://codeclimate.com/github/SEC-i/ecoControl)
[![Coverage Status](http://img.shields.io/coveralls/SEC-i/ecoControl.svg?style=flat-square)](https://coveralls.io/r/SEC-i/ecoControl)
[![License](http://img.shields.io/badge/license-MIT-brightgreen.svg?style=flat-square)](http://opensource.org/licenses/MIT)
[![Switch Language](http://img.shields.io/badge/lang-en--de-brightgreen.svg?style=flat-square)](https://github.com/SEC-i/ecoControl)

*Obwohl es es eine deutsche Version von ecoControl gibt, findet die Entwicklung überwiegend in Englisch statt. Aus diesem Grund handelt es sich bei dieser Webseite um eine reine Übersetzung.*

Was ist ecoControl?
-------------------
**ecoControl** ist ein Prototype, der demonstrieren soll, wie heterogene Energiesysteme wie Blockheizkraftwerke oder Photovoltaik-Anlagen effizient in Mehrfamilienhäusern betrieben werden können. Dazu ermöglicht **ecoControl** das zentrale Einstellen von einzelnen Parametern und stellt eine einheitliche Programmierschnittstelle zur Verfügung. Über diese Schnittstelle ist es möglich, auf geeignete Prognosen zurückzugreifen und Optimierungsalgorithmen zu entwickelt und auszuführen.  
**ecoControl** unterstützt momentan folgende Energiesysteme: Blockheizkraftwerke, Spitzenlastkessel und Wärmespeicher. Da die Software unter der [MIT Lizenz](http://opensource.org/licenses/MIT) veröffentlich wurde, kann sie von jedem, der Python programmieren kann, um weitere Energiesysteme erweitert werden.


Download
--------
Die aktuellste Version von **ecoControl** können Sie jederzeit unter folgendem Link downloaden:  
https://github.com/SEC-i/ecoControl/archive/master.zip


Erste Schritte
--------------

#### ecoControl Autoinstaller für Debian / Ubuntu
Wenn Sie Debian 7.6 oder Ubuntu 14.04 verwenden, können Sie einfach die folgende Zeile im Terminal auführen. Dies wird den Autoinstaller ausführen, der **ecoControl** und alle Softwarevoraussetzungen automatisch einrichtet.
```bash
$ curl -sL https://raw.github.com/SEC-i/ecoControl/master/autoinstaller.sh | bash
```

#### Manuelle Installation
Installieren Sie [pip](https://pypi.python.org/pypi/pip/), [npm](http://nodejs.org/) und [bower](http://bower.io/):
```bash
$ sudo apt-get update
$ sudo apt-get install python-pip npm
$ sudo npm install -g bower
```

Installieren Sie [PostgreSQL](http://www.postgresql.org/) 9.3 oder neuer:
```bash
$ sudo apt-get install postgresql-9.3 postgresql-contrib-9.3
```
*Sollte der letzte Befehl fehlschlagen, lesen Sie bitte nach, wie Sie [PostgreSQL auf Ihrem System installieren können](http://www.postgresql.org/download/).*

Laden und entpacken Sie **ecoControl**:
```bash
$ wget -O ecoControl.zip https://github.com/SEC-i/ecoControl/archive/master.zip
$ unzip ecoControl.zip
$ cd ecoControl/
```

Installieren Sie alle benötigten Python Abhängigkeiten und laden Sie alle Javascript Bibliotheken:
```bash
$ pip install requirements.txt
$ bower install
```

Richten Sie eine Datenbank für **ecoControl** ein:
```bash
$ sudo -u postgres psql -c "CREATE ROLE ecocontrol LOGIN PASSWORD 'sec-i';"
$ sudo -u postgres createdb --owner=ecocontrol ecocontrol
$ python manage.py syncdb
```
*Sie sollten das Standardpasswort aus Sicherheitsgründen ändern. Vergessen Sie nicht, die Änderungen auch in der [settings.py](https://github.com/SEC-i/ecoControl/blob/master/server/settings.py) Datei vorzunehmen.*

Starten Sie einen Webserver lokal auf Ihrem Rechner:
```bash
$ python manage.py runserver
```

Öffnen Sie [http://localhost:8000/](http://localhost:8000/) in Ihrem Browser und starten Sie **ecoControl**.

Informationen wie **ecoControl** in Produktion eingesetzt werden kann, finden Sie im [Einrichtungskapitel](http://ecocontrol.readthedocs.org/en/latest/getting_started.html#how-to-deploy-ecocontrol) der [Dokumentation](http://ecocontrol.readthedocs.org/latest/).


Dokumentation
-------------
Eine englische Dokumentation findet sich unter: http://ecocontrol.readthedocs.org/latest/


Mitmachen
------------------
Wenn Sie dieses Projekt unterstützen wollen, machen Sie bei der [Smart Energy Control Initiative](http://www.sec-i.org/) mit!


Herausgeber
-------
**ecoControl** wurde von [Eva-Maria Herbst](https://github.com/samifalcon), [Fabian Maschler](https://github.com/maschler), [Fabio Niephaus](https://github.com/fniephaus), [Max Reimann](https://github.com/MaxReimann) und [Julia Steier](https://github.com/steier) im Rahmen eines Bachelor-Projekts am [Hasso Plattner Institut](http://www.hpi.de/) in Potsdam entwickelt.
Unterstützt wurden sie von [Carsten Witt](https://github.com/infoprofi) sowie von [Tim Felgentreff](https://github.com/timfel), [Jens Lincke](https://github.com/JensLincke) und [Marcel Taeumel](https://github.com/marceltaeumel) vom Fachgebiet [Software-Architekturen](http://www.hpi.uni-potsdam.de/hirschfeld/) von [Prof. Hirschfeld](http://www.hirschfeld.org/).

Lizenz
-------
**ecoControl** ist open-source und unter der [MIT Lizenz](http://opensource.org/licenses/MIT) veröffentlicht.
