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

from openerp import api, fields, models


class ForecastingSmoothingTechniques(models.Model):

    _inherit = 'forecast'

    @api.model
    def _default_product(self):
        """Usability feature -

        :return: product.product id.
        """
        product_id = self._context.get('product_id', False)
        product = self.env['product.product'].search([('id', '=', product_id)])
        return product

    @api.depends('name', 'product_id')
    def _compute_display_name(self):
        """ Usability feature -

        Check if the name of the product are set in the forecast and used to
        overwrite the display name.

        :return: the forecasting name with the product.product name as prefix.
        """
        for forecast in self:
            name = forecast.name
            product = (forecast.product_id and
                       forecast.product_id.name or False)
            if name and product:
                display_name = '%(product)s: %(name)s'
            elif name:
                display_name = '%(name)s'
            elif product:
                display_name = '%(product)s: No Forecast Name'
            forecast.display_name = display_name % dict(
                product=product, name=name)

    display_name = fields.Char(
        string='Name', compute='_compute_display_name')

    product_tmpl_id = fields.Many2one(
        related='product_id.product_tmpl_id',
        store=True)

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        help='Product related to the current forecasting',
        default=_default_product,
        track_visibility='always')
