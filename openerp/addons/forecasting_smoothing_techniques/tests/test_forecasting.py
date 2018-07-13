# coding: utf-8
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Katherine Zaoral <kathy@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
#                Gabriela Quilarque <gabriela@vauxoo.com>
############################################################################

import csv
import logging

from openerp import _, tools
from openerp.exceptions import AccessError, ValidationError
from openerp.tests import common
from openerp.tools import mute_logger

_logger = logging.getLogger(__name__)

try:
    import pandas as pd
except ImportError:
    _logger.debug('Cannot `import panda`.')


class TestForecast(common.TransactionCase):

    """ Test that the forecasting smoothing model is working propertly.
    """

    maxDiff = None

    def setUp(self):
        super(TestForecast, self).setUp()
        self.forecast_obj = self.env['forecast']
        self.fdata_obj = self.env['forecast.data']

    def compare(self, expected, real):
        """ Compare the correct result with the real result. Print logger with
        error tag. Raise an assert if there different indicating with field
        is the one different, the actual value, the expected value and the
        differencial between. In the case of the data values results per
        point indicate the sequence number of the problematic point.

        :expected: dictionary with the expected values
        :real: dictionary with the real forecasting values
        """
        elist = list()
        keys = expected.keys()
        keys.sort()
        for key in keys:
            vreal = real.get(key)
            vexpected = expected.get(key)

            if isinstance(vexpected, (float,)):
                if not self.forecast_obj.almost_equal(vreal, vexpected):
                    elist.append(self.get_msg_error(
                        key, vreal, vexpected))
            elif isinstance(vexpected, (pd.DataFrame,)):

                vexpected = vexpected.to_dict(orient='dict')

                # Get real result of the values
                fields_to_compare = vexpected.keys() + ['sequence']
                value_ids = self.fdata_obj.browse(vreal).read(
                    fields_to_compare)
                for item in value_ids:
                    item.pop('id')

                # Transform to DataFrame object to make it easy to manage.
                vreal = pd.DataFrame(value_ids)
                vreal.set_index('sequence', inplace=True)
                vreal = vreal.reindex_axis(sorted(vreal.columns), axis=1)

                # Compare actual and expected values (Transform to dict)
                vreal = vreal.to_dict(orient='dict')
                for (fname, values) in vreal.iteritems():
                    for val in values:
                        actual = vreal.get(fname).get(val)
                        wanted = vexpected.get(fname).get(val)
                        if not self.forecast_obj.almost_equal(actual, wanted):
                            elist.append(self.get_msg_error(
                                fname, actual, wanted, index=val))

        error_msg = '\n'.join(['\n', _('Fall forecast calculation ')] + elist)
        self.assertTrue(elist == [], error_msg)

    def get_msg_error(self, fname, actual, expected, index=False):
        """ Compare two float values add return an error message.

        :fname: field name to compare
        :actual: real value of the forecasting
        :expected: expected value of the forecasting
        :index: indicate the sequence relative to the current comparation for
                a forecasing data value record.

        :returns: a string with the formated error message that reports the
        error found with all the required details to indenfificate.
        """
        error_msg = "{fname:15} {actual:15} != {expected:15} {ca} {diff:15}"
        if index:
            error_msg += '   at value with sequence {index}'
        expected = float(expected)
        # pylint: disable=prefer-other-formatting
        error_msg = error_msg.format(
            fname=fname,
            actual=actual,
            expected=expected,
            ca=expected < actual and '>' or '<',
            diff=abs(actual - expected),
            index=index,
        )
        return error_msg

    def get_expected_value_ids_results(self, test_file):
        """ Open a test case expected output file and transform it to a
        pandas.DataFrame object to make easier the comparation of the results.

        :test_file: the name of the file to extract the
                    forecast.data expected results.
        :returns: a pandas.DataFrame object with the expected results for
                  every value in the forecasting data.
        """
        infile = tools.file_open(test_file)
        reader = csv.DictReader(infile)
        result = {}
        for row in reader:
            key = int(row.pop('sequence'))
            if key in result:
                # implement your duplicate row handling here
                pass
            result[key] = dict([
                (kval, val != '' and float(val) or 0.0)
                for kval, val in row.iteritems()
            ])
        result = pd.DataFrame.from_dict(result, orient='index')
        result['sequence'] = result.index
        result.set_index('sequence', inplace=True)
        result = result.reindex_axis(sorted(result.columns), axis=1)
        return result

    def test_00(self):
        """ Test CRUD, Check models constrains and empty fields """

        # Test Create
        forecast = self.forecast_obj.create({})

        # Test Read + Check defaults values
        defaults = {
            'period': 5, 'exp_alpha': 0.3, 'holt_alpha': 0.3,
            'beta': 0.03, 'holt_period': 1,
        }
        self.compare(defaults, forecast.read(defaults.keys())[0])

        # Test Write
        forecast.period = 3

        # Test Duplicate
        forecast2 = forecast.copy()
        self.compare(defaults, forecast2.read(defaults.keys())[0])

        # Test Contraints
        for item in [1, 0, -2]:
            with self.assertRaisesRegexp(
                    ValidationError,
                    "Period must be an integer greater than 1."):
                forecast.period = item

        for item in [0, 1, 2, -2]:
            with self.assertRaisesRegexp(
                    ValidationError, 'Alpha should be between 0 and 1.'):
                forecast.exp_alpha = item

        for item in [0, 1, 2, -2]:
            with self.assertRaisesRegexp(
                    ValidationError, 'Beta should be between 0 and 1.'):
                forecast.beta = item

        for item in [0, 1, 2, -2]:
            with self.assertRaisesRegexp(
                    ValidationError, 'Alpha should be between 0 and 1.'):
                forecast.holt_alpha = item

        # Check that forecasting = 0.0 when data is 0.0
        values = forecast.value_ids
        self.assertFalse(any(values), 'Must be blank')
        keys = [
            'sma_forecast',
            'sma_ma_error',
            'cma_forecast',
            'cma_ma_error',
            'wma_forecast',
            'wma_ma_error',
            'single_forecast',
            'single_ma_error',
            'double_forecast',
            'double_ma_error',
            'triple_forecast',
            'triple_ma_error',
            'holt_forecast',
            'holt_ma_error',
        ]
        out = {}.fromkeys(keys, 0.0)
        self.compare(out, forecast.read(keys)[0])

    def test_00_1(self):
        """ Check Clear method/button works propertly """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_01'))
        self.assertTrue(len(forecast.value_ids))
        forecast.clear()
        self.assertFalse(len(forecast.value_ids))

    def test_00_2(self):
        """ Check Reset Defaults button works propertly """

        # Make a copy of a existing forecasting to test
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_01'))
        forecast_dict = forecast.read()[0]

        # Check Defaults
        defaults = dict(
            period=5,
            exp_alpha=0.3,
            holt_alpha=0.3,
            beta=0.03,
            holt_period=1,
        )
        for fname, default_value in defaults.items():
            self.assertEqual(forecast_dict.get(fname), default_value)

        # Change Defaults
        new_defaults = dict(
            period=2,
            exp_alpha=0.1,
            holt_alpha=0.4,
            beta=0.02,
            holt_period=4,
        )
        forecast.write(new_defaults)
        forecast_dict = forecast.read()[0]
        for fname, default_value in new_defaults.items():
            self.assertEqual(forecast_dict.get(fname), default_value)

        # Reset Defaults
        forecast.reset_defaults()
        forecast_dict = forecast.read()[0]
        for fname, default_value in defaults.items():
            self.assertEqual(forecast_dict.get(fname), default_value)

    def test_00_3(self):
        """ Check forecast_id default value propertly set in fsd model """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_01'))

        # Check saved forecast data
        self.assertTrue(len(forecast.value_ids) > 1)
        forecasts = forecast.value_ids.mapped('forecast_id')
        self.assertEqual(forecasts, forecast)

        # Create new forecast data from forecast and check default
        forecast.write({'value_ids': [
            (0, 0, {'sequence': 81, 'value': 104})]})
        new_val_data = forecast.value_ids.filtered(
            lambda val: val.sequence == 81)
        self.assertTrue(new_val_data)
        self.assertEqual(new_val_data.forecast_id, forecast)

        # Create new forecast data simulating the view
        new_val_data = self.fdata_obj.with_context({
            'forecast_id': forecast.id,
        }).create({'sequence': 82, 'value': 150})
        self.assertTrue(new_val_data)
        self.assertEqual(new_val_data.forecast_id, forecast)

    def test_01(self):
        """ Run 80 values, count for 1 to 30 and repeat.
        """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_01'))
        out = self.get_test_01_out()
        self.compare(out, forecast.read(out.keys())[0])

    def get_test_01_out(self):
        """ Return a dictionary with the expected result of the test.

        :returns: dictionary with the expected values for the test 01
        """
        test_file = 'forecasting_smoothing_techniques/tests/test_01_out.csv'
        value_ids = self.get_expected_value_ids_results(test_file)
        return dict(
            value_ids=value_ids,
            cma_forecast=18.0, cma_ma_error=3.15,
            sma_forecast=17.0, sma_ma_error=4.6,
            wma_forecast=18.666667, wma_ma_error=2.10,
            single_forecast=17.690605, single_ma_error=2.881943,
            double_forecast=19.755723, double_ma_error=5.155758,
            triple_forecast=19.580177, triple_ma_error=6.901317,
            holt_forecast=18.221501, holt_ma_error=3.003755
        )

    def test_02(self):
        """ All Table with 10 values """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_02'))
        out = self.get_test_02_out()
        self.compare(out, forecast.read(out.keys())[0])

    def get_test_02_out(self):
        """ Return a dictionary with the expected result of the test.

        :returns: dictionary with the expected values for the test 02
        """
        test_file = 'forecasting_smoothing_techniques/tests/test_02_out.csv'
        value_ids = self.get_expected_value_ids_results(test_file)
        return dict(
            value_ids=value_ids,
            sma_forecast=7.0, sma_ma_error=3.0,
            cma_forecast=8.0, cma_ma_error=2.0,
            wma_forecast=8.66666, wma_ma_error=1.33,
            single_forecast=7.760825, single_ma_error=1.577526,
            double_forecast=9.481168, double_ma_error=2.691897,
            triple_forecast=9.451321, triple_ma_error=3.432094,
            holt_forecast=11, holt_ma_error=0
        )

    def _test_03(self, period):
        """ base for various periods """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_03'))
        forecast.write({'holt_period': period})
        out = self.get_test_03_out(period)
        self.compare(out, forecast.read(out.keys())[0])

    def test_03_1(self):
        """ holt(k=1) for 11 values """
        self._test_03(1)

    def test_03_2(self):
        """ holt(k=2) for 11 values """
        self._test_03(2)

    def test_03_3(self):
        """ holt(k=3) for 11 values """
        self._test_03(3)

    def test_03_4(self):
        """ holt(k=4) for 11 values """
        self._test_03(4)

    def get_test_03_out(self, period=1):
        """ Return a list with the result values.

        :returns: dictionary with the expected values for the test 03
        """
        out = dict()
        test_file = 'forecasting_smoothing_techniques/tests/test_03_out.csv'
        value_ids = self.get_expected_value_ids_results(test_file)
        out.update(value_ids=value_ids)
        if period == 1:
            out.update(
                holt_period=1, holt_forecast=359.70, holt_ma_error=17.67,
                sma_forecast=292.60, sma_ma_error=76.4,
                cma_forecast=315.00, cma_ma_error=48.2,
            )
        elif period == 2:
            out.update(
                holt_period=2, holt_forecast=372.6,
            )
        elif period == 3:
            out.update(
                holt_period=3, holt_forecast=385.4,
            )
        elif period == 4:
            out.update(
                holt_period=4, holt_forecast=398.3,
            )
        else:
            raise Exception(
                _('There is not output for the enter count of periods'))
        return out

    def test_04(self):
        """ SMA(5) and WMA(5) in 12 integer values """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_04'))
        out = self.get_test_04_out()
        self.compare(out, forecast.read(out.keys())[0])

    def get_test_04_out(self):
        """ Return a dictionary with the expected result of the test.

        :returns: dictionary with the expected values for the test 04
        """
        test_file = 'forecasting_smoothing_techniques/tests/test_04_out.csv'
        value_ids = self.get_expected_value_ids_results(test_file)
        return dict(
            value_ids=value_ids,
            sma_forecast=117.00, sma_ma_error=10.42,
            cma_forecast=120.00, cma_ma_error=6.37,
            wma_forecast=120.33, wma_ma_error=4.37,
        )

    def test_05(self):
        """ SMA(3) in 12 integer values """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_05'))
        self.assertEqual(forecast.period, 3)
        out = self.get_test_05_out()
        self.compare(out, forecast.read(out.keys())[0])

    def get_test_05_out(self):
        """ Return a dictionary with the expected result of the test.

        :returns: dictionary with the expected values for the test 05
        """
        test_file = 'forecasting_smoothing_techniques/tests/test_05_out.csv'
        value_ids = self.get_expected_value_ids_results(test_file)
        return dict(
            value_ids=value_ids,
            sma_forecast=101.66, sma_ma_error=14.07,
            cma_forecast=118.33, cma_ma_error=7.9,
        )

    def test_06(self):
        """ Test what happens with not enough forecast data.

        List of minimum data to calculate every forecast:

            sma: values < period + 1
            cma: values < period
            wma: values < period
            exp: values < 2
            holt: values < 3

        In this test I just consult the Forecast records created in data demo
        check the values length and make a read() to simulate access the
        record from the forecast menu and to force calculate the forecast

        Not errors must be raised.
        """
        forecast = self.forecast_obj.browse(self.ref(
            'forecasting_smoothing_techniques.fst_demo_06'))
        self.assertTrue(forecast)
        self.assertTrue(forecast.value_ids)
        self.assertEqual(len(forecast.value_ids), 1)
        forecast.read([])

    def test_08_1(self):
        """ Security: Manager can do anything
        """

        # Create demo user to test forecast manager security
        user_obj = self.env['res.users']
        user = user_obj.create({
            'name': 'Forecast Manager',
            'login': 'forecast_manager',
            'email': 'forecast_manager@yourcompany.example.com',
            'password': '123456'})
        self.assertTrue(user)

        # Get group information
        group_obj = self.env['res.groups']
        mngr_group = group_obj.browse(self.ref(
            'forecasting_smoothing_techniques.forecast_group_manager'))
        self.assertTrue(mngr_group)

        # add a demo user to the group
        mngr_group.users = [(6, 0, [user.id])]
        self.assertIn(user, mngr_group.users)

        # Test Create, Write, Read, Copy and Delete (ALL SUCCESS)
        forecast = self.forecast_obj.sudo(user).create({})
        forecast.sudo(user).write({
            'name': 'New name was set in unit test 06 1'})
        self.assertTrue(forecast.sudo(user).name)
        forecast2 = forecast.sudo(user).copy()
        self.assertTrue(forecast2)
        forecast.sudo(user).unlink()

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_08_2(self):
        """ Security: Forecast User can not create or delete.
        """

        # Create demo user to test forecast manager security
        user_obj = self.env['res.users']
        user = user_obj.create({
            'name': 'Forecast User',
            'login': 'forecast_user',
            'email': 'forecast_user@yourcompany.example.com',
            'password': '123456'})
        self.assertTrue(user)

        # Get group information
        group_obj = self.env['res.groups']
        user_group = group_obj.browse(self.ref(
            'forecasting_smoothing_techniques.forecast_group_user'))
        self.assertTrue(user_group)

        # add a demo user to the group
        user_group.users = [(6, 0, [user.id])]
        self.assertIn(user, user_group.users)

        # Test Create FAIL
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to create.*forecast'):
            self.forecast_obj.sudo(user).create({})

        # Test Write SUCCESS
        forecast = self.forecast_obj.search([])[0]
        forecast.sudo(user).write({
            'name': 'New name was set in unit test 06 2'})

        # Test Read SUCCESS
        self.assertTrue(forecast.sudo(user).name)

        # Test Copy FAIL
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to create.*forecast'):
            forecast.sudo(user).copy()

        # Test Delete FAIL
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to delete.*forecast'):
            forecast.sudo(user).unlink()

    @mute_logger('openerp.addons.base.ir.ir_model', 'openerp.osv.orm')
    def test_08_3(self):
        """ Security: Non Forecast group user can not do anything
        """

        # Create demo user to test non forecast security
        user_obj = self.env['res.users']
        user = user_obj.create({
            'name': 'Regular User',
            'login': 'regular_user',
            'email': 'regular_user@yourcompany.example.com',
            'password': '123456'})
        self.assertTrue(user)

        # Get group information
        group_obj = self.env['res.groups']
        user_group = group_obj.browse(self.ref(
            'forecasting_smoothing_techniques.forecast_group_user'))
        self.assertTrue(user_group)
        mngr_group = group_obj.browse(self.ref(
            'forecasting_smoothing_techniques.forecast_group_manager'))
        self.assertTrue(mngr_group)

        # add a demo user to the group
        self.assertNotIn(user, user_group.users)
        self.assertNotIn(user, mngr_group.users)

        # Test Create FAIL
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to create.*forecast'):
            self.forecast_obj.sudo(user).create({})

        # Test Write FAIL
        forecast = self.forecast_obj.search([])[0]
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to modify.*forecast'):
            forecast.sudo(user).write({
                'name': 'New name was set in unit test 06 2'})

        # Test Read FAIL
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to access.*forecast'):
            self.assertTrue(forecast.sudo(user).name)

        # Test Copy FAIL
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to access.*forecast'):
            forecast.sudo(user).copy()

        # Test Delete FAIL
        with self.assertRaisesRegexp(
                AccessError, 'not allowed to delete.*forecast'):
            forecast.sudo(user).unlink()

    def test_07(self):
        """ Check almost_equal method.
        """
        self.assertTrue(self.forecast_obj.almost_equal(2.19, 2.17))
        self.assertTrue(self.forecast_obj.almost_equal(2.19, 4.0))
        self.assertFalse(self.forecast_obj.almost_equal(2.19, 4.7))
