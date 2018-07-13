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


class purchase_register_consolidate_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(purchase_register_consolidate_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date': self._get_date,
                'get_product_category': self._get_product_category,
                'get_product_qty_april':self._get_product_qty_april,
                'get_product_qty_may':self._get_product_qty_may,
                'get_product_qty_june':self._get_product_qty_june,
                'get_product_qty_july':self._get_product_qty_july,
                'get_product_qty_august':self._get_product_qty_august,
                'get_product_qty_september':self._get_product_qty_september,
                'get_product_qty_october':self._get_product_qty_october,
                'get_product_qty_november':self._get_product_qty_november,
                'get_product_qty_december':self._get_product_qty_december,
                'get_product_qty_jan':self._get_product_qty_jan,
                'get_product_qty_feb':self._get_product_qty_feb,
                'get_product_qty_march':self._get_product_qty_march,
                'get_product_qty_total':self._get_product_qty_total,
                'get_product_qty_april_total':self._get_product_qty_april_total,
                'get_product_qty_may_total':self._get_product_qty_may_total,
                'get_product_qty_june_total':self._get_product_qty_june_total,
                'get_product_qty_july_total':self._get_product_qty_july_total,
                'get_product_qty_august_total':self._get_product_qty_august_total,
                'get_product_qty_september_total':self._get_product_qty_september_total,
                'get_product_qty_october_total':self._get_product_qty_october_total,
                'get_product_qty_november_total':self._get_product_qty_november_total,
                'get_product_qty_dec_total':self._get_product_qty_dec_total,
                'get_product_qty_jan_total':self._get_product_qty_jan_total,
                'get_product_qty_feb_total':self._get_product_qty_feb_total,
                'get_product_qty_march_total':self._get_product_qty_march_total,
                'get_april_total_value':self._get_april_total_value,
                'get_may_total':self._get_may_total,
                'get_june_total':self._get_june_total,
                'get_july_total':self._get_july_total,
                'get_august_total':self._get_august_total,
                'get_september_total':self._get_september_total,
                'get_october_total':self._get_october_total,
                'get_november_total':self._get_november_total,
                'get_dec_total':self._get_dec_total,
                'get_jan_total':self._get_jan_total,
                'get_feb_total':self._get_feb_total,
                'get_march_total':self._get_march_total,
                'get_total':self._get_total,
                
        })

    def _get_date(self, data):
        val = []
        res = {}
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        now = time.strftime("%Y-%m-%d")
        res['from_date']=from_date
        res['to_date']=to_date
        res['now']=now
        val.append(res)
        return val
        
    def _get_product_category(self, data):
        month = []
        where_sql=[]
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                for ide in data['form']['company_ids']:
                    where_sql.append("sm.company_id=%s" % str(ide))
                self.cr.execute("select pt.default_code, sm.product_id, pc.categ_id,pc.name as product, pcc.name as category,sum(sm.product_qty) as qty, (sum(sm.product_qty)*pc.list_price) as price  from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            else:
                cmpn = ()
                for idek in data['form']['company_ids']:
                    cmpn = cmpn + (idek,)
                where_sql.append("sm.company_id in %s" % str(cmpn))
                self.cr.execute("select pt.default_code, sm.product_id, pc.categ_id,pc.name as product, pcc.name as category,sum(sm.product_qty) as qty, (sum(sm.product_qty)*pc.list_price) as price  from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(from_date[0]),str(to_date[0]),str(cmpn)))
        line_list = [i for i in self.cr.dictfetchall()]
        dic_cus={}
        for cus in line_list:
            dic_cus[cus['category']]=[]
        for cus in line_list:
            dic_cus[cus['category']].append([cus['product'],cus['product_id'],cus['default_code'],cus['category'],cus['categ_id'],cus['qty'],cus['price'],month])
        return dic_cus
    
    def _get_product_qty_april(self,data,product,month):
        if 4 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_may(self,data,product,month):
        if 5 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_june(self,data,product,month):
        if 6 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_july(self,data,product,month):
        if 7 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_august(self,data,product,month):
        if 8 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-31'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_september(self,data,product,month):
        if 9 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_october(self,data,product,month):
        if 10 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-30'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_november(self,data,product,month):
        if 11 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_november(self,data,product,month):
        if 11 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_december(self,data,product,month):
        if 12 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_jan(self,data,product,month):
        if 1 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-31'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_feb(self,data,product,month):
        if 1 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_march(self,data,product,month):
        if 1 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),product))
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select sum(sm.product_qty) as qty from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and sm.product_id='%s'group by pt.default_code,sm.product_id, pc.categ_id, pc.name , pcc.name,pc.list_price" % (str(f_date),str(t_date),str(cmpn),product))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list==[]:
                lis=[]
                val={}
                qty=0
                val['qty']=qty
                lis.append(val)
                return lis
            else:
                return line_list   
        else:
            lis=[]
            val={}
            qty=0
            val['qty']=qty
            lis.append(val)
            return lis
            
    def _get_product_qty_total(self,data,category,categ_id):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        qty=0
        total=0
        lis=[]
        val={}
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2)  as qty,ROUND(sum(sm.product_qty*pc.list_price)::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id = '%s' and pc.categ_id='%s'" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),categ_id))
                total_list=[i for i in self.cr.dictfetchall()]
                for value in total_list:
                    if value['qty'] !=None:               
                        qty=qty+value['qty']
                        total=total+value['total']
            else:
                cmpn = ()
                for idek in data['form']['company_ids']:
                    cmpn = cmpn + (idek,)
                self.cr.execute("select id from product_category where name='%s'"%(category))
                categ_list=[i for i in self.cr.dictfetchall()]
                for record in categ_list:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty,ROUND(sum(sm.product_qty*pc.list_price)::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(from_date[0]),str(to_date[0]),str(cmpn),record['id']))
                    total_list=[i for i in self.cr.dictfetchall()]
                    for value in total_list:
                        if value['qty'] !=None:               
                            qty=qty+value['qty']
                            total=total+value['total']                  
        line_list = [i for i in self.cr.dictfetchall()]
        val['qty']=qty
        val['total']=total
        lis.append(val)
        return lis
    
    def _get_product_qty_april_total(self,data,category,categ_id,month):
        if 4 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
     
    def _get_product_qty_may_total(self,data,category,categ_id,month):
        if 5 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_june_total(self,data,category,categ_id,month):
        if 6 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_july_total(self,data,category,categ_id,month):
        if 7 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_august_total(self,data,category,categ_id,month):
        if 6 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_september_total(self,data,category,categ_id,month):
        if 9 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_october_total(self,data,category,categ_id,month):
        if 10 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_november_total(self,data,category,categ_id,month):
        if 11 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_dec_total(self,data,category,categ_id,month):
        if 12 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_jan_total(self,data,category,categ_id,month):
        if 1 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_feb_total(self,data,category,categ_id,month):
        if 2 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_product_qty_march_total(self,data,category,categ_id,month):
        if 3 in month:
            from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
            to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s' and pc.categ_id='%s' " % (str(f_date),str(t_date),str(data['form']['company_ids'][0]),categ_id))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['qty']=qty
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select id from product_category where name='%s'"%(category))
                    categ_list=[i for i in self.cr.dictfetchall()]
                    for record in categ_list:
                        self.cr.execute("select ROUND(sum(sm.product_qty)::numeric,2) as qty, ROUND(sum(sm.product_qty*pc.list_price)/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s and pc.categ_id='%s'" % (str(f_date),str(t_date),str(cmpn),record['id']))
                        total_list=[i for i in self.cr.dictfetchall()]
                        for value in total_list:
                            if value['qty'] !=None:               
                                qty=qty+value['qty']
                                total=total+value['total']
                    val['qty']=qty
                    val['total']=total/1000
                    lis.append(val)
                    return lis  
        else:
            lis=[]
            val={}
            val['qty']=0
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_total(self,data):
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        total=0
        lis=[]
        val={}
        if 'company_ids' in data['form']:
            if len(data['form']['company_ids']) < 2:
                self.cr.execute("select ROUND(sum(sm.product_qty*pc.list_price)::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
                line_list = [i for i in self.cr.dictfetchall()]
                if line_list==[]:
                    val['total']=total
                    lis.append(val)
                    return lis
                else:
                    return line_list 
            else:
                cmpn = ()
                for idek in data['form']['company_ids']:
                    cmpn = cmpn + (idek,)
                self.cr.execute("select ROUND(sum(sm.product_qty*pc.list_price)::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(from_date[0]),str(to_date[0]),str(cmpn)))
                line_list = [i for i in self.cr.dictfetchall()]
                if line_list==[]:
                    val['total']=total
                    lis.append(val)
                    return lis
                else:
                    return line_list
                    
    def _get_april_total_value(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 4 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-04-01'
            t_date=str(to_year)+'-04-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s" % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_may_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 5 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-05-01'
            t_date=str(to_year)+'-05-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_june_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 6 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-06-01'
            t_date=str(to_year)+'-06-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_july_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 7 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-07-01'
            t_date=str(to_year)+'-07-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_august_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 8 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-08-01'
            t_date=str(to_year)+'-08-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_september_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 9 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-09-01'
            t_date=str(to_year)+'-09-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_october_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)
        if 10 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-10-01'
            t_date=str(to_year)+'-10-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_november_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)		
        if 11 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-11-01'
            t_date=str(to_year)+'-11-30'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_dec_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)		
        if 12 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-12-01'
            t_date=str(to_year)+'-12-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_jan_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)		
        if 1 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-01-01'
            t_date=str(to_year)+'-01-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_feb_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)		
        if 2 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-02-01'
            t_date=str(to_year)+'-02-29'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    def _get_march_total(self,data):
        month = []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        from_month=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().month
        to_month=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().month
        for i in range(from_month, to_month+1):
            month.append(i)		
        if 3 in month:
            from_year=datetime.strptime(str(from_date[0]), "%Y-%m-%d").date().year
            to_year=datetime.strptime(str(to_date[0]), "%Y-%m-%d").date().year
            f_date= str(from_year) +'-03-01'
            t_date=str(to_year)+'-03-31'
            qty=0
            total=0
            lis=[]
            val={}
            if 'company_ids' in data['form']:
                if len(data['form']['company_ids']) < 2:
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id='%s'" % (str(f_date),str(t_date),str(data['form']['company_ids'][0])))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list 
                else:
                    cmpn = ()
                    for idek in data['form']['company_ids']:
                        cmpn = cmpn + (idek,)
                    self.cr.execute("select ROUND((sum(sm.product_qty*pc.list_price))/1000::numeric,2) as total from stock_move sm JOIN product_product pt on (pt.id=sm.product_id) Join product_template pc on (pt.product_tmpl_id=pc.id) Join product_category pcc on (pc.categ_id=pcc.id) JOIN stock_picking_type spt on (spt.id=sm.picking_type_id) where spt.code='incoming' and sm.origin_returned_move_id is NULL and sm.create_date >= '%s' and sm.create_date <= '%s' and sm.company_id in %s " % (str(f_date),str(t_date),str(cmpn)))
                    line_list = [i for i in self.cr.dictfetchall()]
                    if line_list==[]:
                        val['total']=total
                        lis.append(val)
                        return lis
                    else:
                        return line_list
        else:
            lis=[]
            val={}
            val['total']=0
            lis.append(val)
            return lis
            
    

                    
        
        
class wrapped_purchase_register_consolidate_report(osv.AbstractModel):
    _name = 'report.fnet_aea_sale_report.report_purchase_register_consolidate'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_sale_report.report_purchase_register_consolidate'
    _wrapped_report_class = purchase_register_consolidate_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
