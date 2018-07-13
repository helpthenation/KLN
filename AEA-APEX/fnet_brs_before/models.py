# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_move(models.Model):
    _inherit = 'account.move'

    @api.model
    @api.multi
    def _updating_unique_ref(self):
           self.env.cr.execute('''select id from account_move where ref::text like '%CHQ%' or ref::text like '%Chq%' or  ref::text like '%chq%' order by ref asc''')
           lists=self.env.cr.dictfetchall() 
           for i in lists:          
               move_obj=self.env['account.move'].browse(i['id'])
               newstr = ''.join((ch if ch in '0123456789' else ' ') for ch in move_obj.ref)
               print'SSSSSSSSSSSSSSSSSSSSSSSSSSSs',str(newstr.split()),move_obj.ref,move_obj.id
               if newstr.split() != []:
                   self.env.cr.execute("""
                    update account_move set is_consolidated=True and consolidate_cheque_no = '%s' 
                    where id=%d """%(str(newstr.split()[0]),i['id']))
                   move_obj.write({'is_consolidated':True,'consolidate_cheque_no':str(newstr.split()[0])}) 
          
