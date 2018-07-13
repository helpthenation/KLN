# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sale_discount_field(models.Model):
    _inherit = 'sale.order'

    @api.model
    @api.multi
    def _updating_discount_amount(self):
           self.env.cr.execute('''update account_voucher set state = 'draft'  where id in (22200,22201,22486,22487)''')


          
