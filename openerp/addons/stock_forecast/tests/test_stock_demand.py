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

from dateutil.relativedelta import relativedelta

from openerp import fields
from openerp.tests import common


class TestForecastDemand(common.TransactionCase):

    def setUp(self):
        super(TestForecastDemand, self).setUp()
        self.history_obj = self.env['stock.history']
        self.demand_obj = self.env['wizard.stock.demand']
        self.move_obj = self.env['stock.move']

    def create_and_run_demand_wizard(self, create_filter):
        """ - Create a stock demand wizard with random product and location
        - Run demand wizard to activate the stock.history
        - If create_filter True/False indicate if create forecast rule filter
        - Search for the filter created.

        :return: result of search the forecasr rule filter
        """
        product = self.env['product.product'].search([])[0]
        location = self.env['stock.location'].search([])[0]
        wiz = self.demand_obj.create({
            'product_id': product.id,
            'location_id': location.id,
            'date_from': (fields.date.today() - relativedelta(
                months=1)).strftime('%Y-%m-%d'),
            'date_to': fields.date.today(),
            'demand_filter': create_filter,
        })
        self.assertTrue(wiz)
        wiz.open_table()
        name, domain, model = wiz.get_demand_data()
        irfilter = self.env['ir.filters'].search([
            ('name', '=', name),
            ('domain', '=', str(domain)),
            ('model_id', '=', model),
        ])
        return irfilter

    def test_01(self):
        """Return the action from the wizard
        """
        move_brw = self.move_obj.search([], limit=1)
        if move_brw:
            # Creating the wizard with the required values
            demand_brw = self.demand_obj.create({
                'product_id': move_brw.product_id.id,
                'location_id': move_brw.location_id.id,
                'date_from': '2015-01-01',
                'date_to': move_brw.create_date,
            })
            action = demand_brw.open_table()
            # Validating the type of the action returned
            self.assertTrue(isinstance(action, dict))
            domain = action.get('domain', [])
            for values in domain:
                # Validating the values in the domain
                if 'date' in values[0]:
                    domain_date = values[2]
                    move_date = fields.Datetime.from_string(
                        move_brw.create_date).strftime('%Y-%m-%d')
                    self.assertTrue(domain_date in [move_date, '2015-01-01'])
                elif 'product' in values[0]:
                    self.assertEqual(values[2], move_brw.product_id.id)
                elif 'product' in values[0]:
                    self.assertEqual(values[2], move_brw.location_id.id)

    def test_02(self):
        """Validating that the compute field is computed
        """
        history_brw = self.history_obj.search([], limit=1)
        if history_brw:
            # Validating the new compute field was computed
            self.assertTrue(history_brw.quantity_onstock >= 0)

    def test_03(self):
        """ Stock Demand: Auto Generate Forecast Rule Filter
        """
        irfilter = self.create_and_run_demand_wizard(create_filter=True)
        self.assertTrue(irfilter)

    def test_04(self):
        """ Stock Demand: Do not Generate Forecast Rule Filter
        """
        irfilter = self.create_and_run_demand_wizard(create_filter=False)
        self.assertFalse(irfilter)
