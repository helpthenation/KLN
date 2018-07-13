# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Ported to Odoo by Andrea Cometa <info@andreacometa.it>
#    Ported to v8 API by Eneko Lacunza <elacunza@binovo.es>
#    Copyright (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
from openerp.exceptions import except_orm, Warning, RedirectWarning
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta

class update_pricelist(models.Model):
    """
    This wizard will submit the all the selected Sale Target
    """

    _name = "update.pricelist"
    _description = "Submit the pricelist"          
       
    date=fields.Date('Date',required=True)
    prod_categ_id=fields.Many2one('product.category', 'Product Category', required=True)
    product_entry_line=fields.One2many('product.entry.line', 'prod_upadate_id', 'Product Lines')
    company_id=fields.Many2one('res.company','Company',
    default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('update.pricelist')))

    _defaults = {
        'date': datetime.datetime.now().strftime("%Y-%m-%d"),
        }                 
        
    @api.multi
    @api.onchange('prod_categ_id')
    def onchange_prod_categ_id(self):
        list_of_dict=[]
        if self.prod_categ_id:
            cate = self.env['product.category'].browse(self.prod_categ_id.id,)
            self.env.cr.execute("""select 
                              pp.id as prod,
                              pt.uom_id as uom,
                              pt.list_price as sale_pr,
                              pt.mrp_price as mrp ,
                              pt.purchase_discount as purchase_discount ,
                              pt.discount_price as discount_price 
                        from product_template pt
                        join product_product pp on (pp.product_tmpl_id = pt.id)
                        where pt.categ_id = '%s' and pt.company_id = '%s' and pt.type != 'service'
                            order by 2 """ % (self.prod_categ_id.id, cate.company_id.id))
            line_list = [i for i in self.env.cr.dictfetchall()]
            for fid in line_list:
               list_of_dict.append((0,0,{"product_id":fid['prod'], "uom_id":fid['uom'],"mrp_price":fid['mrp'],"list_price":fid['sale_pr'],
                "purchase_discount":fid['purchase_discount'],'discount_price':fid['discount_price']}))
            self.product_entry_line =  list_of_dict 
            
    @api.multi
    def update(self):
        for rec in self.product_entry_line:
            self.env.cr.execute("""update product_template set mrp_price=%s,purchase_discount=%s,discount_price=%s,list_price=%s
            where id=%d"""%(rec.mrp_price,rec.purchase_discount,rec.discount_price,rec.list_price,rec.product_id.product_tmpl_id.id))            
            self.env.cr.execute("""update product_product set mrp_price=%s,purchase_discount=%s,discount_price=%s
            where id=%d"""%(rec.mrp_price,rec.purchase_discount,rec.discount_price,rec.product_id.id))            
          
            
class product_entry_line(models.Model):
    _name = 'product.entry.line' 

    prod_upadate_id=fields.Many2one('update.pricelist', 'Sale Entry')
    product_id=fields.Many2one('product.product', 'Product', required=True, readonly=True)
    uom_id=fields.Many2one('product.uom', 'Product UOM', required=True, readonly=True)
    mrp_price=fields.Float('MRP Price')
    list_price=fields.Float('Sale Price')
    purchase_discount=fields.Float('Purchase Discount')
    discount_price=fields.Float('Sale Discount')
    company_id=fields.Many2one('res.company','Company',
    default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('product.entry.line')))
