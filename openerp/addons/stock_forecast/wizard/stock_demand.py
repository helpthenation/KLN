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

from openerp import _, api, fields, models


class StockDemand(models.TransientModel):

    _name = 'wizard.stock.demand'

    product_id = fields.Many2one('product.product', 'Product',
                                 help='Product used to filter '
                                 'the information to show, '
                                 'We will show you only moves '
                                 'related to this product')
    date_from = fields.Date('Date From',
                            help='Date Start used to get '
                            'the range of the demands')
    date_to = fields.Date('Date to',
                          help='Date End used to get '
                          'the range of the demands')
    location_id = fields.Many2one('stock.location',
                                  'Location',
                                  help='Destination location '
                                  'of the moves to show')
    demand_filter = fields.Boolean(
        'Generate Rule Filter',
        help='If True generate a Search Filter to re-use in the forecast rule'
             '. If False only check the demand')

    @api.multi
    def open_table(self):
        """ Open the stock history view using the info registered in the wizard
        """
        ctx = dict(self._context).copy()
        ctx.update({
            'history_date': self.date_to,
        })
        name, domain, model = self.get_demand_data()

        if self.demand_filter:
            self.create_demand_filter(name, domain, model)

        tree_view = self.env.ref('stock_forecast.'
                                 'view_stock_demand_history_report_tree')
        return {
            'domain': domain,
            'name': name,
            'view_type': 'form',
            'views': [(tree_view.id, 'tree')],
            'view_mode': 'tree,graph',
            'res_model': model,
            'type': 'ir.actions.act_window',
            'context': ctx,
        }

    @api.multi
    def get_demand_data(self):
        """ Pre-process the date to be use to filter the stock.history records.

        :return: tuple (name view, domain, model name)
        """
        model = 'stock.history'
        name = ' '.join([
            _('Stock Demand for'), self.product_id.name, _('Product'),
            _('in'), self.location_id.display_name,
            '(' + _('From'), self.date_from, _('to'), self.date_to + ')'])
        domain = [
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('quantity', '<', 0.0),
            ('product_id', '=', self.product_id.id),
            ('location_id', '=', self.location_id.id)]

        return name, domain, model

    @api.multi
    def create_demand_filter(self, name, domain, model):
        """ Create forecast rule filter

        :name: name of the filter
        :domain: stock demand domain
        :model: model name

        :return: if_filters record created
        """
        context = {
            'forecast_value': 'quantity_force_positive',
            'forecast_order': 'date'}
        filter_obj = self.env['ir.filters']
        irfilter = filter_obj.search([
            ('name', '=', name),
            ('domain', '=', str(domain)),
            ('context', '=', str(context)),
            ('model_id', '=', model),
        ])
        if not irfilter:
            irfilter = filter_obj.create({
                'name': name,
                'domain': domain,
                'context': context,
                'model_id': model})
        return irfilter


class StockHistory(models.Model):

    _inherit = 'stock.history'

    @api.multi
    def _compute_quantity_onstock(self):
        """ Set the quantity available at the moment to delivery the product
        """
        for history in self:
            history._cr.execute(
                'SELECT sum(quantity) FROM stock_history '
                'WHERE product_id=%(prod)s AND date < %(date)s',
                dict(prod=history.product_id.id, date=history.date))
            result = history._cr.fetchall()
            qty = result and result[0][0] or 0.0
            history.quantity_onstock = qty

    quantity_onstock = fields.Float(
        'Quantity Demanded',
        compute='_compute_quantity_onstock',
        store=False,
        help='Quantity demanded in the move')

    quantity_force_positive = fields.Float(
        'Quantity Demanded',
        compute='_compute_quantity_force_positive',
        help='Same as Quantity but positive always')

    @api.multi
    def _compute_quantity_force_positive(self):
        """ Set the quantity available at the moment to delivery the product
        """
        for history in self:
            history.quantity_force_positive = abs(history.quantity)
