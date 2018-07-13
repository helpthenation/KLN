.. image:: https://img.shields.io/badge/licence-LGPL--3-blue.svg
    :alt: License: LGPL-3

Stock Forecast
==============

.. contents::

This module add a way to generate forecasting from the product demand.

**Features**:

- Integrate forecasting with products. Add button ``Forecasting`` in the
  product form view and add product field to the forecast record.
- Add product and product template fields to the Forecast model to be used as
  a informative fields to filter the forecast.
- Add wizard at ``Reporting > Warehouse > Stock Demand`` to calculate demand
  for a product in a specific location. Also can have a date margin to extract
  demand only in a certain group (required Forecast Manager permission).
- Add demo data so you can check how the product demand forecast works. You
  can go to ``Settings > Technical > Forecasting > Forecast`` and select the
  forecast with the prefix ``(ST Test 01)``.
- NOTE: A internal move is considered a demand for a location.

Installation
============

To install this module, you need to:

- Not special pre-installation is required, just install as a regular odoo
  module:

  - Download this module from `Vauxoo/forecast
    <https://github.com/vauxoo/forecast>`_
  - Add the repository folder into your odoo addons-path.
  - Go to ``Settings > Module list`` search for the current name and click in
    ``Install`` button.

Configuration
=============

To configure this module, you need to:

* There is not special configuration for this module.

Usage
=====

To use this module, you need to:

* Go to a ``Product`` form view and click on the ``Forecasting``
  button at the top right of the form. There you can check or create a new
  forecasting for you selected product product.

  .. image:: product_button_forcast.png
     :alt: Forecasting button at the Product Form View

* Once in the forecast form view you can check that is associated to what
  product in the section ``Done for product``.

  .. image:: forecast_buttons.png
     :alt: Forecast Buttons

**Demand Forecast**

A demand forecast is set by the way that the forecast rule is configured. This
kind of rule need to the linked to a filter that have at least next elements
at domain:

- A product, group of products or product category.
- A range of dates where the data will be extract.
- A location you want to review.


Also the filter need to have the context required forecast keys
``['forecast_order', 'forecast_value']``. Optionally can use the
``forecast_step`` key in the filter context to indicate that you want to fill
the empty demand dates with 0.0 values and a ``group_by`` key to group the
data by a date/datetime. You can use the syntax ``'group_by':
[datefield:period]``.  The ``period`` and the ``forecast_step`` can
be one of the next options: ``['day', 'week', 'month', 'year']``

**NOTE: For more information about how does the forecasting rules works you
can find out at Forecasting Rules module description**

The Demand Forecast Rule is related to the ``stock.history`` model. This last
one holds the information about the product demand. To calculate the product
demand you can go to ``Reporting > Warehouse > Stock Demand`` wizard and
generate a query of the demand for a specific product / location. In the
``Stock Demand`` wizard there is an option (a check field) that let you
auto-generate a filter ready to be use in a forecast rule. The generate filter
will have this name by default ``Stock Demand for {product} in {location}
(From {date_from} to {date_to}``

*NOTE*: You can run the - ``Reporting > Warehouse > Stock Valuation`` wizard
and generate the demand for all the products / locations in your system.
**WARNING: This could take a lot of time if you have a database with a lot of
products and movements. We highly recommend to generate the demand you need
using the Stock Demand wizard**.

**Forecast Rules Examples**

If you install this module using data demo you can find examples of some
demand forecast rules at ``Settings > Technical Features > Forecasting >
Forecasting Rules`` menu that you can copy and reuse for your purpose.

- You can extract a demand for a product. All the operations for a range of
  date. Check ``(SFD01) 2015 Demand for iMac with Retina 5K display Product in
  WH/Stock until 2015-09-29``.
- You can extract a demand for a product group by month ``(SFD02) 2015 Demand
  for iPad Mini 4 in WH/Stock until 2015-09-29 (Group by Month)``.
- A demand for a new product using the data of the replaced product in
  ``(SFD03) 2015 Demand for New Product S76 Kudu Pro in WH/Stock until
  2015-09-29``.
- The demand of the last 2 months group by week. The last 2 months not taking
  into account the current one ``(SFD04) Last 2 months Demand for Gazelle Pro
  in WH/Stock at date 2015-09-29 (Group by Week)``.
- The demand of the last month for a product group by day. The last month not
  taking into account the current one ``(SFD05) Last month Demand for iPod
  Touch in WH/Stock at date 2015-09-29 (Group by day)``.
- The demand for a product category ``(SFD06) 2015 Computers Category Demand
  in WH/Stock until 2015-09-29 (Group by Month)``.
- Last N days demand group by day. Look example ``(SFD07) Last 14 days Demand
  for iPod Touch Product in WH/Stock at date 2015-09-29 (Group by day)``

.. image:: forecast_examples.png

Known issues / Roadmap
======================

Bug Tracker
===========

Bugs are tracked on
`GitHub Issues <https://github.com/Vauxoo/forecast/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and
welcomed feedback
`here <https://github.com/Vauxoo/forecast/issues/new?body=module:%20
stock_forecast%0Aversion:%20
8.0.1.1.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_

TODO
====

- Maybe the display_name field and compute method can be defined in the
  forecasting_smoothing_techniques module and overwrite in every forecast
  module.
- Update this module description and screenshots.
- When adding a forecasting rule for a product category let to also search
  inside its children categories.

Credits
=======

**Contributors**

* Nhomar Hernandez <nhomar@vauxoo.com> (Planner/Auditor)
* Katherine Zaoral <kathy@vauxoo.com> (Developer)

Maintainer
==========

.. image:: https://s3.amazonaws.com/s3.vauxoo.com/description_logo.png
   :alt: Vauxoo
   :target: https://www.vauxoo.com
   :width: 200

This module is maintained by the Vauxoo.

To contribute to this module, please visit https://www.vauxoo.com.
