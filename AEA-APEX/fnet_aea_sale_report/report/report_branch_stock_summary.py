#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import osv
from openerp.report import report_sxw
from datetime import datetime, timedelta
import time


class stock_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(stock_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date':self._get_date,
                'get_product_category': self._get_product_category,
                'get_product':self._get_product,
                'get_open_qty':self._get_open_qty,
                'get_open_value':self._get_open_value,
                'get_tot_open_qty':self._get_tot_open_qty,
                'get_tot_open_value':self._get_tot_open_value,
                'get_grand_open_qty':self._get_grand_open_qty,
                'get_grand_open_value':self._get_grand_open_value,
                'get_com':self._get_com,
        })

    def _get_date(self, data):
        val = []
        res = {}
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        now = time.strftime("%Y-%m-%d")
        res['from_date']=from_date
        res['now']=now
        val.append(res)
        return val
        
    def _get_product_category(self, data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        self.cr.execute(" select distinct pcc.name "\
                            " from stock_move sm "\
                            " JOIN product_product pt on (pt.id=sm.product_id)"\
                            " Join product_template pc on (pt.product_tmpl_id=pc.id)"\
                            " Join product_category pcc on (pc.categ_id=pcc.id)"\
                            " where to_char(sm.date, 'YYYY-MM-DD') = '%s' "\
                            " and sm.company_id in %s "\
                            "order by 1" % (str(from_date[0]),tuple(com[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_product(self,data,val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        self.cr.execute(" select distinct pt.name_template as prod,pt.default_code as code"\
                            " from stock_move sm "\
                            " JOIN product_product pt on (pt.id=sm.product_id)"\
                            " Join product_template pc on (pt.product_tmpl_id=pc.id)"\
                            " Join product_category pcc on (pc.categ_id=pcc.id)"\
                            " Join product_uom pu on (pu.id=pc.uom_id)"\
                            " where to_char(sm.date, 'YYYY-MM-DD') = '%s' "\
                            " and sm.company_id in %s "\
                            " and pcc.name='%s' "\
                            "order by 1" % (str(from_date[0]),tuple(com[0]),str(val)))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_open_qty(self,data,code,vals):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        wizard=self.pool.get('stock.history')
        domain=[]
        date=['date','<=',from_date[0]]
        domain.append(date)
        fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
        groupby=['product_id', 'location_id','company_id']
        res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
        li = []
        gi=[]
        g = {}
        value = 0.0
        for rec in res:
            quan=(rec['product_id'][0],rec['quantity'],rec['company_id'])
            li.append(quan)
        for li1 in li:
            prod = self.pool.get('product.product').browse(self.cr, self.uid, li1[0])
            g = (prod.default_code,li1[1],li1[2])
            gi.append(g)
        get = [item for item in gi if item[0] == code and item[2] in vals]
        my_set = {x[0] for x in get}
        my_sums = [(i,sum(x[1] for x in get if x[0] == i)) for i in my_set]
        if get:
            value = my_sums[0][1]
            return value
        else:
            value = 0.0
            return value
            
    def _get_open_value(self,data,code,vals):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        wizard=self.pool.get('stock.history')
        domain=[]
        date=['date','<=',from_date[0]]
        domain.append(date)
        fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
        groupby=['product_id', 'location_id','company_id']
        res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
        li = []
        gi=[]
        g = {}
        value = 0.0
        for rec in res:
            quan=(rec['product_id'][0],rec['inventory_value'],rec['company_id'])
            li.append(quan)
        for li1 in li:
            prod = self.pool.get('product.product').browse(self.cr, self.uid, li1[0])
            g = (prod.default_code,li1[1],li1[2])
            gi.append(g)
        get = [item for item in gi if item[0] == code and item[2] in vals]
        my_set = {x[0] for x in get}
        my_sums = [(i,sum(x[1] for x in get if x[0] == i)) for i in my_set]
        if get:
            value = my_sums[0][1]
            valu = "%.2f" % value
            return valu
        else:
            value = 0.0
            return value    
            
    def _get_tot_open_qty(self,data,prod,company_id):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        wizard=self.pool.get('stock.history')
        domain=[]
        date=['date','<=',from_date[0]]
        domain.append(date)
        fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
        groupby=['product_categ_id','product_id', 'location_id']
        res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
        li = []
        gi = []
        g = {}
        value = 0.0
        for rec in res:
            quan=(rec['product_categ_id'][0],rec['quantity'],rec['company_id'])
            li.append(quan)
        for li1 in li:
            prods = self.pool.get('product.category').browse(self.cr, self.uid, li1[0])
            g = (prods.name,li1[1],li1[2])
            gi.append(g)
        get = [item for item in gi if item[0] == prod and item[2] in company_id]
        if get:
            lol = 0.0
            for lin in get:
                lol += lin[1]
            value = lol
        else:
            value = 0.0
        return value    
        
    def _get_tot_open_value(self,data,prod,company_id):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        wizard=self.pool.get('stock.history')
        domain=[]
        date=['date','<=',from_date[0]]
        domain.append(date)
        fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
        groupby=['product_categ_id','product_id', 'location_id']
        res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
        li = []
        gi = []
        g = {}
        value = 0.0
        for rec in res:
            quan=(rec['product_categ_id'][0],rec['inventory_value'],rec['company_id'])
            li.append(quan)
        for li1 in li:
            prods = self.pool.get('product.category').browse(self.cr, self.uid, li1[0])
            g = (prods.name,li1[1],li1[2])
            gi.append(g)
        get = [item for item in gi if item[0] == prod and item[2] in company_id]
        if get:
            lol = 0.0
            for lin in get:
                lol += lin[1]
            valu = "%.2f" % lol
            return valu            
        else:
            value = 0.0
        return value  
        
    def _get_grand_open_qty(self,data,company_id):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        wizard=self.pool.get('stock.history')
        domain=[]
        date=['date','<=',from_date[0]]
        domain.append(date)
        fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
        groupby=['product_categ_id','product_id', 'location_id']
        res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
        li = []
        value = 0.0
        for rec in res:
            quan=(rec['quantity'],rec['company_id'])
            li.append(quan)
        get = [item for item in li if item[1] in company_id]
        if get:
            lol = 0.0
            for lin in get:
                lol += lin[0]
            value = lol
        else:
            value = 0.0
        return value   
        
    def _get_grand_open_value(self,data,company_id):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        wizard=self.pool.get('stock.history')
        domain=[]
        date=['date','<=',from_date[0]]
        domain.append(date)
        fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
        groupby=['product_categ_id','product_id', 'location_id']
        res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
        li = []
        value = 0.0
        for rec in res:
            quan=(rec['inventory_value'],rec['company_id'])
            li.append(quan)
        get = [item for item in li if item[1] in company_id]
        if get:
            lol = 0.0
            for lin in get:
                lol += lin[0]
            valu = "%.2f" % lol
            return valu 
        else:
            value = 0.0
        return value                                    
        
            
    def _get_com(self,val):
        na = self.pool.get('res.company').browse(self.cr, self.uid, val)
        if na.name[0:3] == 'AEA':
            na1 = 'Associated Electrical Agencies'
            return na1
        else:
            na1 = 'Apex Agencies'
            return na1
        
class wrapped_stock_ledger_summary(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_stock_summary'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_stock_summary'
    _wrapped_report_class = stock_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
