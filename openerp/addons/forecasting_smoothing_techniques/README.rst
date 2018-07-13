.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Forecasting by Smoothing Techniques
===================================

Data collected over time is likely to show some form of random variation.
"Smoothing techniques" can be used to reduce or cancel the effect of these
variations. These techniques, when properly applied, will ``smooth`` out the
random variation in the time series data to reveal any underlying trends that
may exist.

**NOTE**: This module add a calculator to odoo that simulate the application in
`this link <http://home.ubalt.edu/ntsbarsh/Business-stat/otherapplets/ForecaSmo.htm>`_

Installation
============

To install this module, you need to:

- Install python package used to calculate the forecasting: ``pandas`` and
  ``numexpr``. You can install them manually ``sudo pip install package_name``
  or you can use this repository ``requirement.txt`` field with the command
  ``sudo pip install -r requirements.txt``.
- Download this module from `Vauxoo/stock-forecasting <https://github.com/vauxoo/stock-forecasting>`_
- Add the repository folder into your odoo addons-path.
- Go to ``Settings > Module list`` search for the current name and click in
  ``Install`` button.

Configuration
=============

To configure this module, you need to:

* Set the Forecasting permission for your user to be able to use this module
  new features. Go to  ``Settings > Users > Users`` menu and select your user
  from the list view. In the user form view activate the ``Forecasting``
  permission as ``User`` or ``Manager``. Also need to activate the Technical
  Features to see the Forecasting Menu.

  .. image:: forecasting_permission.png
     :alt: Forecasting Permission

.. note:: If you are using a data base with demo data the user ``Admin``
   will be by default a ``Forecast Manager`` and the ``Demo User`` will be a
   ``Forecast User``.

Usage
=====

To use this module, you need to:

* Go to a ``Settings > Technical > Forecasting`` menu. There you will find
  the ``Forecasts`` sub menu that will show you a list view with all the
  Forecast Records. There you just simply can check or create a new
  forecasting.  Forecasting list view have the forecast ``ID`` and ``name``
  for quick identification, forecasting parameters, and some columns with a
  brief result summary.

  .. image:: forecasting_menu.png
     :alt: Forecasting Menu and List View

* When click over a Forecasting record over the ``Create`` button will take
  you to the Forecasting Form View. This view show up at the top the basic
  forecast data and some buttons:

  - ``Reset Details``: Reset the default parameters of the forecasting.
  - ``Clear``: Clear the forecasting incoming data values.
  - ``List of Values``: Go to the list of the forecasting incoming data so
    you can edit them. Also you can see a table with all the forecasting
    results per data point (detail results).

  In the first view of the forecasting form view you can view a graph with
  the results of all the forecasting methods applied over the data you
  submit.

  .. image:: forecast_buttons.png
     :alt: Forecast Buttons

* There is a functionality to help the user to use the forecast model.
  You can hide/show two kinds of help:

  - ``Help``: Show step by step the things to configure to generate the
    forecast.

    .. image:: forecast_help.png
       :alt: Forecast Step by Steph Help

  - ``Mathematical Base Help``: Showing information about how the forecast
    methods works, how to set the parameters and how to make the forecast
    results compare. If you have any doubt there is an explanation about every
    forecasting methods so will be more easy to use.

    .. image:: forecast_complete_form_view.png
       :alt: forecast complete form view

* When editing the forecast values (Click over the ``List of Values`` button)
  you can observe all the values in the table with all the detail forecasting
  results per data point with the mathematical absolute error (MAE).

.. image:: forecast_data_tree_view.png
   :alt: Forecast Data List View

* To edit the list of values just click over the value in the forecasting data
  list view to go to the form view and edit the values. You can edit the
  Sequence and the Value itself indicating in the ``Data Information``
  section. As you can check all the ``Forecasting Results`` for this
  particular point can be also review in the form view, this results fields
  are not editable only readonly.

.. image:: forecast_data_form_view.png
   :alt: Forecasr Data Form View

* If the forecast values are not length enough for calculate the forecast then
  will show at the top of the form a list with the warnings and what to do to
  eliminate then.

.. image:: forecast_data_warning.png
   :alt: Forecast Data Warning

Known issues / Roadmap
======================

* Review problem can not create new forecast records even in the forecast
  groups are correctly set.

TODO
====

- The module name can be change to just forecast or forecasting.
- Add constraint that make that the list of values are consecutive values
  start from 1. If not then the forecast calculus will fail.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Vauxoo/stock-forecasting/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Vauxoo/stock-forecasting/issues/new?body=module:%20{forecasting_smoothing_techniques}%0Aversion:%20{8.0.1.0.0}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

Contributors
------------

* Nhomar Hernandez <nhomar@vauxoo.com> (Planner/Auditor)
* Maria Gabriela Quilarque <gabriela@vauxoo.com> (Planner)
* Katherine Zaoral <kathy@vauxoo.com> (Developer)

Maintainer
----------

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by the Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
