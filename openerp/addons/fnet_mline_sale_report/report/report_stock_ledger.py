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


class stock_ledger_summary_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(stock_ledger_summary_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_date':self._get_date,
                'get_product_category': self._get_product_category,
                'get_product':self._get_product,
                'get_open_qty':self._get_open_qty,
                'get_pur_qty':self._get_pur_qty,
                #~ 'get_branch_pur_qty':self._get_branch_pur_qty,
                'get_sale_ret_qty':self._get_sale_ret_qty,
                'get_sale_qty':self._get_sale_qty,
                #~ 'get_branch_sale_qty':self._get_branch_sale_qty,
                'get_purchase_ret_qty':self._get_purchase_ret_qty,
                'get_close_qty':self._get_close_qty,
                'get_value':self._get_value,
                'get_tot_open_qty':self._get_tot_open_qty,
                'get_tot_pur_qty':self._get_tot_pur_qty,
                #~ 'get_tot_branch_pur_qty':self._get_tot_branch_pur_qty,
                'get_tot_sale_ret_qty':self._get_tot_sale_ret_qty,
                'get_tot_sale_qty':self._get_tot_sale_qty,
                #~ 'get_tot_branch_sale_qty':self._get_tot_branch_sale_qty,
                'get_tot_purchase_ret_qty':self._get_tot_purchase_ret_qty,
                'get_tot_close_qty':self._get_tot_close_qty,
                'get_tot_value':self._get_tot_value,
                'get_grand_open_qty':self._get_grand_open_qty,
                'get_grand_pur_qty':self._get_grand_pur_qty,
                #~ 'get_grand_branch_pur_qty':self._get_grand_branch_pur_qty,
                'get_grand_sale_ret_qty':self._get_grand_sale_ret_qty,
                'get_grand_sale_qty':self._get_grand_sale_qty,
                #~ 'get_grand_branch_sale_qty':self._get_grand_branch_sale_qty,
                'get_grand_purchase_ret_qty':self._get_grand_purchase_ret_qty,
                'get_grand_close_qty':self._get_grand_close_qty,
                'get_grand_value':self._get_grand_value,
                'get_com':self._get_com,
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
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select distinct pc.categ_id, pcc.name "\
                                " from stock_move sm "\
                                " JOIN product_product pt on (pt.id=sm.product_id)"\
                                " Join product_template pc on (pt.product_tmpl_id=pc.id)"\
                                " Join product_category pcc on (pc.categ_id=pcc.id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            line_list = [i for i in self.cr.dictfetchall()]
        else:
            self.cr.execute(" select distinct pcc.name "\
                                " from stock_move sm "\
                                " JOIN product_product pt on (pt.id=sm.product_id)"\
                                " Join product_template pc on (pt.product_tmpl_id=pc.id)"\
                                " Join product_category pcc on (pc.categ_id=pcc.id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_product(self,data,val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select distinct pt.id as id,pt.name_template as prod, pt.default_code as code, pu.name as uom "\
                                " from stock_move sm "\
                                " JOIN product_product pt on (pt.id=sm.product_id)"\
                                " Join product_template pc on (pt.product_tmpl_id=pc.id)"\
                                " Join product_category pcc on (pc.categ_id=pcc.id)"\
                                " Join product_uom pu on (pu.id=pc.uom_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and pcc.id=%s "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),val))
            line_list = [i for i in self.cr.dictfetchall()]
        else:
            self.cr.execute(" select distinct pt.name_template as prod, pt.default_code as code, pu.name as uom "\
                                " from stock_move sm "\
                                " JOIN product_product pt on (pt.id=sm.product_id)"\
                                " Join product_template pc on (pt.product_tmpl_id=pc.id)"\
                                " Join product_category pcc on (pc.categ_id=pcc.id)"\
                                " Join product_uom pu on (pu.id=pc.uom_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pcc.name='%s' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),str(val)))
            line_list = [i for i in self.cr.dictfetchall()]
        return line_list
        
    def _get_open_qty(self,data,vals):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        from_datetime=from_date[0] + '00:00:00'
        wizard=self.pool.get('stock.history')
        if len(com[0]) < 2:
            domain=[]
            date=['date','<=',from_date[0]]
            domain.append(date)
            fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_id'][0],rec['quantity'])
                li.append(quan)
            get = [item for item in li if item[0] == vals]
            if get:
                value = get[0][1]
                return value
            else:
                value = 0.0
                return value
        else:
            domain=[]
            date=['date','<=',from_date[0]]
            domain.append(date)
            fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            gi = []
            g = {}
            value = 0.0
            for rec in res:
                quan=(rec['product_id'][0],rec['quantity'])
                li.append(quan)
            for li1 in li:
                prod = self.pool.get('product.product').browse(self.cr, self.uid, li1[0])
                g = (prod.default_code,li1[1])
                gi.append(g)
            get = [item for item in gi if item[0] == vals]
            my_set = {x[0] for x in get}
            my_sums = [(i,sum(x[1] for x in get if x[0] == i)) for i in my_set]
            if get:
                value = my_sums[0][1]
                return value
            else:
                value = 0.0
                return value
        
    def _get_pur_qty(self, data, val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sm.product_id as product_id, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and sm.product_id=%s "\
                                " and spt.code='incoming' "\
                                " and rp.supplier is True "\
                                " and sm.state = 'done' "\
                                " Group by sm.product_id "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),val))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
        else:
            self.cr.execute(" select pp.name_template as code, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pp.name_template='%s' "\
                                " and spt.code='incoming' "\
                                " and rp.supplier is True "\
                                " and sm.state = 'done' "\
                                " Group by pp.name_template "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),str(val)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
        
    #~ def _get_branch_pur_qty(self,data,val):
        #~ com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        #~ from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        #~ to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        #~ if len(com[0]) < 2:
            #~ self.cr.execute(" select sm.product_id as product_id, sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id=%s "\
                                #~ " and sm.product_id=%s "\
                                #~ " and spt.code='incoming' "\
                                #~ " and rp.supplier is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ " Group by sm.product_id "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),val))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty']
            #~ else:
                #~ return 0.0
        #~ else:
            #~ self.cr.execute(" select pp.name_template as code, sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id in %s "\
                                #~ " and pp.name_template='%s' "\
                                #~ " and spt.code='incoming' "\
                                #~ " and rp.supplier is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ " Group by pp.name_template "\
                                #~ " order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),str(val)))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty']
            #~ else:
                #~ return 0.0
            
    def _get_sale_ret_qty(self,data,val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sm.product_id as product_id, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and sm.product_id=%s "\
                                " and spt.code='incoming' "\
                                " and rp.customer is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                " Group by sm.product_id "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),val))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
        else:
            self.cr.execute(" select pp.name_template as code, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pp.name_template='%s' "\
                                " and spt.code='incoming' "\
                                " and rp.customer is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                " Group by pp.name_template "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),str(val)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
                
    def _get_sale_qty(self, data,val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sm.product_id as product_id, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and sm.product_id=%s "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                " Group by sm.product_id "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),val))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
        else:
            self.cr.execute(" select pp.name_template as code, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pp.name_template='%s' "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                " Group by pp.name_template "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),str(val)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
                
    def _get_branch_sale_qty(self,data, val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sm.product_id as product_id, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and sm.product_id=%s "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                " Group by sm.product_id "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),val))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
        else:
            self.cr.execute(" select pp.name_template as code, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pp.name_template='%s' "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                " Group by pp.name_template "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),str(val)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
                
    def _get_purchase_ret_qty(self,data,val):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sm.product_id as product_id, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and sm.product_id=%s "\
                                " and spt.code='outgoing' "\
                                " and rp.supplier is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                " Group by sm.product_id "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),val))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
        else:
            self.cr.execute(" select pp.name_template as code, sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pp.name_template='%s' "\
                                " and spt.code='outgoing' "\
                                " and rp.supplier is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                " Group by pp.name_template "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),str(val)))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty']
            else:
                return 0.0
            
    def _get_close_qty(self, data, vals):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        wizard=self.pool.get('stock.history')
        if len(com[0]) < 2:
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_id'][0],rec['quantity'])
                li.append(quan)
            get = [item for item in li if item[0] == vals]
            if get:
                value = get[0][1]
            else:
                value = 0.0
            return value
        else:
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            gi = []
            g = {}
            value = 0.0
            for rec in res:
                quan=(rec['product_id'][0],rec['quantity'])
                li.append(quan)
            for li1 in li:
                prod = self.pool.get('product.product').browse(self.cr, self.uid, li1[0])
                g = (prod.default_code,li1[1])
                gi.append(g)
            get = [item for item in gi if item[0] == vals]
            my_set = {x[0] for x in get}
            my_sums = [(i,sum(x[1] for x in get if x[0] == i)) for i in my_set]
            if get:
                value = my_sums[0][1]
                return value
            else:
                value = 0.0
                return value
        
    def _get_value(self, data, vals):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        wizard=self.pool.get('stock.history')
        if len(com[0]) < 2:
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_id'][0],rec['quantity'],rec['inventory_value'])
                li.append(quan)
            get = [item for item in li if item[0] == vals]
            if get:
                value = get[0][2]
            else:
                value = 0.0
            valu = "%.2f" % value
            return valu
        else:
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            gi = []
            g = {}
            value = 0.0
            for rec in res:
                quan=(rec['product_id'][0],rec['quantity'],rec['inventory_value'])
                li.append(quan)
            for li1 in li:
                prod = self.pool.get('product.product').browse(self.cr, self.uid, li1[0])
                g = (prod.default_code,li1[1],li1[2])
                gi.append(g)
            get = [item for item in gi if item[0] == vals]
            my_set = {x[0] for x in get}
            my_sums = [(i,sum(x[2] for x in get if x[0] == i)) for i in my_set]
            if get:
                value = my_sums[0][1]
                valu = "%.2f" % value
                return valu
            else:
                value = 0.0
                return value
        
    def _get_tot_open_qty(self,data,prod):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
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
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            get = [item for item in li if item[0] == prod]
            if get:
                value = get[0][1]
            else:
                value = 0.0
            return value
        else:
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
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            for li1 in li:
                prods = self.pool.get('product.category').browse(self.cr, self.uid, li1[0])
                g = (prods.name,li1[1])
                gi.append(g)
            get = [item for item in gi if item[0] == prod]
            if get:
                lol = 0.0
                for lin in get:
                    lol += lin[1]
                value = lol
            else:
                value = 0.0
            return value
            
    def _get_tot_pur_qty(self,data,prod):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and pt.categ_id=%s "\
                                " and spt.code='incoming' "\
                                " and rp.supplier is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pc.name='%s' "\
                                " and spt.code='incoming' "\
                                " and rp.supplier is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
            
    #~ def _get_tot_branch_pur_qty(self,data,prod):
        #~ com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        #~ from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        #~ to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        #~ if len(com[0]) < 2:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id=%s "\
                                #~ " and pt.categ_id=%s "\
                                #~ " and spt.code='incoming' "\
                                #~ " and rp.supplier is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),prod))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
        #~ else:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id in %s "\
                                #~ " and pc.name='%s' "\
                                #~ " and spt.code='incoming' "\
                                #~ " and rp.supplier is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),prod))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
            
    def _get_tot_sale_ret_qty(self,data,prod):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and pt.categ_id=%s "\
                                " and spt.code='incoming' "\
                                " and rp.customer is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pc.name='%s' "\
                                " and spt.code='incoming' "\
                                " and rp.customer is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
    
    def _get_tot_sale_qty(self,data,prod):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and pt.categ_id=%s "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pc.name='%s' "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0

    #~ def _get_tot_branch_sale_qty(self,data,prod):
        #~ com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        #~ from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        #~ to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        #~ if len(com[0]) < 2:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id=%s "\
                                #~ " and pt.categ_id=%s "\
                                #~ " and spt.code='outgoing' "\
                                #~ " and rp.customer is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),prod))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
        #~ else:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id in %s "\
                                #~ " and pc.name='%s' "\
                                #~ " and spt.code='outgoing' "\
                                #~ " and rp.customer is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),prod))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
            
    def _get_tot_purchase_ret_qty(self,data,prod):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and pt.categ_id=%s "\
                                " and spt.code='outgoing' "\
                                " and rp.supplier is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN product_category pc on (pc.id=pt.categ_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and pc.name='%s' "\
                                " and spt.code='outgoing' "\
                                " and rp.supplier is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0]),prod))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
            
    def _get_tot_close_qty(self,data,prod):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            get = [item for item in li if item[0] == prod]
            if get:
                value = get[0][1]
            else:
                value = 0.0
            return value
        else:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            gi = []
            g = {}
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            for li1 in li:
                prods = self.pool.get('product.category').browse(self.cr, self.uid, li1[0])
                g = (prods.name,li1[1])
                gi.append(g)
            get = [item for item in gi if item[0] == prod]
            if get:
                lol = 0.0
                for lin in get:
                    lol += lin[1]
                value = lol
            else:
                value = 0.0
            return value
            
        
    def _get_tot_value(self,data,prod):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'],rec['inventory_value'])
                li.append(quan)
            get = [item for item in li if item[0] == prod]
            if get:
                value = get[0][2]
            else:
                value = 0.0
            valu = "%.2f" % value
            return valu
        else:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            gi = []
            g = {}
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'],rec['inventory_value'])
                li.append(quan)
            for li1 in li:
                prods = self.pool.get('product.category').browse(self.cr, self.uid, li1[0])
                g = (prods.name,li1[1],li1[2])
                gi.append(g)
            get = [item for item in gi if item[0] == prod]
            my_set = {x[0] for x in get}
            my_sums = [(i,sum(x[2] for x in get if x[0] == i)) for i in my_set]
            if get:
                value = my_sums[0][1]
                valu = "%.2f" % value
                return valu
            else:
                value = 0.0
                return value
            
    def _get_grand_open_qty(self,data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
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
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            for line in li:
                value += line[1]
            return value
        else:
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
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            for line in li:
                value += line[1]
            return value
    
    def _get_grand_pur_qty(self, data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and spt.code='incoming' "\
                                " and rp.supplier is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and spt.code='incoming' "\
                                " and rp.supplier is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        
    #~ def _get_grand_branch_pur_qty(self,data):
        #~ com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        #~ from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        #~ to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        #~ if len(com[0]) < 2:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id=%s "\
                                #~ " and spt.code='incoming' "\
                                #~ " and rp.supplier is True "\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
        #~ else:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id in %s "\
                                #~ " and spt.code='incoming' "\
                                #~ " and rp.supplier is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
            
    def _get_grand_sale_ret_qty(self, data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and spt.code='incoming' "\
                                " and rp.customer is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and spt.code='incoming' "\
                                " and rp.customer is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0

    def _get_grand_sale_qty(self,data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and spt.code='outgoing' "\
                                " and rp.customer is True "\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
            
    #~ def _get_grand_branch_sale_qty(self,data):
        #~ com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        #~ from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        #~ to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        #~ if len(com[0]) < 2:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id=%s "\
                                #~ " and spt.code='outgoing' "\
                                #~ " and rp.customer is True "\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
        #~ else:
            #~ self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                #~ " from stock_picking sp "\
                                #~ " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                #~ " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                #~ " JOIN product_product pp on (pp.id=sm.product_id)"\
                                #~ " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                #~ " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                #~ " where sm.date >= '%s' "\
                                #~ " and sm.date <= '%s' "\
                                #~ " and sm.company_id in %s "\
                                #~ " and spt.code='outgoing' "\
                                #~ " and rp.customer is True "\
                                #~ " and rp.branch_transfer is True"\
                                #~ " and sm.state = 'done' "\
                                #~ "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            #~ line_list = [i for i in self.cr.dictfetchall()]
            #~ if line_list:
                #~ return line_list[0]['qty'] or 0.0
            #~ else:
                #~ return 0.0
 
    def _get_grand_purchase_ret_qty(self,data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id=%s "\
                                " and spt.code='outgoing' "\
                                " and rp.supplier is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),str(data['form']['company_ids'][0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
        else:
            self.cr.execute(" select sum(coalesce(product_qty,0)) as qty "\
                                " from stock_picking sp "\
                                " JOIN stock_move sm on (sm.picking_id=sp.id)"\
                                " JOIN stock_picking_type spt on (spt.id=sp.picking_type_id)"\
                                " JOIN product_product pp on (pp.id=sm.product_id)"\
                                " JOIN product_template pt on (pt.id=pp.product_tmpl_id)"\
                                " JOIN res_partner rp on (rp.id=sp.partner_id)"\
                                " where sm.date >= '%s' "\
                                " and sm.date <= '%s' "\
                                " and sm.company_id in %s "\
                                " and spt.code='outgoing' "\
                                " and rp.supplier is True "\
                                " and sm.origin_returned_move_id is not null"\
                                " and sm.state = 'done' "\
                                "order by 1" % (str(from_date[0]),str(to_date[0]),tuple(com[0])))
            line_list = [i for i in self.cr.dictfetchall()]
            if line_list:
                return line_list[0]['qty'] or 0.0
            else:
                return 0.0
            
    def _get_grand_close_qty(self, data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            for line in li:
                value += line[1]
            return value
        else:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'])
                li.append(quan)
            for line in li:
                value += line[1]
            return value
        
    def _get_grand_value(self, data):
        com = 'company_ids' in data['form'] and [data['form']['company_ids']] or []
        from_date = 'from_date' in data['form'] and [data['form']['from_date']] or []
        to_date = 'to_date' in data['form'] and [data['form']['to_date']] or []
        if len(com[0]) < 2:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'],rec['inventory_value'])
                li.append(quan)
            for line in li:
                value += line[2]
            valu = "%.2f" % value
            return valu
        else:
            wizard=self.pool.get('stock.history')
            domain=[]
            date=['date','<=',to_date[0]]
            domain.append(date)
            fields=['product_categ_id','product_id', 'location_id', 'move_id','company_id', 'date', 'source', 'quantity', 'inventory_value']
            groupby=['product_categ_id','product_id', 'location_id']
            res = wizard.read_group(self.cr, self.uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False, lazy=True)
            li = []
            value = 0.0
            for rec in res:
                quan=(rec['product_categ_id'],rec['quantity'],rec['inventory_value'])
                li.append(quan)
            for line in li:
                value += line[2]
            valu = "%.2f" % value
            return valu
            
    def _get_com(self,val):
        na = self.pool.get('res.company').browse(self.cr, self.uid, val)
        if na.name[0:3] == 'AEA':
            na1 = 'Associated Electrical Agencies'
            return na1
        else:
            na1 = 'Apex Agencies'
            return na1
        
        
class wrapped_stock_ledger_summary(osv.AbstractModel):
    _name = 'report.fnet_mline_sale_report.report_stock_ledger'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_sale_report.report_stock_ledger'
    _wrapped_report_class = stock_ledger_summary_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
