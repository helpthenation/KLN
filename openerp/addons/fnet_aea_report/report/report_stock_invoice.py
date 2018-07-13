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
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from openerp.report import report_sxw
import math
from openerp.tools.amount_to_text_en import amount_to_text
from math import pi

class stock_invoice_report(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(stock_invoice_report, self).__init__(cr, uid, name, context=context)
        ids = context.get('active_ids')
        inv_obj = self.pool['stock.picking']
        inv_br_obj = inv_obj.browse(cr, uid, ids, context=context)
        self.localcontext.update({
             'get_invoice_tn_obj': self._get_invoice_tn_obj,
             'get_payment_term':self._get_payment_term,
             'get_round': self._get_round,
             'get_amd2text': self._get_amd2text,
             'get_weight': self._get_weight,
             'get_qty': self._get_qty,
             'get_com': self._get_com,
             'get_gro_amd': self._get_gro_amd,
             'get_csh':self._get_csh,
             'get_amd_tot':self._get_amd_tot,
        })
        self.context = context

    def _get_invoice_tn_obj(self):
        print "GGGGGGGGGGG"
        ids = self.context.get('active_ids')
        inv_obj = self.pool['stock.picking']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
              select 
                  distinct sp.id, pp.name_template as prod,
                  sm.product_uom_qty as qty, 
                  pu.name as uom,                 
                  pt.mrp_price as mrp,
                  sol.price_unit as rate,
                  ceiling(sm.product_uom_qty / pt.case_qty) as case_qty,
                  sol.price_unit * sol.product_uom_qty as value,
                  so.amount_total 
                 from stock_picking sp 
                 join stock_move sm on (sm.picking_id=sp.id) 
                 join stock_picking_type spt on (spt.id=sp.picking_type_id) 
                 Join procurement_group pg on (pg.id=sp.group_id) 
                 Join sale_order so on (so.name=pg.name) 
                 join sale_order_line sol on (sol.order_id=so.id and sm.product_id=sol.product_id) 
                 JOIN product_product pp ON (pp.id=sm.product_id) 
                 JOIN product_uom pu ON (pu.id = sm.product_uom) 
                 JOIN product_template pt ON (pt.id = pp.product_tmpl_id) 
                 where spt.code='outgoing' and sp.id=%s
                         """ %(inv_br_obj.id))
        t = self.cr.dictfetchall()
        return t
    
    def _get_payment_term(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        return so_br_obj.payment_term.name
        
        
    def _get_round(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        rnd = 0.0
        for line in so_br_obj.order_line:
            if line.product_id.type == 'service':
                rnd += line.price_unit
        return rnd
        
    def _get_tot(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        tax = inv_br_obj.amount_untaxed
        tot = inv_br_obj.amount_tax
        val = tax + tot
        return val

    def _amount_to_text(self, amount, currency):
        cur = self.pool['res.currency'].browse(self.cr, self.uid, currency, context=self.context)
        if cur.name.upper() == 'EUR':
            currency_name = 'Euro'
        elif cur.name.upper() == 'USD':
            currency_name = 'Dollars'
        elif cur.name.upper() == 'INR':
            currency_name = 'Rupees'
        elif cur.name.upper() == 'BRL':
            currency_name = 'reais'
        else:
            currency_name = cur.name
        #TODO : generic amount_to_text is not ready yet, otherwise language (and country) and currency can be passed
        #amount_in_word = amount_to_text(amount, context=context)
        return amount_to_text(amount, currency=currency_name)
    
    def _get_amd2text(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        tot = so_br_obj.amount_total
        res = self._amount_to_text(tot, so_br_obj.currency_id.id)
        return res
        
    def _get_weight(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        self.cr.execute("""
             SELECT
                 SUM(sol.product_uom_qty * pt.weight) as weight  
             FROM sale_order so
             JOIN sale_order_line sol ON (sol.order_id = so.id)
             JOIN product_product pp ON (pp.id = sol.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE so.id = '%s'
                         """ %(so_br_obj.id))
        g = self.cr.dictfetchall()
        t = g[0]['weight']
        return t
        
    def _get_qty(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        self.cr.execute("""
             SELECT
                 SUM(sol.product_uom_qty) as product_qty
             FROM sale_order so
             JOIN sale_order_line sol ON (sol.order_id = so.id)
             JOIN product_product pp ON (pp.id = sol.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE so.id = '%s' and pt.type != 'service'
                         """ %(so_br_obj.id))
        g = self.cr.dictfetchall()
        t = g[0]['product_qty']
        return t
        
    def _get_com(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        print stock_br_obj.picking_type_id.code, "%%%%%%%%%%%%%%%%%%%%%%%"
        if stock_br_obj.picking_type_id.code == 'incoming':
            raise osv.except_osv(_("Warning"), _("Please Choose the Delivery Order!"))
        else:
            print "YYYYYYYYYY"
            so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
            so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
            na = so_br_obj.company_id.name
            if na[0:3] == 'AEA':
                na = 'Associated Electrical Agencies'
            else:
                na = 'Apex Agencies'
            return na
        
    def _get_gro_amd(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        rnd = 0.0
        gro = so_br_obj.amount_untaxed
        for line in so_br_obj.order_line:
            if line.product_id.type == 'service':
                rnd += line.price_unit
        val = gro - rnd
        return val
        
    def _get_csh(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        self.cr.execute("""
              SELECT 
                  sum(ceiling(sol.product_uom_qty / pt.case_qty)) as case_qty
             FROM sale_order so
             JOIN sale_order_line sol ON (sol.order_id = so.id)
             JOIN product_product pp ON (pp.id = sol.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             JOIN product_uom pu ON (pu.id = sol.product_uom)
            WHERE so.id = '%s' and pt.type != 'service'
                         """ %(so_br_obj.id))
        t = self.cr.dictfetchall()
        return t[0]['case_qty']
        
    def _get_amd_tot(self):
        ids = self.context.get('active_ids')
        stock_obj = self.pool['stock.picking']
        so_obj = self.pool['sale.order']
        stock_br_obj = stock_obj.browse(self.cr, self.uid, ids, context=self.context)
        so_br_id=so_obj.search(self.cr,self.uid,[('name','=',stock_br_obj.group_id.name)])
        so_br_obj=so_obj.browse(self.cr, self.uid, so_br_id, context=self.context)
        ge = "%0.2f" % so_br_obj.amount_total
        return ge
        
class wrapped_report_stock_invoice(osv.AbstractModel):
    _name = 'report.fnet_aea_report.report_stock_invoice'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_report.report_stock_invoice'
    _wrapped_report_class = stock_invoice_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
