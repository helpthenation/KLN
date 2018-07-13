# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    group_discount_global=fields.Boolean("Allow setting a discount on the sales order Total Amount",
            implied_group='fnet_discount.group_discount_global',default=True,
            help="Allows you to apply some discount per sales order Total Amount.")
    group_product_discount=fields.Boolean("Allow setting a discount on the sales order line",
            implied_group='fnet_discount.group_discount_global',default=True,
            help="Allows you to apply some discount per sales order line.")
    discount_value = fields.Float(string='Discount',help='Choose the value of the Discount')
    discount_percentage = fields.Float(string='Discount Percentage',help='Choose the value of the Discount')
    discount_calculation_account_id = fields.Many2one('account.account',string='Discount Account')
    product_discount_account_id = fields.Many2one('account.account',string='Trading Account')



