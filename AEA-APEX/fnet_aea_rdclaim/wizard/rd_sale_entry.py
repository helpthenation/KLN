# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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
from openerp import api, models,_

import time
from datetime import datetime
from dateutil import relativedelta
import xlwt
from xlsxwriter.workbook import Workbook
from cStringIO import StringIO
import base64
from openerp.osv import fields, osv
from openerp.tools.translate import _
import os
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from openerp import SUPERUSER_ID,api
from openerp.addons.report_xls import report_xls
import time
from lxml import etree
from itertools import groupby
import itertools
from operator import itemgetter
from openerp.osv.orm import setup_modifiers


class rdsale_entries(osv.osv_memory):
    _name = 'rdsale.entries'
    
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

    _description = 'RD Sale Entry Analysis'
    
    _columns = { 
          'period_from': fields.many2one('account.period', 'Period From'),
          'period_to': fields.many2one('account.period', 'Period To'),
          'date_from':fields.date('Date From'),
          'date_to':fields.date('Date To'), 
          'company_id': fields.many2one('res.company', 'Company',readonly=True),
          'prod_categ_id':fields.many2one('product.category', 'Product Category',required=True),
          'manager_id': fields.many2one('res.users', string='Sales Manager'),
          'sr_id': fields.many2many('res.users', string='Sales Representative'),
          'is_open':fields.boolean('Opening'),
          'is_awd':fields.boolean('AW To Stockiest'),
          'is_sale':fields.boolean('RD Sale'),
          'is_closing':fields.boolean('Closing'),
          'filter': fields.selection(
            [('filter_no', 'No Filters'),
             ('filter_date', 'Date')], "Filter by", 
            default='filter_date'),
    }

    _defaults = {
         'company_id': _get_default_company,
         'is_open':True, 
         'is_awd':True,
         'is_sale':True,
         'is_closing':True,
         #~ 'manager_id':_get_manager_ids
    }
                  
        
    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id,context=None):
        res = {}
        domain = []
        result = {} 
        list_li=[]
        if manager_id:                         
            cr.execute("""select 
                                    smr.member_id as mem_id
                            from crm_case_section ccs
                            join sale_member_rel smr on (smr.section_id = ccs.id)
                            where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            sid=[]
            for fid in line_list:
                list_li.append(fid['mem_id'])
            result={
                 'value':
                     {
                      'sr_id':list_li,                      
                     },
                 'domain': {'sr_id':[('id', 'in', tuple(list_li))]}  
                   }

            return result
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:context = {}
        res = super(rdsale_entries, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        if context.get('active_model', False) == 'rdsale.entries':
            doc = etree.XML(res['arch'])
            nodes = doc.xpath("//field[@name='company_id']")
            for node in nodes:
                node.set('readonly', '1')
                node.set('help', 'If you print the report from Account list/form view it will not consider Charts of account')
                setup_modifiers(node, res['fields']['company_id'])
            res['arch'] = etree.tostring(doc)
        return res
    def onchange_filter(self, cr, uid, ids, filter='filter_no',context=None):
        res = {}
        if filter == 'filter_no':
            res['value'] = {
                'period_from': False,
                'period_to': False,
                'date_from': False,
                'date_to': False,
            }
        if filter == 'filter_date':
            date_from, date_to = time.strftime(
                    '%Y-01-01'), time.strftime('%Y-%m-%d')
            res['value'] = {
                'period_from': False,
                'period_to': False,
                'date_from': date_from,
                'date_to': date_to
            }

        if filter == 'filter_period':
            start_period = end_period = False
            cr.execute('''
                    SELECT * FROM (SELECT p.id
                               FROM account_period p                               
                               WHERE COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_start ASC
                               LIMIT 1) AS period_start
                UNION ALL
                SELECT * FROM (SELECT p.id
                               FROM account_period p
                               
                               WHERE 
                                p.date_start < NOW()
                               AND COALESCE(p.special, FALSE) = FALSE
                               ORDER BY p.date_stop DESC
                               LIMIT 1) AS period_stop''')
            periods = [i[0] for i in cr.fetchall()]
            if periods:
                start_period = end_period = periods[0]
                if len(periods) > 1:
                    end_period = periods[1]
            res['value'] = {'period_from': start_period, 'period_to':
                            end_period, 'date_from': False, 'date_to': False}            
        return res        
    def pre_print_report(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        data['form'].update(self.read(cr, uid, ids,[
                           'date_from',  'date_to', 
                            'period_from', 'period_to',
                             'filter', 'company_id',
                             'prod_categ_id',
                              'manager_id',
                               'sr_id','is_open', 'is_awd','is_sale','is_closing'
                           ], context=context)[0])
        return data

    def xls_export(self, cr, uid, ids, context=None):
        return self.check_report(cr, uid, ids, context=context)
    def _build_contexts(self, cr, uid, ids, data, context=None):
        if context is None:
            context = {}
        result = {}
        result['company_id'] = 'company_id' in data['form'] and data['form']['company_id'] or False
        result['prod_categ_id'] = 'prod_categ_id' in data['form'] and data['form']['prod_categ_id'] or False
        result['manager_id'] = 'manager_id' in data['form'] and data['form']['manager_id'] or False
        result['sr_id'] = 'sr_id' in data['form'] and data['form']['sr_id'] or False
        if data['form']['filter'] == 'filter_date':
            result['date_from'] = data['form']['date_from']
            result['date_to'] = data['form']['date_to']
        if data['form']['filter'] == 'filter_period':
            if not data['form']['period_from'] or not data['form']['period_to']:
                raise osv.except_osv(_('Error!'),_('Select a starting and an ending period.'))
            result['period_from'] = data['form']['period_from']
            result['period_to'] = data['form']['period_to']
        return result
    def _print_report(self, cr, uid, ids, data, context=None):
        data = self.pre_print_report(cr, uid, ids, data, context=context)
        context = context or {}
        if context.get('xls_export'):
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'fnet_aea_rdclaim.rdsale_entries_xlsx.xlsx',
                    'datas': data,}
        else:
            return {'type': 'ir.actions.report.xml',
                    'report_name': 'fnet_aea_rdclaim.report_rdsale_entries',
                    'datas': data,
                     'res_model':'rdsale.entries',}
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, [
        'date_from',  'date_to', 
                                                               'period_from', 'period_to',
                                                                'filter', 'company_id',
                                                                'prod_categ_id',
                                                                'manager_id',
                                                                  'sr_id',
                                                                  'is_open', 'is_awd','is_sale','is_closing' ], context=context)[0]
        for field in ['period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)

class ParticularReport(models.AbstractModel):
   
    _name = 'report.fnet_aea_rdclaim.report_rdsale_entries'
    
    
    def _get_sale_entries_product(self,data):
        self.env.cr.execute("""SELECT DISTINCT
                                      pp.id as product_id,
                                      pp.name_template,
                                      pp.default_code,
                                      pt.categ_id
                                      From
                                      product_template pt
                                      JOIN product_product pp ON pp.product_tmpl_id = pt.id
                                      WHERE pt.categ_id=%d  and pt.company_id=%s and pp.name_template::text not like '%s'
                                      ORDER BY pp.default_code ASC"""%(data['form']['prod_categ_id'][0],data['form']['company_id'][0],'%ROUND%'))
        line_list = [i for i in self.env.cr.dictfetchall()]
        return line_list
            
    def _get_stockiest_line(self,data):
        head=self._get_sale_entries_product(data)
        final_list=[]
        date_query=''
        if data['form']['date_from'] and data['form']['date_to']:
            date_query=" and se.date_from >= '%s' and se.date_from <= '%s' "%(data['form']['date_from'],data['form']['date_to'])        
        manager_list=[]
        if  data['form']['manager_id']:
            manager_list.append(data['form']['manager_id'][0])
        else:
            self.env.cr.execute("""select distinct user_id as id from crm_case_section where company_id = %d"""%(data['form']['company_id'][0]))
            sale_rep=self.env.cr.dictfetchall()
            for rec in  sale_rep:
                manager_list.append(rec['id'])
        #~ print'RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR',manager_list
        if manager_list != []:
            for m in manager_list:
                ss=[]
                user = self.env['res.users'].browse(m)
                self.env.cr.execute("""select sml.member_id as id from res_users rs 
                    join crm_case_section ccs on ccs.user_id = rs.id 
                    join sale_member_rel sml on ccs.id = sml.section_id
                    where ccs.user_id = %d """%(m))
                sr_list=self.env.cr.dictfetchall()
                #~ print'SRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR',sr_list
                if sr_list != []:
                    
                    for k in sr_list:
                        stockiest_list = []
                        self.env.cr.execute("""SELECT DISTINCT
                                      res_partner.name,res_partner.city,res_partner.id
                                      FROM res_partner
                                      JOIN res_users on res_users.id = res_partner.user_id where  res_users.id = %d and res_partner.company_id=%s
                                      ORDER BY res_partner.id ASC"""%(k['id'],data['form']['company_id'][0]))
                        line_list =  self.env.cr.dictfetchall()
                        self.env.cr.execute("""select name,city from res_partner join res_users on res_users.partner_id=res_partner.id where res_users.id=%d and res_partner.company_id=%s """%(k['id'],data['form']['company_id'][0]))
                        stockiest= self.env.cr.dictfetchall()
                        salesrep_qty=[]
                        for j in line_list:
                            slist=[]
                            awt=[]
                            #~ print'^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^',j['id'],data['form']['prod_categ_id'][0],data['form']['company_id'][0],date_query
                            prod = self.env['res.partner'].browse(j['id'])
                            self.env.cr.execute("""
                                    SELECT pp.default_code as code,
                                    coalesce(sum(sel.amount),0.0) as quantity,
                                    coalesce(sum(sel.current_stock),0.0) as opening,
                                    coalesce(sum(sel.sale_stock),0.0) as sale,
                                    coalesce(coalesce(sum(sel.current_stock),0.0) + coalesce(sum(sel.sale_stock),0.0)  - coalesce(sum(sel.amount),0.0),0.0) as closing
                                    FROM  sale_entry  se
                                    left join sale_entry_line sel on se.id = sel.sale_entry_id
                                    left join product_product pp on pp.id = sel.product_id
                                    where se.partner_id=%d and se.prod_categ_id=%d and se.company_id=%d %s
                                    group by pp.default_code
                                    order by pp.default_code asc
                                
                                """%(j['id'],data['form']['prod_categ_id'][0],data['form']['company_id'][0],date_query))
                            OPEN_list = [q for q in self.env.cr.dictfetchall()]
                            salesrep_qty.extend(OPEN_list)
                            
                            if OPEN_list != []:
                                slist.append({'opening':OPEN_list})
                                stockiest_list.append({'name':prod.name,'city':prod.city,'lines':slist})
                        #~ ss.append({'saleperson':stockiest[0]['name'],
                            #~ 'sp_city':stockiest[0]['city'],
                            #~ 'customer_lines':stockiest_list})
                        salerep_total=sorted(salesrep_qty,key=itemgetter('code'))
                        grouped_salerep_total={}
                        for key,value in itertools.groupby(salerep_total,key=itemgetter('code')):
                            for i in value:
                                grouped_salerep_total.setdefault(key, []).append(i) 
                        sales_reps_totals=[]
                        for key,value in sorted(grouped_salerep_total.iteritems()):
                            opening=0.0 
                            rd=0.0  
                            awd=0.0
                            close=0.0
                            for val in value:
                                opening+=val['opening']
                                rd+=val['quantity']
                                awd+=val['sale']
                                close+=val['closing']
                            sales_reps_totals.append({'code':key,'opening':opening,'awd':awd,'rd':rd,'close':close})      
                        #~ print'OE###############################################',   sales_reps_totals
                        ss.append({'saleperson':stockiest[0]['name'],
                            'sp_city':stockiest[0]['city'],
                            'customer_lines':stockiest_list,                        
                            'sales_reps_totals':sales_reps_totals})                     
                final_list.append({'manager_name':user.login,'salesrep':ss})      
        #~ print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',final_list
        return final_list               
    def _get_sale_entries_categ_name(self,data):
        if data['form']['prod_categ_id']:
            return data['form']['prod_categ_id'][1]
        else:           
            return  None  
    def _get_sale_manager_name(self,data):
        if data['form']['manager_id']:
            return data['form']['manager_id'][1]
        else:
            return "N/A"
            
    def generate_pdf_report(self, data, obj):
        product_name=self._get_sale_entries_product(data)
        stockiest_line=self._get_stockiest_line(data)
        product_categ=self._get_sale_entries_categ_name(data)      
        sales_manager=self._get_sale_manager_name(data)      

    @api.multi
    def render_html(self, data=None):
        #~ print'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',data
        report_obj = self.env['report']
        rdsale_report = report_obj._get_report_from_name('fnet_aea_rdclaim.report_rdsale_entries')
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        obj = self.env['rdsale.entries'].browse(active_ids)
        docargs = {
            'doc_ids': self.ids,
            'doc_model': rdsale_report.model,
            'docs': obj,
            'data': data,
            'product_categ':self._get_sale_entries_categ_name,
            'sales_manager':self._get_sale_manager_name ,
            'product_name':self._get_sale_entries_product ,
            'stockiest_line':self._get_stockiest_line,
        }
        return report_obj.render('fnet_aea_rdclaim.report_rdsale_entries', docargs)
        
