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
from openerp.osv import fields, osv

class RdUpdate(osv.osv):
    _name="rd.update"
    _rec_name="prod_categ_id"
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
          'prod_categ_id': fields.many2one('product.category', 'Product Category', required=True, track_visibility='always'),
          'company_id': fields.many2one('res.company', 'Company'),
           }
           
    _defaults = {
        'company_id': _get_default_company,
        }
        
    def update_product_lines(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        prod_temp_list=self.pool.get('product.template').search(cr, uid, [('categ_id','=',obj.prod_categ_id.id),('company_id', '=', obj.company_id.id)], context=context)
        cr.execute("""select pp.id as id from product_template pt
         left join product_product pp on pt.id = pp.product_tmpl_id
         where pt.type != 'service' and pt.categ_id =%d and pt.company_id=%d order by pp.id asc"""%(obj.prod_categ_id.id,obj.company_id.id))
        prod_list = [i[0] for i in cr.fetchall()] 
        stock_open_list = self.pool.get('sale.open').search(cr, uid, [('prod_categ_id','=',obj.prod_categ_id.id),('company_id', '=', obj.company_id.id)], context=context)
        sale_entry_list = self.pool.get('sale.entry').search(cr, uid, [('prod_categ_id','=',obj.prod_categ_id.id),('company_id', '=', obj.company_id.id)], context=context)
        for rec in stock_open_list:
            stock_obj=self.pool.get('sale.open').browse(cr,uid,rec)       
            cr.execute("""select product_id from sale_open_line where sale_open_id = %d"""%(rec))
            open_prod_list = [i[0] for i in cr.fetchall()]
            for val in prod_list:
                if val not in open_prod_list:
                    prod_obj=self.pool.get('product.product').browse(cr,uid,val)
                    vals={
                    'sale_open_id':rec,
                    'product_id':val,
                    'uom_id':prod_obj.product_tmpl_id.uom_id.id,
                    'amount':0.0,
                    'company_id':obj.company_id.id,
                    }
                    self.pool.get('sale.open.line').create(cr, uid, vals, context=context)
                                    #~ print'ffffffffffffffffffffffffffffffff',data.product_id.default_code 
        for rec in sale_entry_list:
            stock_obj=self.pool.get('sale.entry').browse(cr,uid,rec)       
            cr.execute("""select product_id from sale_entry_line where sale_entry_id = %d"""%(rec))
            open_prod_list = [i[0] for i in cr.fetchall()]
            for val in prod_list:
                if val not in open_prod_list:
                    prod_obj=self.pool.get('product.product').browse(cr,uid,val)
                    vals={
                    'sale_entry_id':rec,
                    'product_id':val,
                    'uom_id':prod_obj.product_tmpl_id.uom_id.id,
                    'amount':0.0,
                    'company_id':obj.company_id.id,
                    }
                    self.pool.get('sale.entry.line').create(cr, uid, vals, context=context)
                    
                    
class RdGenerate(osv.osv):
    _name="rd.generate"
    _rec_name="prod_categ_id"
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        period = periods and periods[0] or False
        if period:
            return self.pool.get('account.period').browse(cr,uid,period).fiscalyear_id.date_start
        else:
            return False
            
    _columns = {
          'prod_categ_id': fields.many2one('product.category', 'Product Category', required=True, track_visibility='always'),
          'company_id': fields.many2one('res.company', 'Company'),
          'date_from':fields.date('From Date'),
           }
           
    _defaults = {
        'company_id': _get_default_company,
        #~ 'date_from': _get_period,
        }
        
    def generate_stock_lines(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids) 
        cr.execute("""select pp.id as id from product_template pt
         left join product_product pp on pt.id = pp.product_tmpl_id
         where pt.type != 'service' and pt.categ_id =%d and pt.company_id=%d order by pp.id asc"""%(obj.prod_categ_id.id,obj.company_id.id))
        prod_list = [i[0] for i in cr.fetchall()]                    
        cr.execute("""select distinct id from res_partner where company_id=%d and
        customer = 'True' and active = 'True' and 
        user_id is not null""" %(obj.company_id.id))
        partner= [k['id'] for k in cr.dictfetchall()] 
        for rec in partner:
            stock_open_list = self.pool.get('sale.open').search(cr, uid, [('partner_id','=',rec),('prod_categ_id','=',obj.prod_categ_id.id),('company_id', '=', obj.company_id.id)], context=context)
            if not stock_open_list:
                custom = self.pool.get('res.partner').browse(cr, uid,rec) 
                vals={
                        'date_from': obj.date_from,
                        'sr_id': custom.user_id.id or False ,
                        'partner_id':custom.id,
                        'prod_categ_id':obj.prod_categ_id.id,
                        'state': 'draft', 
                        'company_id':obj.company_id.id,
                         }              
                open_obj = self.pool.get('sale.open').create(cr, uid, vals, context=context) 
                #~ print'opennnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn',open_obj
                for val in prod_list:
                    prod_obj=self.pool.get('product.product').browse(cr,uid,val)
                    vals={
                    'sale_open_id':open_obj,
                    'product_id':val,
                    'uom_id':prod_obj.product_tmpl_id.uom_id.id,
                    'amount':0.0,
                    'company_id':obj.company_id.id,
                    }
                    self.pool.get('sale.open.line').create(cr, uid, vals, context=context)
