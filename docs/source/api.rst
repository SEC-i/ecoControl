.. index:: API

:tocdepth: 3

========================
REST API Documentation
========================
The ecoControl server communicates through a REST-API only.


List of All API End Points
---------------------------

===================================   ===========================================
API End Point                         Description
===================================   ===========================================
**General**
api/                                  :ref:`api`
api/export/                           :ref:`api_export`
api/login/                            :ref:`api_login`
api/logout/                           :ref:`api_logout`
api/notifications/                    :ref:`api_notifications`
api/sensors/                          :ref:`api_sensors`
api/settings/                         :ref:`api_settings`
api/status/                           :ref:`api_status`
**Technician**                        
api/configure/                        :ref:`api_configure`
api/data/(monthly|yearly)/            :ref:`api_data`
api/forecast/                         :ref:`api_forecast`
api/forward/                          :ref:`api_forward`
api/live/                             :ref:`api_live`
api/settings/tunable/                 :ref:`api_tunables`
api/snippets/                         :ref:`api_snippets`
api/code/                             :ref:`api_code`
api/start/                            :ref:`api_start`
api/statistics/(monthly/)             :ref:`api_statistics`
api/thresholds/                       :ref:`api_thresholds`
api/automoptimize/                    :ref:`api_auto_optimization`
**Manager**                           
api/avgs/                             :ref:`api_avgs`
api/balance/total/(latest/)           :ref:`api_balances`
api/history/                          :ref:`api_history`
api/loads/                            :ref:`api_loads`
api/sensor/                           :ref:`api_sensor`
api/sums/                             :ref:`api_sums`
===================================   ===========================================

General 
----------

Bla


.. _api:

Starting point
~~~~~~~~~~~~~~~

.. code-block:: text

    /api

GET
+++++

Returns the current version number

.. code-block:: bash

   GET /api HTTP/1.1

.. code-block:: js

        {
            
        }

.. _api_export:

CSV-Export function
~~~~~~~~~~~~~~~

.. code-block:: text

    /api/export

POST 
++++++

Reflects post data and starts a CSV file download.

==============   ===============
Param            Description
==============   ===============
name             Name of the service 
description      Description of service 
==============   ===============

.. code-block:: text

   POST /api/export

.. code-block:: bash

   curl


.. _api_login:

Login end point
~~~~~~~~~~~~~~~

.. _api_logout:

Logout end point
~~~~~~~~~~~~~~~

.. _api_notifications:

Get notifications list
~~~~~~~~~~~~~~~

.. _api_sensors:

Get sensors list
~~~~~~~~~~~~~~~

.. _api_settings:

Get settings list
~~~~~~~~~~~~~~~

.. _api_status:

Get system status
~~~~~~~~~~~~~~~


Technician
----------

.. _api_configure:

Set configurations
~~~~~~~~~~~~~~~

.. _api_data:

Get sensor data
~~~~~~~~~~~~~~~

.. _api_forecast:

Get forecast
~~~~~~~~~~~~~~~

.. _api_forward:

forward
~~~~~~~~~~~~~~~

.. _api_live:

Get live data
~~~~~~~~~~~~~~~


.. _api_tunables:

Get tunable settings
~~~~~~~~~~~~~~~

.. _api_snippets:

Manage snippets
~~~~~~~~~~~~~~~

.. _api_code:

Manage code
~~~~~~~~~~~~~~~

.. _api_start:

Start system
~~~~~~~~~~~~~~~

.. _api_statistics:

Get statistics
~~~~~~~~~~~~~~~

.. _api_thresholds:

Manage thresholds
~~~~~~~~~~~~~~~

.. _api_auto_optimization:

Manage auto optimization
~~~~~~~~~~~~~~~


Manager
----------

.. _api_avgs:

Get sensor averages
~~~~~~~~~~~~~~~

.. _api_balances:

Get balances
~~~~~~~~~~~~~~~

.. _api_history:

Get history
~~~~~~~~~~~~~~~

.. _api_loads:

Get loads
~~~~~~~~~~~~~~~

.. _api_sensor:

Get sensor details
~~~~~~~~~~~~~~~

.. _api_sums:

Get sensor sums
~~~~~~~~~~~~~~~

