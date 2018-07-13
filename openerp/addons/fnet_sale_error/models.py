# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sale_discount_field(models.Model):
    _inherit = 'sale.order'

    @api.model
    @api.multi
    def _updating_discount_amount(self):
           self.env.cr.execute(''' 
           update sale_order set partner_id = 1671 , partner_invoice_id = 1671 , partner_shipping_id = 1671 
           where id = 23499
           ''')
           self.env.cr.execute(''' 
			update stock_picking set partner_id = 1671 where id = 17324
           ''')

          
