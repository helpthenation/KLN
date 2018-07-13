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


class TestIrFilters(common.TransactionCase):

    """Test that the ir.filters model work properly w/wo a forecasting rule.
    """

    def setUp(self):
        super(TestIrFilters, self).setUp()
        self.irfilter_obj = self.env['ir.filters']

        # # Get the data demo
        self.rule = self.env['forecasting.rule'].browse(self.ref(
            'forecasting_rules.forecast_rule_demo_01'))

        # TODO check delete the data demo ir filter
        # self.irfilter = self.filter_obj.browse(self.ref(
        #     'forecasting_rules.filter_demo_01'))

    def create_filter(self, name='NOT ESPECIFIED', model_id='res.partner',
                      context='{}', domain='[]', link_rule=True):
        """Create a ir filter with the specificated arguments

        :name: name of the ir.filter to create
        :model_id: model name to use in the ir.filter
        :context: context field in the ir.filter record
        :domain: domain field in the ir.filter record
        :link_rule: boolean that tell if you want to link or not the created
                    irfilter to a forecast rule

        :return: recordset with the record create
        """
        irfilter = self.irfilter_obj.create({
            'name': 'All Partner (Test %s)' % name,
            'model_id': model_id,
            'context': context,
            'domain': domain,
        })
        if link_rule:
            self.rule.filter_id = irfilter.id
        return irfilter

    def test_01(self):
        """Basic CRUD
        """
        # Test Create (W Basic Values)
        # NOTE: can not create a irfilter without # the next list of values.
        irfilter_name = 'All Partners'
        irfilter = self.irfilter_obj.create({
            'name': irfilter_name,
            'model_id': 'res.partner',
            'context': '{}',
            'domain': '[]',
        })
        self.assertTrue(irfilter)

        # Test Read (via recorset)
        self.assertEquals(irfilter.name, irfilter_name)

        # Test Read (via orm read())
        irfilter_dict = irfilter.read()[0]
        self.assertTrue(isinstance(irfilter_dict, (dict,)))
        self.assertEquals(irfilter_dict.get('name', False), irfilter_name)

        # Test Write
        new_name = irfilter_name + ' [Rename in python unit test]'
        irfilter.name = new_name
        self.assertEqual(irfilter.name, new_name)

        # TODO Fix tis test is falling.
        # # Test Duplicate
        # irfilter2 = irfilter.copy()
        # self.assertTrue(irfilter2)

    def test_02(self):
        """Create filter with a forecast rule.
        """
        irfilter = self.create_filter(name='2', link_rule=False)
        self.rule.filter_id = irfilter.id
        self.assertEqual(self.rule.filter_id, irfilter)
        self.assertTrue(irfilter.get_related_rules())

    def test_03(self):
        """Create a filter with a invalid domain
        """
        irfilter = self.create_filter(name='3')
        error = 'The domain value you introduce is not a valid domain'
        invalid_domain = [
            'this is an error',
            '[this is an error]',
        ]

        for domain in invalid_domain:
            with self.assertRaisesRegexp(ValidationError, error):
                irfilter.domain = domain

    def test_04(self):
        """Create a filter with a invalid context
        """
        irfilter = self.create_filter(name='4')
        error = 'The context value you introduce is not a valid context'
        invalid_context = [
            'this is an error',
            '[]',
            '{value: bad}',
            "{'not_forecast_value': 'value'}",
        ]
        for context in invalid_context:
            with self.assertRaisesRegexp(ValidationError, error):
                irfilter.context = context

    def test_05(self):
        """Create a filter with a invalid model

        This is manage from the orm.
        """
        irfilter = self.create_filter(name='5')
        with self.assertRaises(ValueError):
            irfilter.model_id = 'non.exist.model'
