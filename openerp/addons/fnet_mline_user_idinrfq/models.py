# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sale_discount_field(models.Model):
    _inherit = 'purchase.order'

    @api.model
    @api.multi
    def _updating_user_id(self):
           self.env.cr.execute('''select id,user_id as user_id from purchase_requisition''')
           order_list=self.env.cr.dictfetchall() 
           for i in order_list:          
               self.env.cr.execute("""
                update purchase_order set user_id= %d 
                where requisition_id=%d """%(i['user_id'],i['id']))
          
