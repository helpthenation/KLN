
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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
from openerp.osv import fields, osv
from datetime import datetime, timedelta
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from lxml import etree

class rd_scheme(osv.osv):
    _name = 'rd.scheme'
    
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
        return periods and periods[0] or False  
        
    _columns = {
          'name':fields.char('Name', size=64, readonly=True),
          'prod_categ_id': fields.many2one('product.category', 'Product Category', required=True, track_visibility='always'),
          'period_id': fields.many2one('account.period', 'Period', required=True),
          'rd_scheme_line':fields.one2many('rd.scheme.line', 'scheme_id', 'Scheme Line'),
          'company_id': fields.many2one('res.company', 'Company'),
          'state': fields.selection([('draft', 'Draft'),('progress', 'Progress'),('cancel', 'Cancel'), ('done', 'Scheme Closed')],'Status', readonly=True, track_visibility='always'),
           }

    _defaults = {
        'state':'draft',
        'period_id':_get_period,
        'company_id': _get_default_company,
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'seheme.entry') or '/',
        }
        
    def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, company_id, context=None):
        result = {}
        list_of_dict=[]
        if prod_categ_id:
            cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            cr.execute("""select 
                              pp.id as prod,
                              pt.uom_id as uom,
                              pt.list_price as sale_pr,
                              pt.mrp_price as mrp 
                        from product_template pt
                        join product_product pp on (pp.product_tmpl_id = pt.id)
                        where pt.categ_id = '%s' and pt.company_id = '%s' and pt.type != 'service'
                            order by 2 """ % (prod_categ_id, cate.company_id.id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"product_id":fid['prod'], "uom_id":fid['uom'],"mrp_price":fid['mrp'],"scheme_qty":1.00})
            result['value'] = {'rd_scheme_line':list_of_dict,}
            return result
    
    def scheme_open(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        cr.execute("""SELECT 
                          rs.id as val
                    FROM rd_scheme rs
                    WHERE rs.period_id = '%s' AND rs.prod_categ_id = '%s' AND rs.id != '%s'
                   """ % (obj.period_id.id, obj.prod_categ_id.id, obj.id))
        line_list = [i for i in cr.dictfetchall()]
        if line_list:
            raise osv.except_osv(_('Error!'), _('This scheme already launched. Pleace launch new scheme!'))
        else:
            self.write(cr, uid, ids, {'state':'progress'}, context=context)
        return True 
        
    def scheme_close(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
        
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)
        
class rd_scheme_line(osv.osv):
    _name = 'rd.scheme.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    #~ def _get_period(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ if context.get('period_id', False):
            #~ return context.get('period_id')
        #~ periods = self.pool.get('account.period').find(cr, uid, context=context)
        #~ return periods and periods[0] or False  
        
    _columns = {
     'scheme_id':fields.many2one('rd.scheme', 'Scheme'),
     'product_id':fields.many2one('product.product', 'Product', readonly=True),
     'uom_id':fields.many2one('product.uom', 'UOM', readonly=True),
     'invoice_price':fields.float('Invoice Price', digits_compute= dp.get_precision('Discount')),
     'mrp_price':fields.float('MRP Price', digits_compute= dp.get_precision('Discount'), readonly=True),
     'scheme_qty': fields.float('Scheme Quantity' ,digits_compute= dp.get_precision('Discount'), readonly=True),
     'scheme_price': fields.float('Scheme Price' ,digits_compute= dp.get_precision('Discount')),
     'company_id': fields.many2one('res.company', 'Company'),
      }
      
    _defaults = {
        'company_id': _get_default_company,
        'scheme_qty': 1.00,
        #~ 'period_id': _get_period,
        }
        
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        result = {}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id)
            prod_tmpl = self.pool.get('product.template').browse(cr, uid, prod.product_tmpl_id.id)
            result['value'] = {'uom_id':prod_tmpl.uom_id.id,
                              'invoice_price':prod_tmpl.list_price,
                              'mrp_price':prod_tmpl.mrp_price,
                              }
        
        return result
