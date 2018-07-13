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

from openerp.tests import common


class TestForecast(common.TransactionCase):

    """ Test that the forecast model set correctly the product and the display
    name.
    """

    def setUp(self):
        super(TestForecast, self).setUp()
        self.forecast_obj = self.env['forecast']
        self.product_obj = self.env['product.product']

        self.product = self.product_obj.browse(
            self.ref('product.product_product_7'))
        self.product_name = self.product.name

    def create_forecast(self, name='UNDEFINED', values=None):
        """Create a forecast record

        Create a forecast record with the specified arguments
        By default assign also the forecast rule.

        :return: the forecast created record set.
        """
        if not values:
            values = {
                'name': '(Test %s)' % name,
            }
        forecast = self.forecast_obj.create(values)
        return forecast

    def test_01(self):
        """Create a Forecast only with name
        """
        forecast = self.create_forecast(name='1')
        self.assertTrue(forecast)

    def test_02(self):
        """Create a forecast from product view automatic set forecast product
        """
        values = {
            'name': 'Unit Test 02',
        }
        forecast = self.forecast_obj.with_context({
            'product_id': self.product.id,
        }).create(values)
        self.assertTrue(forecast)
        self.assertEqual(forecast.product_id, self.product)

    def test_03(self):
        """Forecast Display name with product.

        Result correspond to "product name: forecast name"
        """
        values = {
            'name': 'Unit Test 03',
            'product_id': self.product.id,
        }
        forecast = self.forecast_obj.create(values)
        expected_display_name = ''.join([
            self.product_name, ': ', forecast.name])
        self.assertEqual(forecast.display_name, expected_display_name)

    def test_04(self):
        """Forecast Display name without product

        Result correspond to "name"
        """
        values = {
            'name': 'Unit Test 03',
        }
        forecast = self.forecast_obj.create(values)
        expected_display_name = forecast.name
        self.assertEqual(forecast.display_name, expected_display_name)

    def test_05(self):
        """Forecast Display name without forecast name

        Result correspond to "product: "
        """
        values = {
            'product_id': self.product.id,
        }
        forecast = self.forecast_obj.create(values)
        expected_display_name = ''.join([self.product.name,
                                         ': No Forecast Name'])
        self.assertEqual(forecast.display_name, expected_display_name)
