.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Forecasting Rules
=================

This module extend the forecasting functionality by adding a new model named
``Forecast Rule`` that it is a bridge to fulfill the forecast data with odoo
data.

The ``Forecast Rule`` will give you a way to manage, group and review same
data from different perspective: Is the search engine to extract odoo data and
reused as forecast data. You can review the demo data of this module
(the ones with prefix ``FRDXX``).

Is expected in a future that this module will be the one that integrate the
forecasting results with the other odoo records that extract data from the
forecast.

Installation
============

To install this module, you need to:

- Install python package used to calculate the forecasting: ``pandas`` and
  ``numexpr``. You can install them manually ``sudo pip install package_name``
  or you can use this repository ``requirement.txt`` field with the command
  ``sudo pip install -r requirements.txt``.
- Install the odoo module as a regular module:

  - Download this module from `Vauxoo/forecas <https://github.com/vauxoo/forecast>`_ repository.
  - Add the repository folder into your odoo addons-path and reload you odoo
    server.
  - Go to ``Settings > Module list`` search for the current name and click
    ``Install`` button.

Configuration
=============

You can find the Forecast Rules menu at ``Settings > Technical > Forecasting >
Forecasting Rules``.

.. image:: forecast_rule_menu.png
   :alt: Forecast Rule Menu

To access to the ``Forecast Rules`` you need to at least have Forecasting
basic permissions. To edit the Forecasting Rules you need to active a
``Forecast Manager`` permissions in the Forecasting category.

.. image:: forecast_rule_group.png
   :alt: Forecast Rule Group

Usage
=====

* This module let to determinate explicitly the way that the forecast data is
  filled. In the forecast form view you can see two new mutually exclusive
  fields:

  - ``Use Manual Data``: Forecast data is manually introduce by the user.
    This is possible by checking to True the new boolean field. To fill the
    forecast data just go to the ``List of values`` button and add/edit every
    forecast value.

    .. image:: forecast_form_manual.png
       :alt: Use Manual Forecast Data

  - ``Forecast Rule``: When the ``Use Manual Data`` is unset then the
    ``Forecast Rule`` field is shown. This last one give the parameters to
    extract odoo data. After add the rule record just click over the new
    button named ``Fill Values`` that will make the process to update the
    forecast data.

    .. image:: forecast_form_rule.png
       :alt: Forecast using a Forecast Rule

**How does the forecast rules works**

You need to define the odoo model where the
data will be extract and link an ``ir filter`` to indicate the context and
domain used to extract the data.

.. image:: forecast_rule_form.png
   :alt: Forecast Rule

The context will need two required keys ``['forecast_order',
'forecast_value']``: these keys will be used to know what float field and what
order the data will be extract.

A third key can be passed named ``forecast_step`` that is used only when the
``forecast_order`` is a date or datetime field. This parameter will fill the
empty spaces of a forecast for those days, weeks, months, or years were there
is not data demo to the forecast but the group of data belongs to a date range
domain.

Also you can used ``'group_by'`` key in your context to group the return data,
but only one group_by element.

.. image:: forecast_ir_filter.png
   :alt: Forecast Filter Requirements

**Note:** *You can review the demo data to understand better the forecast
rules.*

Known issues / Roadmap
======================

* There is not known issues.

TODO
====

- Add a way to manage multiple group_by elements in the Forecast Filter.
- Separate the context of validate the ir.filter into a new generic module.
- Change the forecasting.rule model to forecast.rule.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/Vauxoo/forecast/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/Vauxoo/forecast/issues/new?body=module:%20{forecasting_rules}%0Aversion:%20{8.0.1.0.0}%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

Credits
=======

**Contributors**

* Nhomar Hernandez <nhomar@vauxoo.com> (Planner/Auditor)
* Katherine Zaoral <kathy@vauxoo.com> (Planner/Developer)

Maintainer
----------

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by the Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
