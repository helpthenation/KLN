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


class ForecastingRule(models.Model):

    _name = 'forecasting.rule'
    _description = 'Forecasting Rule'

    name = fields.Char(required=True,
                       help='Name to identify the Forecasting Rule')
    model = fields.Selection(
        related='filter_id.model_id',
        required=True,
        help='Model were this forecast apply. Be careful, If you update this'
             ' field the ir.filter model field will be updated and vice versa')
    filter_id = fields.Many2one(
        'ir.filters',
        domain="[('model_id','=', model)]",
        string='Filter',
        required=True,
        help='Filter that indicate what values are going to be extract'
             ' for the forecast')

    display_name = fields.Char(
        string='Name', compute='_compute_display_name')

    @api.depends('name')
    def _compute_display_name(self):
        for rule in self:
            names = [str(rule.id), rule.name]
            rule.display_name = ' '.join(names)
