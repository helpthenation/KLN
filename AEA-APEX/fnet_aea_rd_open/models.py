# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sale_entry(models.Model):
    _inherit = 'sale.entry'

    @api.model
    @api.multi
    def _updating_opening_sale(self):
           self.env.cr.execute('''select * from sale_open order by id asc limit 500''')
           lists=self.env.cr.dictfetchall()
           for i in lists:
                self.env.cr.execute("""select id from sale_entry where date_from='%s' and
                sr_id=%d and partner_id=%d and prod_categ_id=%d and company_id=%d"""
                %(i['date_from'],i['sr_id'],i['partner_id'],i['prod_categ_id'],i['company_id']))
                entry_id=self.env.cr.dictfetchone()
                print'ENTRYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY',entry_id
                open_obj=self.env['sale.open'].browse(i['id'])
                for rec in open_obj.sale_open_line:
                    print "RECCCCCCCCcc",rec
                    if rec and entry_id:
                        print 'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',rec.amount,rec.product_id.id,entry_id['id']
                        self.env.cr.execute("""update sale_entry_line set current_stock = %s where sale_entry_id = %d
                        and product_id = %d"""%(rec.amount,entry_id['id'],rec.product_id.id))


