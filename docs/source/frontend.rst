.. index:: Front End

Front End
=========================
The front end has been developed independently from the ecoControl server and communicates exclusively through the REST-API.
It is based on jQuery and Twitter's Bootstrap which provides an easy to use grid system and enables a responsive design.
For all diagrams, the front end is using Highcharts and Highstock. The programming interface is based on Ace.

Structure
-------------
The front end can be found within the /static folder.


+----------------------+-----------------------------------------------------+
| Folder               | Description                                         |
+======================+=====================================================+
| css/                 | Custom style sheets                                 |
+----------------------+-----------------------------------------------------+
| img/                 | All images                                          |
+----------------------+-----------------------------------------------------+
| js/                  | ecoControl specific Javascript code                 |
+----------------------+-----------------------------------------------------+
| js/libs/             | Custom libraries                                    |
+----------------------+-----------------------------------------------------+
| js/mgmt/             | All Javascript code for the management views        |
+----------------------+-----------------------------------------------------+
| js/tech/             | All Javascript code for the technician views        |
+----------------------+-----------------------------------------------------+
| libs/                | Third party libraries                               |
+----------------------+-----------------------------------------------------+
| templates/           | Mustache templates                                  |
+----------------------+-----------------------------------------------------+
| index.html           | This is the starting point                          |
+----------------------+-----------------------------------------------------+



Multi-language Support
-----------------------

The front end is available in English and in German. The language files can be found in /static/js/ and are called lang.en.js and lang.de.js.