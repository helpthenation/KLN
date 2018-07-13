# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

from datetime import datetime

from openerp.tests import common


class TestForecastRule(common.TransactionCase):

    """ Test that the forecast rules defined in demo really are adding the
    correspond values ids
    """

    def setUp(self):
        super(TestForecastRule, self).setUp()
        self.forecast_obj = self.env['forecast']

    def test_01(self):
        """Check SFD01 2015 Demand for iMac with Retina 5K display Product in WH/Stock
          - values length is 87 values.
             - 80 sales
             - 7 internal movements
        """
        forecast = self.forecast_obj.browse(
            self.ref('stock_forecast.forecast_demo_01'))
        self.assertTrue(forecast)
        self.assertEqual(len(forecast.value_ids), 87)

    def test_02(self):
        """Check SFD02 2015 Demand for iPad Mini 4 in WH/Stock (Month)
          - values length is 80 values.
        """
        forecast = self.forecast_obj.browse(
            self.ref('stock_forecast.forecast_demo_02'))
        self.assertTrue(forecast)
        self.assertEqual(len(forecast.value_ids), 9)

    def test_03(self):
        """Check SFD03 2015 Demand for New Product S76 Kudu Pro in WH/Stock
          - values length is 85 values.
             - 80 sales
             - 5 internal movements
        """
        forecast = self.forecast_obj.browse(
            self.ref('stock_forecast.forecast_demo_03'))
        self.assertTrue(forecast)
        self.assertEqual(len(forecast.value_ids), 85)

    def test_04(self):
        """Check SFD04 Last 2 months Demand for Gazelle Pro in WH/Stock (week)
          - values length is 8 values.
        """
        forecast = self.forecast_obj.browse(
            self.ref('stock_forecast.forecast_demo_04'))

        day1 = datetime.strptime('2015-07-01', '%Y-%m-%d')
        day2 = datetime.strptime('2015-08-31', '%Y-%m-%d')
        weeks = (day2.isocalendar()[1] - day1.isocalendar()[1] + 1)

        self.assertEqual(weeks, 10)
        self.assertTrue(forecast)
        self.assertEqual(len(forecast.value_ids), weeks)

    def test_05(self):
        """Check SFD05 Last month Demand for iPod Touch in WH/Stock (day)
          - values length is 31 values.
        """
        forecast = self.forecast_obj.browse(
            self.ref('stock_forecast.forecast_demo_05'))
        self.assertTrue(forecast)
        self.assertEqual(len(forecast.value_ids), 31)

    def test_06(self):
        """Check SFD06 2015 Computers Category Demand in WH/Stock (month)
          - values length is 9 values.
        """
        forecast = self.forecast_obj.browse(
            self.ref('stock_forecast.forecast_demo_06'))
        self.assertTrue(forecast)
        self.assertEqual(len(forecast.value_ids), 9)

    def test_07(self):
        """Check SFD07 Last 14 days Demand for iPod Touch Product in WH/Stock (day)
          - values length is 14 values.
        """
        forecast = self.forecast_obj.browse(
            self.ref('stock_forecast.forecast_demo_07'))
        self.assertTrue(forecast)
        self.assertEqual(len(forecast.value_ids), 14)
