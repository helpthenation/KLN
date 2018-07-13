# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sale_discount_field(models.Model):
    _inherit = 'sale.order'

    @api.model
    @api.multi
    def _updating_discount_amount(self):
           self.env.cr.execute('''select so.id as id from sale_order so
            join account_payment_term_line apl on apl.id =  so.payment_term
           where so.date_order::date >= '2017-09-22' and apl.days = 0''')
           order_list=self.env.cr.dictfetchall() 
           for i in order_list:          
               self.env.cr.execute("""
                update sale_order set amount_total=round((amount_untaxed + amount_tax - (amount_untaxed * (disc_value / 100)))::DECIMAL,2) 
                where  date_order::date >= '2017-09-22' and id=%d """%(i['id']))
          