rd_scheme_line()

class scheme_entry(osv.osv):
    _name = 'scheme.entry'
    
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
        return periods and periods[0] or False  
    
    _columns = {
        'period_id':fields.many2one('account.period', 'Period', required=True),
        'manager_id': fields.many2one('res.users', 'Sales Manager', required=True),
        'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
        'partner_id':fields.many2one('res.partner', 'Stokiest Id', required=True),
        'prod_categ_id':fields.many2one('product.category', 'Product Category', required=True),
        'state': fields.selection([('draft', 'submit'),('progress', 'Progress'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company'),
        'scheme_id': fields.many2one('rd.scheme', 'Scheme ID',readonly=True),
        'scheme_entry_line':fields.one2many('scheme.entry.line', 'scheme_entry_id', 'Scheme Line',readonly=True),
    }
    _defaults = {
        'company_id': _get_default_company,
        'state':'draft',
        'period_id':_get_period,
        }

    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if manager_id:
            cr.execute("""select 
                                smr.member_id as mem_id
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['mem_id'])
        domain = {'sr_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    def onchange_sr_id(self, cr, uid, ids, sr_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if sr_id:
            cr.execute("""select 
                                id as stokiest_id
                        from res_partner
                        where user_id = '%s' and company_id = '%s' """ % (sr_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['stokiest_id'])
        domain = {'partner_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    #~ def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, company_id,context=None):
        #~ result = {}
        #~ list_of_dict=[]
        #~ if prod_categ_id:
            #~ cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            #~ cr.execute("""select 
                              #~ pp.id as prod,
                              #~ pt.uom_id as uom,
                              #~ pt.list_price as sale_pr,
                              #~ pt.mrp_price as mrp 
                        #~ from product_template pt
                        #~ join product_product pp on (pp.product_tmpl_id = pt.id)
                        #~ where pt.categ_id = '%s' and pt.company_id = '%s' and pt.type != 'service'
                            #~ order by 2 """ % (prod_categ_id, cate.company_id.id))
            #~ line_list = [i for i in cr.dictfetchall()]
            #~ for fid in line_list:
                #~ list_of_dict.append({"product_id":fid['prod'], "uom_id":fid['uom']})
            #~ result['value'] = {'scheme_entry_line':list_of_dict,}
        #~ return result 
        
    def submit(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        tot_obj = self.pool.get('scheme.entry.total')
        sch_val_sr = self.pool.get('rd.scheme.line').search(cr, uid, [('scheme_id', '=', obj.scheme_id.id)], context=context)
        for lin in self.pool.get('rd.scheme.line').browse(cr, uid, sch_val_sr):
            for line in obj.scheme_entry_line:
                if line.product_id.id == lin.product_id.id:
                    val = {
                     'period_id':obj.period_id.id,
                     'manager_id':obj.manager_id.id,           
                     'sr_id':obj.sr_id.id,           
                     'partner_id':obj.partner_id.id,           
                     'prod_categ_id':obj.prod_categ_id.id,           
                     'company_id':obj.company_id.id,           
                     'scheme_id':obj.scheme_id.id,           
                     'product_id':line.product_id.id,           
                     'uom_id':line.uom_id.id,           
                     'amount':line.amount,           
                     'value':lin.scheme_price,           
                     'total':lin.scheme_price * line.amount,           
                    }
                    tot_obj.create(cr, uid, val, context=context)
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
        
    def generate(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        sc_obj = self.pool.get('rd.scheme')
        sc_line_obj = self.pool.get('scheme.entry.line')
        cr.execute("""SELECT 
                          se.id
                    FROM scheme_entry se
                    WHERE se.period_id = '%s' AND se.sr_id = '%s' AND se.partner_id = '%s' AND se.prod_categ_id = '%s' AND se.id != '%s'
                     """ % (obj.period_id.id, obj.sr_id.id, obj.partner_id.id, obj.prod_categ_id.id, obj.id))
        line_list = [i for i in cr.dictfetchall()]
        if line_list:
            raise osv.except_osv(_('Error!'), _('This scheme Entry already Entered. Please generate new entry!'))
        else:
            sc_sr = sc_obj.search(cr, uid, [('prod_categ_id','=',obj.prod_categ_id.id),('period_id','=',obj.period_id.id),('state','=','progress')],context=context)
            if sc_sr:
                cr.execute("""SELECT 
                                  sel.product_id as prod,
                                  sel.uom_id as uom,
                                  coalesce(sum(sel.amount),0) as val
                            FROM scheme_entry se
                            JOIN account_period ap ON (ap.id = se.period_id)
                            JOIN sale_entry sae ON (se.prod_categ_id = sae.prod_categ_id AND se.sr_id = sae.sr_id AND se.partner_id = sae.partner_id)
                            JOIN sale_entry_line sel ON (sel.sale_entry_id = sae.id)
                            WHERE sae.date_from >= '%s' AND sae.date_from <= '%s' AND sel.amount != 0.0
                            GROUP BY sel.product_id,sel.uom_id """ % (obj.period_id.date_start, obj.period_id.date_stop))
                line_list = [i for i in cr.dictfetchall()]
                for line in line_list:
                    vals = {
                      'scheme_entry_id':obj.id,
                      'product_id':line['prod'],
                      'uom_id':line['uom'],
                      'amount':line['val'],
                      'company_id':obj.company_id.id,
                    }
                    sc_line_obj.create(cr, uid, vals, context=context)
                self.write(cr, uid, ids, {'scheme_id':sc_sr[0],'state':'progress'},context=context)
        return True
    
scheme_entry()

class scheme_entry_line(osv.osv):
    _name = 'scheme.entry.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
      'scheme_entry_id':fields.many2one('scheme.entry', 'Scheme Line'),
      'product_id':fields.many2one('product.product', 'Product', required=True, readonly=True),
      'uom_id':fields.many2one('product.uom', 'Product UOM', required=True, readonly=True),
      'amount':fields.float('Achived Quantity'),
      'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': _get_default_company,
        }
        
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        result = {}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id)
            prod_tmpl = self.pool.get('product.template').browse(cr, uid, prod.product_tmpl_id.id)
            result['value'] = {'uom_id':prod_tmpl.uom_id.id
                              }
        
        return result

scheme_entry_line()

class scheme_entry_total(osv.osv):
    _name = 'scheme.entry.total'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _columns = {
        'period_id':fields.many2one('account.period', 'Period', required=True),
        'credit':fields.boolean('credit', readonly=True),
        'manager_id': fields.many2one('res.users', 'Sales Manager', readonly=True),
        'sr_id': fields.many2one('res.users', 'Sales Representative', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Stokiest Id', readonly=True),
        'prod_categ_id':fields.many2one('product.category', 'Product Category', readonly=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'scheme_id': fields.many2one('rd.scheme', 'Scheme ID', readonly=True),
        'product_id':fields.many2one('product.product', 'Product', readonly=True),
        'uom_id':fields.many2one('product.uom', 'Product UOM', readonly=True),
        'amount':fields.float('Quantity', readonly=True),
        'value':fields.float('Value', readonly=True),
        'total':fields.float('Total Amount', readonly=True),
    }
    _defaults = {
        'company_id': _get_default_company,
        }

    
scheme_entry_total()

class scheme_credit(osv.osv):
    _name = 'scheme.credit'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
    'company_id': fields.many2one('res.company', 'Company'),
    'period_id':fields.many2one('account.period', 'Period', required=True),
    'scheme_credit_line':fields.one2many('scheme.credit.line', 'credit_id', 'Scheme Credit',readonly=True),
    'state': fields.selection([('draft', 'Draft'),('generate', 'Generated'),('done', 'Post')],'Status', readonly=True, track_visibility='always'),
    }
    
    _defaults = {
        'state':'draft',
        'company_id':_get_default_company
    
    }
    
    def generate(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        scheme = self.pool.get('scheme.entry.total')
        cr.execute("""SELECT 
                          set.partner_id as part,
                          sum(set.total) as val
                    FROM scheme_entry_total set
                    WHERE set.period_id = '%s' AND set.credit is false
                    GROUP BY set.partner_id """ % (obj.period_id.id))
        line_list = [i for i in cr.dictfetchall()]
        for line in line_list:
            val = {
                 'credit_id':obj.id,
                 'partner_id':line['part'],
                 'amount':line['val']
                  }
            self.pool.get('scheme.credit.line').create(cr, uid, val, context=context)
        return self.write(cr, uid, ids, {'state':'generate'}, context=context)
        
    def post(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        period_pool = self.pool.get('account.period')
        precision = self.pool.get('decimal.precision').precision_get(cr, uid, 'Payroll')
        timenow = time.strftime('%Y-%m-%d')
        date = timenow
        search_periods = period_pool.find(cr, uid, date, context=context)
        period_id = search_periods[0]
        name = _('RD Credit Note')
        sr_bank = self.pool.get('account.journal').search(cr, uid, [('allow_rd_writing', '=', True), ('company_id', '=', obj.company_id.id)], context=context)
        bank = self.pool.get('account.journal').browse(cr, uid, sr_bank[0])
        for line in obj.scheme_credit_line:
            move = {
                'narration': name,
                'date': timenow,
                'ref': name,
                'journal_id': bank.id,
                'period_id': period_id,
            }
            move_id = move_pool.create(cr, uid, move, context=context)
            debit_li = {
                         'move_id':move_id,
                         'name':'Debit',
                         'date': timenow,
                         'partner_id':line.partner_id.id,
                         'account_id':line.partner_id.property_account_receivable.id,
                         'journal_id':bank.id,
                         'period_id':period_id,
                         'debit':0.0,
                         'credit':line.amount,
                 }
            move_line_pool.create(cr, uid, debit_li, context=context)
            credit_li = {
                         'move_id':move_id,
                         'name':'Credit',
                         'date': timenow,
                         'partner_id':line.partner_id.id,
                         'account_id':bank.default_credit_account_id.id,
                         'journal_id':bank.id,
                         'period_id':period_id,
                         'debit':line.amount,
                         'credit':0.0,
                         }
            move_line_pool.create(cr, uid, credit_li, context=context)
        val = []
        cr.execute("""SELECT 
                          set.id as part
                    FROM scheme_entry_total set
                    WHERE set.period_id = '%s' AND set.credit is false """ % (obj.period_id.id))
        line_list = [i for i in cr.fetchall()]
        for line in line_list:
            val.append(line[0])
        cr.execute('UPDATE scheme_entry_total set credit = %s where id in %s', (True,tuple(val),))
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        sale_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in sale_orders:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete this credit note!'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)

scheme_credit()

class scheme_credit_line(osv.osv):
    _name = 'scheme.credit.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
    'company_id': fields.many2one('res.company', 'Company'),
    'credit_id': fields.many2one('scheme.credit', 'Credit ID'),
    'partner_id':fields.many2one('res.partner', 'Stokiest ID'),
    'amount':fields.float('Amount'),
    }
    
    _defaults = {
        'company_id':_get_default_company
    }
scheme_credit_line()

class sale_target(osv.osv):
    _name = 'sale.target'
    
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
        return periods and periods[0] or False
    
    _columns = {
        'period_id': fields.many2one('account.period', 'Period', required=True),
        'manager_id': fields.many2one('res.users', 'Sales Manager', required=True),
        'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
        'partner_id':fields.many2one('res.partner', 'Stokiest Id', required=True),
        'prod_categ_id':fields.many2one('product.category', 'Product Category', required=True),
        'state': fields.selection([('draft', 'submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company'),
        'sale_target_line':fields.one2many('sale.target.line', 'sale_target_id', 'Sale Target Line'),
    }
    _defaults = {
        'company_id': _get_default_company,
        'state':'draft',
        'date_from': time.strftime("%Y-%m-01"),
        'date_to': time.strftime("%Y-%m-%d"),
        'period_id': _get_period,
        'manager_id': lambda obj, cr, uid, context: uid,
        }
        
    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if manager_id:
            cr.execute("""select 
                                smr.member_id as mem_id
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['mem_id'])
        domain = {'sr_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    def onchange_sr_id(self, cr, uid, ids, sr_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if sr_id:
            cr.execute("""select 
                                id as stokiest_id
                        from res_partner
                        where user_id = '%s' and company_id = '%s' """ % (sr_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['stokiest_id'])
        domain = {'partner_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, company_id,context=None):
        result = {}
        list_of_dict=[]
        if prod_categ_id:
            cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            cr.execute("""select 
                              pp.id as prod,
                              pt.uom_id as uom,
                              pt.list_price as sale_pr,
                              pt.mrp_price as mrp 
                        from product_template pt
                        join product_product pp on (pp.product_tmpl_id = pt.id)
                        where pt.categ_id = '%s' and pt.company_id = '%s' and pt.type != 'service'
                            order by 2 """ % (prod_categ_id, cate.company_id.id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"product_id":fid['prod'], "uom_id":fid['uom']})
            result['value'] = {'sale_target_line':list_of_dict,}
        return result 
        
    def submit(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)

    def unlink(self, cr, uid, ids, context=None):
        sale_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in sale_orders:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete!'))

        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
    
sale_target()

class sale_target_line(osv.osv):
    _name = 'sale.target.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
      'sale_target_id':fields.many2one('sale.target.id', 'Sale Target'),
      'product_id':fields.many2one('product.product', 'Product', required=True, readonly=True),
      'uom_id':fields.many2one('product.uom', 'Product UOM', required=True, readonly=True),
      'amount':fields.float('Quantity'),
      'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': _get_default_company,
        }
        
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        result = {}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id)
            prod_tmpl = self.pool.get('product.template').browse(cr, uid, prod.product_tmpl_id.id)
            result['value'] = {'uom_id':prod_tmpl.uom_id.id
                              }
        
        return result

sale_target_line()

class sale_entry(osv.osv):
    _name = 'sale.entry'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
        
    _columns = {
        'date_from':fields.date('Date From'),
        'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
        'partner_id':fields.many2one('res.partner', 'Stokiest Id', required=True),
        'prod_categ_id':fields.many2one('product.category', 'Product Category', required=True),
        'state': fields.selection([('draft', 'submit'),('waiting', 'Waiting For Approval'),('done', 'Submitted'),('cancel', 'Cancel')],'Status', readonly=True, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company'),
        'sale_entry_line':fields.one2many('sale.entry.line', 'sale_entry_id', 'Sale Entry Line'),
    }
    _defaults = {
        'company_id': _get_default_company,
        'state':'draft',
        'date_from': time.strftime("%Y-%m-%d"),
        'sr_id': lambda obj, cr, uid, context: uid,
        }
        
    
    def onchange_sr_id(self, cr, uid, ids, sr_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if sr_id:
            cr.execute("""select 
                                id as stokiest_id
                        from res_partner
                        where user_id = '%s' and company_id = '%s' """ % (sr_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['stokiest_id'])
        domain = {'partner_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    #~ def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, company_id,date_from,context=None):
        #~ result = {}
        #~ list_of_dict=[]
        #~ if prod_categ_id:
            #~ cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            #~ cr.execute("""SELECT 
                               #~ t1.prod, t1.uom, coalesce(t2.amount,0) as amount, 
                               #~ coalesce(t1.sum_open,0) as sum_open, coalesce(t1.total,0) as total, 
                              #~ coalesce(t1.current_stock,0) as current_stock 
                           #~ from (
                    #~ select prod, uom, sum_open, sum(sum_amount) as total , 
                    #~ (sum_open - sum(sum_amount)) as current_stock from (
                    #~ SELECT 
                          #~ DISTINCT pp.id as prod,
                    #~ /*      ap.date_start,
                          #~ ap.date_stop, */
                          #~ pt.uom_id as uom,
                          #~ coalesce(stl.amount,0) as target_qty,
                          #~ coalesce(sol.amount + sm.product_qty,0) sum_open,
                          #~ SUM(sel.amount) as sum_amount,
                          #~ coalesce((sol.amount + sm.product_qty) - SUM(sel.amount),0) as open
                    #~ FROM product_template pt
                    #~ JOIN product_product pp on (pp.product_tmpl_id = pt.id)
                    #~ JOIN sale_target st ON (st.prod_categ_id = pt.categ_id)
                    #~ JOIN account_period ap  ON (ap.id = st.period_id)
                    #~ JOIN sale_target_line stl ON (stl.sale_target_id = st.id AND stl.product_id = pp.id)
                    #~ JOIN sale_entry se ON (se.partner_id = st.partner_id AND se.sr_id = st.sr_id AND se.prod_categ_id = st.prod_categ_id AND ap.date_start <=se.date_from AND ap.date_stop >=se.date_from)
                    #~ JOIN sale_entry_line sel ON (sel.sale_entry_id = se.id AND pp.id = sel.product_id)
                    #~ JOIN sale_open so ON (so.partner_id = se.partner_id AND so.prod_categ_id = se.prod_categ_id)
                    #~ JOIN sale_open_line sol ON (sol.sale_open_id = so.id AND sol.product_id = stl.product_id)
                    #~ LEFT JOIN stock_picking sp ON (sp.partner_id = se.partner_id)
                    #~ LEFT JOIN stock_move sm ON (sm.picking_id = sp.id AND sm.product_id = stl.product_id)
                    #~ WHERE pt.categ_id = '%s' AND pt.company_id = '%s' AND pt.type != 'service' AND se.state = 'done'
                    #~ GROUP BY pp.id,pt.uom_id,stl.amount,sol.amount,sm.product_qty--,ap.date_start,ap.date_stop
                    #~ ) t group by prod, uom, sum_open) t1 
                    #~ join (
                    #~ select ap.date_start,ap.date_stop, stl.amount, stl.product_id from sale_target st join sale_target_line stl on stl.sale_target_id=st.id
                    #~ join account_period ap on ap.id=st.period_id where ap.date_start<='%s' and ap.date_stop>='%s') t2 on t1.prod=t2.product_id
                    #~ order by 1 """ % (prod_categ_id, cate.company_id.id,date_from,date_from))
            #~ line_list = [i for i in cr.dictfetchall()]
            #~ for fid in line_list:
                #~ list_of_dict.append({"product_id":fid['prod'], "uom_id":fid['uom'], "target_qty":fid['amount'], "current_stock":fid['current_stock']})
            #~ result['value'] = {'sale_entry_line':list_of_dict,}
        #~ return result 

    def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, sr_id, partner_id, company_id, date_from, context=None):
        result = {}
        list_of_dict=[]
        if prod_categ_id:
            cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            cr.execute(""" CREATE or REPLACE VIEW table1 as ( select 
                              distinct stl.product_id as prod,
                              coalesce(stl.amount,0) as target,
                              coalesce(sol.amount,0) as open
                              
                        from sale_target st
                        JOIN sale_target_line stl on (stl.sale_target_id = st.id)
                        join sale_entry se on (se.sr_id = st.sr_id and se.partner_id = st.partner_id and se.prod_categ_id = st.prod_categ_id)
                        JOIN account_period ap ON (ap.id = st.period_id)
                        JOIN sale_open so on (so.sr_id = st.sr_id and so.partner_id = st.partner_id and so.prod_categ_id = st.prod_categ_id and ap.date_start <= se.date_from and ap.date_stop >= se.date_from)
                        JOIN sale_open_line sol on (sol.sale_open_id = so.id and stl.product_id = sol.product_id)
                        where st.state = 'done' and so.state = 'done' and so.prod_categ_id = '%s' and so.sr_id = '%s' and so.partner_id = '%s' and so.company_id = '%s') """ % (prod_categ_id, sr_id, partner_id, cate.company_id.id))
            cr.execute(""" select * from table1 """)
            line_list = [i for i in cr.dictfetchall()]
            print line_list, "KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK"
            cr.execute(""" CREATE or REPLACE VIEW table2 as (SELECT
                              sm.product_id as prod, 
                              sum(sm.product_qty) as amount
                        from stock_picking sp
                        JOIN stock_move sm ON (sm.picking_id = sp.id)
                        where sp.partner_id = '%s' and sp.company_id = '%s' 
                        group by sm.product_id ) """ % (partner_id, cate.company_id.id))
            
            cr.execute(""" CREATE or REPLACE VIEW table3 as (select 
                                  sel.product_id as prod,
                                  sum(coalesce(sel.amount,0)) as amount
                            from sale_entry se 
                            JOIN sale_entry_line sel ON (sel.sale_entry_id = se.id)
                            where se.state = 'done' and se.partner_id = '%s' and se.company_id = '%s' and se.sr_id = '%s' and se.prod_categ_id = '%s' 
                            group by sel.product_id,sel.uom_id )""" % (partner_id, cate.company_id.id,sr_id,prod_categ_id))
            
            cr.execute("""select 
                                 t1.prod as product,
                                 t1.target as target,
                                 pt.uom_id as uom,
                                 t1.open as open,
                                 (coalesce(t1.open,0) + coalesce(t2.amount,0)) - coalesce(t3.amount,0) as bal
                            from table1 t1
                            left JOIN table2 t2 on (t2.prod = t1.prod)
                            left join table3 t3 on (t3.prod = t1.prod)
                            join product_product pp on (pp.id = t3.prod)
                            join product_template pt on (pt.id = pp.product_tmpl_id)
                   """)
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                print fid, "FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF"
                list_of_dict.append({"product_id":fid['product'], "uom_id":fid['uom'], "target_qty":fid['target'], "current_stock":fid['bal']})          
        result['value'] = {'sale_entry_line':list_of_dict,}
        return result
                
    def submit(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        sc_obj = self.pool.get('scheme.entry')
        cr.execute("""SELECT 
                          se.id as val
                    FROM sale_entry se
                    WHERE se.date_from = '%s' AND se.sr_id = '%s' AND se.partner_id = '%s' AND se.prod_categ_id = '%s' AND se.id != '%s'
                   """ % (obj.date_from, obj.sr_id.id,obj.partner_id.id,obj.prod_categ_id.id,obj.id))
        line_list = [i for i in cr.dictfetchall()]
        if line_list:
            raise osv.except_osv(_('Error!'), _('This Sale entry already Entered. Please enter Newdate'))
        else:
            self.write(cr, uid, ids, {'state':'waiting'}, context=context)
        return True 
 
    def approve(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'}, context=context)
        
    def refuse(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel'}, context=context)
    
    def unlink(self, cr, uid, ids, context=None):
        sale_orders = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in sale_orders:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete!'))
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)
        
sale_entry()

class sale_entry_line(osv.osv):
    _name = 'sale.entry.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
      'sale_entry_id':fields.many2one('sale.entry', 'Sale Entry'),
      'product_id':fields.many2one('product.product', 'Product', required=True, readonly=True),
      'uom_id':fields.many2one('product.uom', 'Product UOM', required=True, readonly=True),
      'target_qty':fields.float('Target Quantity',readonly=True),
      'current_stock':fields.float('Current Stock',readonly=True),
      'amount':fields.float('Quantity'),
      'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': _get_default_company,
        }
        
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        result = {}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id)
            prod_tmpl = self.pool.get('product.template').browse(cr, uid, prod.product_tmpl_id.id)
            result['value'] = {'uom_id':prod_tmpl.uom_id.id
                              }
        return result
        
sale_target_line()

class sale_open(osv.osv):
    _name = 'sale.open'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    #~ def _get_period(self, cr, uid, context=None):
        #~ if context is None: context = {}
        #~ if context.get('period_id', False):
            #~ return context.get('period_id')
        #~ periods = self.pool.get('account.period').find(cr, uid, context=context)
        #~ return periods and periods[0] or False
    
    _columns = {
        'date_from':fields.date('From Date', required=True, readonly=True),
        'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
        'partner_id':fields.many2one('res.partner', 'Stokiest Id', required=True),
        'prod_categ_id':fields.many2one('product.category', 'Product Category', required=True),
        'state': fields.selection([('draft', 'submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
        'company_id': fields.many2one('res.company', 'Company'),
        'sale_open_line':fields.one2many('sale.open.line', 'sale_open_id', 'Sale Open Line'),
    }
    _defaults = {
        'company_id': _get_default_company,
        'state':'draft',
        'date_from': time.strftime("%Y-04-01"),
        'sr_id': lambda obj, cr, uid, context: uid,
        }
        
    
        
    def onchange_sr_id(self, cr, uid, ids, sr_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if sr_id:
            cr.execute("""select 
                                id as stokiest_id
                        from res_partner
                        where user_id = '%s' and company_id = '%s' """ % (sr_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['stokiest_id'])
        domain = {'partner_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, company_id,context=None):
        result = {}
        list_of_dict=[]
        if prod_categ_id:
            cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            cr.execute("""select 
                              pp.id as prod,
                              pt.uom_id as uom,
                              pt.list_price as sale_pr,
                              pt.mrp_price as mrp 
                        from product_template pt
                        join product_product pp on (pp.product_tmpl_id = pt.id)
                        where pt.categ_id = '%s' and pt.company_id = '%s' and pt.type != 'service'
                            order by 2 """ % (prod_categ_id, cate.company_id.id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"product_id":fid['prod'], "uom_id":fid['uom']})
            result['value'] = {'sale_open_line':list_of_dict,}
        return result 
        
    def submit(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        da = str(obj.date_from).split("-")
        print da[0], "SAAFCSFCSF"
        cr.execute("""SELECT 
                          so.id as val
                    FROM sale_open so
                    WHERE to_char(so.date_from,'YYYY') = '%s' AND so.id != '%s' AND so.sr_id = '%s' AND so.partner_id = '%s' AND so.prod_categ_id = '%s'
                   """ % (str(da[0]), obj.id, obj.sr_id.id, obj.partner_id.id, obj.prod_categ_id.id))
        line_list = [i for i in cr.dictfetchall()]
        if line_list:
            raise osv.except_osv(_('Error!'), _('Sorry already inventory have been created for this category !!!'))
        else:
            self.write(cr, uid, ids, {'state':'done'}, context=context)
            val = {'date_from':'2016-04-01',
                   'sr_id':obj.sr_id.id,
                   'partner_id':obj.partner_id.id,
                   'prod_categ_id':obj.prod_categ_id.id,
                   'state':'done'}
            ent_obj = self.pool.get('sale.entry').create(cr, uid, val, context=context)
            for line in obj.sale_open_line:
                vals = {'sale_entry_id':ent_obj,
                        'product_id':line.product_id.id,
                        'uom_id':line.uom_id.id,
                        'amount':0.00}
                self.pool.get('sale.entry.line').create(cr, uid, vals, context=context)
        return True  
    
sale_open()

class sale_open_line(osv.osv):
    _name = 'sale.open.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
      'sale_open_id':fields.many2one('sale.open', 'Sale Open'),
      'product_id':fields.many2one('product.product', 'Product', required=True, readonly=True),
      'uom_id':fields.many2one('product.uom', 'Product UOM', required=True, readonly=True),
      'amount':fields.float('Quantity'),
      'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': _get_default_company,
        }
        
    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        result = {}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id)
            prod_tmpl = self.pool.get('product.template').browse(cr, uid, prod.product_tmpl_id.id)
            result['value'] = {'uom_id':prod_tmpl.uom_id.id
                              }
        
        return result

sale_open_line()
