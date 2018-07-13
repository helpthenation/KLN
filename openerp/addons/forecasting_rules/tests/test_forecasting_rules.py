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

from openerp.exceptions import ValidationError
from openerp.tests import common
from openerp.tools.safe_eval import safe_eval


class TestForecastingRules(common.TransactionCase):

    """Test that the forecasting rules model is working propertly.

    For the current test the res.partner model will be use as the forecasting
    rule model. Bellow information about some res.partner fields that will be
    used (type, list of fields, module defined):

        int:
            id
        float:
            credit_limit (base module)
            debilt_limit
            credit       (account module)
            debit        (account module)
        date:
            date
        datetime:
            last_reconciliation_data

    As forecast_value we are goin to use the credit_limit float field. This
    field is add in the base module but is show in the partner in the account
    module so will not be show in the partner form view.

    So far some partners already have a credit_limit value set in demo:

        [{'credit_limit': 15000.0, 'id': 19, 'name': u'Chamber Works'},
        {'credit_limit': 15000.0, 'id': 58, 'name': u'Angel Cook'},
        {'credit_limit': 15000.0, 'id': 59, 'name': u'Robert Anderson'},
        {'credit_limit': 1500.0, 'id': 60, 'name': u'Jacob Taylor'},
        {'credit_limit': 1500.0, 'id': 20, 'name': u'Millennium Industries'}
        ]
    """

    def setUp(self):
        super(TestForecastingRules, self).setUp()

        # Save in test the basic objects
        self.rule_obj = self.env['forecasting.rule']
        self.irfilter_obj = self.env['ir.filters']
        self.forecast_obj = self.env['forecast']

        # Get the data demo
        self.forecast = self.forecast_obj.browse(
            self.ref('forecasting_rules.forecast_demo_01'))
        self.rule = self.rule_obj.browse(self.ref(
            'forecasting_rules.forecast_rule_demo_01'))
        self.irfilter = self.irfilter_obj.browse(self.ref(
            'forecasting_rules.filter_demo_01'))
        self.partner_model = self.ref('base.model_res_partner')

        # First ensure that the filter to test correspond to the rule used
        # in this test.
        self.assertEqual(self.rule.filter_id, self.irfilter)

        # Second, ensure that the rule is related to the forecast test record.
        self.assertEqual(self.forecast.rule_id, self.rule)

    def create_rule(self, name='All Partners', model='res.partner',
                    wo_irfilter=False):
        """Create a ir filter with the specificated arguments

        :name: name of the ir.filter to create
        :model: model name to use in the ir.filter

        :return: recordset with the record create
        """
        values = {
            'name': ' Partner Credit Limit (Test %s)' % name,
            'model': model,
            'filter_id': self.irfilter.id,
        }
        if wo_irfilter:
            values.pop('filter_id')
        rule = self.rule_obj.create(values)
        return rule

    def test_01(self):
        """Basic CRUD
        """
        # Test Create (With Basic Values)
        rule = self.create_rule()
        self.assertTrue(rule)

        # Test Read (via recorset)
        rule_name = False
        rule_name = rule.name
        self.assertTrue(rule_name)

        # Test Read (via orm read())
        rule_dict = rule.read()[0]
        self.assertTrue(isinstance(rule_dict, (dict,)))

        # Test Write
        new_name = rule_name + ' [Rename in python unit test]'
        rule.name = new_name
        self.assertEqual(rule.name, new_name)

        # Test Duplicate
        rule2 = rule.copy()
        self.assertTrue(rule2)

    def test_02(self):
        """Constraint: Rule filter context without the required keys

        Remove context required key over an existing forecasting rule filter.
        The required keys are forecast_order and forecast_rule.
        In all the cases must raise an error.
        """
        # Remove forecast_order key
        context = safe_eval(self.rule.filter_id.context)
        with self.assertRaises(ValidationError):
            context.pop('forecast_order')
            self.rule.filter_id.context = str(context)

        # Remove forecast_value key
        context = safe_eval(self.rule.filter_id.context)
        with self.assertRaises(ValidationError):
            context.pop('forecast_value')
            self.rule.filter_id.context = str(context)

    def test_03(self):
        """Constraint: rule filter context with forecast value/order not valid.
        """
        context = safe_eval(self.irfilter.context)

        # Use a not exist order field
        with self.assertRaises(ValidationError):
            context.update(forecast_order='nonexist_field')
            self.rule.filter_id.context = str(context)

        # Use a not exist value field
        with self.assertRaises(ValidationError):
            context.update(forecast_value='nonexist_field')
            self.rule.filter_id.context = str(context)

    def test_04(self):
        """Check: Bidirectional change rule model / filter model
        """
        self.assertEqual(self.irfilter.model_id, self.rule.model)

        # When change the irfilter model then the rule model also change.
        self.irfilter.model_id = 'res.users'
        self.assertEqual(self.rule.model, self.irfilter.model_id)

        # When change the rule model then the irfilter model also change.
        self.rule.model = 'res.groups'
        self.assertEqual(self.irfilter.model_id, self.rule.model)

    def test_05(self):
        """ forecast step: invalid step type """
        context = safe_eval(self.rule.filter_id.context)
        msg = 'Not valid context forecast_step value'
        with self.assertRaisesRegexp(ValidationError, msg):
            context.update({'forecast_step': 'invalid_step'})
            self.rule.filter_id.context = str(context)

    def test_06(self):
        """ forecast step: non date/datetime order when step defined """
        context = safe_eval(self.rule.filter_id.context)
        msg = 'forecast order must be date/datime'
        with self.assertRaisesRegexp(ValidationError, msg):
            context.update({
                'forecast_step': 'week', 'forecast_order': 'id'})
            self.rule.filter_id.context = str(context)

    def test_07(self):
        """ forecast step: generate the right number of values.
          - values length is current_month values.
        """
        forecast = self.forecast_obj.browse(
            self.ref('forecasting_rules.forecast_demo_06'))
        self.assertTrue(forecast)
        # TODO check the best way to extract the date using odoo
        self.assertEqual(len(forecast.value_ids), 9)
