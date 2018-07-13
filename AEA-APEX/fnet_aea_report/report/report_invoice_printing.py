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
import math
from openerp.tools.amount_to_text_en import amount_to_text

class invoice_report_print(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(invoice_report_print, self).__init__(cr, uid, name, context=context)
        ids = context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(cr, uid, ids, context=context)
        self.localcontext.update({
             'get_invoice_obj': self._get_invoice_obj,
             'get_invoice_tn_obj': self._get_invoice_tn_obj,
             'get_total_obj': self._get_total_obj,
             'get_round': self._get_round,
             'get_tot': self._get_tot,
             'get_amd2text': self._get_amd2text,
             'get_weight': self._get_weight,
             'get_qty': self._get_qty,
             'get_dc': self._get_dc,
             'get_dispatch': self._get_dispatch,
             'get_push': self._get_push,
             'get_tax_name': self._get_tax_name,
             'get_com': self._get_com,
             'get_gro_amd': self._get_gro_amd,
        })
        self.context = context

    def _get_invoice_tn_obj(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
              SELECT 
                  pp.name_template as prod,
                  ail.quantity as qty,
                  pu.name as uom,
                  pu.id as pus,
                  ail.price_unit as rate,
                  pt.case_qty as case_qty,
                  pt.mrp_price as mrp,
                  ail.price_subtotal as value
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_uom pu ON (pu.id = ail.uos_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(inv_br_obj.id))
        t = self.cr.dictfetchall()
        return t
    
    def _get_invoice_obj(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
              SELECT 
                  pc.commodity_code as comm_code,
                  pp.name_template as prod,
                  at.amount * 100 as tax,
                  ail.price_unit as pri_unit,
                  ail.quantity as qty,
                  ail.price_unit * ail.quantity as gro_val,
                  ail.discount as dis,
                  ail.price_subtotal as pri_sub,
                  ail.price_subtotal * at.amount as tax_amd,
                  (ail.price_subtotal * at.amount) + ail.price_subtotal as tot
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            JOIN product_category pc ON (pc.id = pt.categ_id)
            JOIN account_invoice_line_tax ailt ON (ailt.invoice_line_id = ail.id)
            JOIN account_tax at ON (at.id = ailt.tax_id)
            WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(inv_br_obj.id))
        t = self.cr.dictfetchall()
        return t
        
    def _get_total_obj(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
              SELECT 
                  sum(ail.quantity) as qty,
                  sum(ail.price_unit * ail.quantity) as gro_val,
                  sum(ail.discount) as dis,
                  sum(ail.price_subtotal) as pri_sub,
                  sum(ail.price_subtotal * at.amount) as tax_amd,
                  sum((ail.price_subtotal * at.amount) + ail.price_subtotal) as tot
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            JOIN product_category pc ON (pc.id = pt.categ_id)
            JOIN account_invoice_line_tax ailt ON (ailt.invoice_line_id = ail.id)
            JOIN account_tax at ON (at.id = ailt.tax_id)
            WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(inv_br_obj.id))
        t = self.cr.dictfetchall()
        return t
        
    def _get_round(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        rnd = 0.0
        for line in inv_br_obj.invoice_line:
            if line.product_id.type == 'service':
                rnd += line.price_unit
        return rnd
        
    def _get_tot(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
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
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        tot = inv_br_obj.amount_total
        res = self._amount_to_text(tot, inv_br_obj.currency_id.id)
        return res
        
    def _get_weight(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
             SELECT
                 SUM(ail.quantity * pt.weight) as weight  
             FROM account_invoice ai
             JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
             JOIN product_product pp ON (pp.id = ail.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE ai.id = '%s'
                         """ %(inv_br_obj.id))
        g = self.cr.dictfetchall()
        t = g[0]['weight']
        return t
        
    def _get_qty(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
             SELECT
                 SUM(ail.quantity) as product_qty
             FROM account_invoice ai
             JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
             JOIN product_product pp ON (pp.id = ail.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE ai.id = '%s'
                         """ %(inv_br_obj.id))
        g = self.cr.dictfetchall()
        t = g[0]['product_qty']
        return t

    def _get_dc(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
              SELECT 
                  sp.name as name,
                  to_char(sp.date,  'DD-MM-YYYY') as date
            FROM sale_order_invoice_rel soil
            JOIN sale_order so ON (so.id = soil.order_id)
            JOIN stock_picking sp ON (sp.group_id = so.procurement_group_id)
            WHERE soil.invoice_id = '%s'
                         """ %(inv_br_obj.id))
        t = self.cr.dictfetchall()
        return t
        
    def _get_dispatch(self):
        res = {}
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
              SELECT 
                    lr.method_type as dis,
                    rp.name as tpt_name,
                    lr.lr_no as lr_no,
                    lr.date as date,
                    rpd.city as desti
            FROM lorry_receipt_line lrl
            JOIN lorry_receipt lr ON (lr.id = lrl.lorry_receipt_id)
            JOIN res_partner rp ON (rp.id = lr.tpt_name)
            JOIN account_invoice ai ON (ai.id = lrl.invoice_id)
            JOIN res_partner rpd ON (rpd.id = ai.partner_id)
            WHERE lrl.invoice_id = '%s'
                         """ %(inv_br_obj.id))
        t = self.cr.dictfetchall()
        if not t:
            res['dis']=' '
            res['tpt_name']=' '
            res['lr_no']=' '
            res['date']=' '
            res['desti']=' '
            t.append(res)
        return t
        
    def _get_push(self,data):
        uom = self.pool['product.uom']
        uom_obj = uom.browse(self.cr, self.uid, data, context=self.context)
        val = uom_obj.factor_inv
        return val
        
    def _get_tax_name(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        self.cr.execute("""
              SELECT 
                  at.amount * 100 as tax,
                  at.name as name
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            JOIN product_category pc ON (pc.id = pt.categ_id)
            JOIN account_invoice_line_tax ailt ON (ailt.invoice_line_id = ail.id)
            JOIN account_tax at ON (at.id = ailt.tax_id)
            WHERE ai.id = '%s'
                         """ %(inv_br_obj.id))
        t = self.cr.dictfetchall()
        ta = t[0]['tax']
        t[0]['tax'] = str(ta) + '%'
        return t
        
    def _get_com(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        na = inv_br_obj.company_id.name
        if na[0:3] == 'AEA':
            na = 'Associated Electrical Agencies'
        else:
            na = 'Apex Agencies'
        return na
        
    def _get_gro_amd(self):
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        rnd = 0.0
        gro = inv_br_obj.amount_untaxed
        for line in inv_br_obj.invoice_line:
            if line.product_id.type == 'service':
                rnd += line.price_unit
        val = gro - rnd
        return val
        
class wrapped_invoice_report_print(osv.AbstractModel):
    _name = 'report.fnet_aea_report.report_invoice_print'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_report.report_invoice_print'
    _wrapped_report_class = invoice_report_print

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
