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

from openerp import api, models,_
from openerp.osv import osv,fields
import math
from openerp.tools.amount_to_text_en import amount_to_text
#~ from openerp.tools import india_amount
from math import pi

class ParticularReport(models.AbstractModel):
   
    _name = 'report.fnet_aea_report.report_invoice'
   
    def get_invoice_tn_obj(self,obj):
        self.env.cr.execute("""
              SELECT 
                  ai.id,
                  pp.name_template as prod,
                  ail.quantity as qty,
                  pu.name as uom,
                  pu.id as pus,
                  ail.price_unit as rate,
                  ceiling(ail.quantity / pt.case_qty) as case_qty,
                  COALESCE(ail.mrp_price,0.00) as mrp,
                  ail.price_subtotal as value
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_uom pu ON (pu.id = ail.uos_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(obj.ids[0]))
        t = self.env.cr.dictfetchall()
        return t
    
    def get_invoice_obj(self,obj):
        self.env.cr.execute("""
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
                         """ %(obj.ids[0]))
        t = self.env.cr.dictfetchall()
        return t
        
    def get_total_obj(self,obj):
        #~ ids = self.context.get('active_ids')
        self.env.cr.execute("""
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
                         """ %(obj.ids[0]))
        t = self.env.cr.dictfetchall()
        return t
        
    def get_round(self,obj):
        rnd = 0.0
        f=obj.round_amount
        for line in obj.invoice_line:
            if line.product_id.type == 'service':
                rnd += line.price_unit
        if f >= 0.0 and rnd == 0.0:
            return f
        else:   
            return rnd
        
    def get_tot(self,obj):
        tax = obj.amount_untaxed
        tot = obj.amount_tax
        val = tax + tot
        return val

    def amount_to_text(self, amount, currency):
        cur = self.env['res.currency'].browse(currency)
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
    
    def get_amd2text(self,obj):
        res = obj.amount_total
        #~ if obj.currency_id.name == 'INR':
            #~ res=india_amount.convertNumberToWords(tot)  
        #~ else:
            #~ res= amount_to_text(tot,obj.currency_id.name)
        return res
        
    def get_weight(self,obj):
        self.env.cr.execute("""
             SELECT
                 SUM(ail.quantity * pt.weight) as weight  
             FROM account_invoice ai
             JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
             JOIN product_product pp ON (pp.id = ail.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE ai.id = '%s'
                         """ %(obj.ids[0]))
        g = self.env.cr.dictfetchall()
        t = g[0]['weight']
        return t
        
    def get_qty(self,obj):
        self.env.cr.execute("""
             SELECT
                 SUM(ail.quantity) as product_qty
             FROM account_invoice ai
             JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
             JOIN product_product pp ON (pp.id = ail.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(obj.ids[0]))
        g = self.env.cr.dictfetchall()
        t = g[0]['product_qty']
        return t

    def get_dc(self,obj):
        self.env.cr.execute("""
                  SELECT 
                      sp.name as name,
                      to_char(sp.date,  'DD-MM-YYYY') as date
                FROM sale_order_invoice_rel soil
                JOIN sale_order so ON (so.id = soil.order_id)
                JOIN stock_picking sp ON (sp.group_id = so.procurement_group_id)
                WHERE soil.invoice_id = '%s'
                             """ %(obj.ids[0]))
        t = self.env.cr.dictfetchall()
        return t
        
    def get_dispatch(self,obj):
        res = {}        
        self.env.cr.execute("""
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
                         """ %(obj.ids[0]))
        t = self.env.cr.dictfetchall()
        if not t:
            res['dis']=' '
            res['tpt_name']=' '
            res['lr_no']=' '
            res['date']=' '
            res['desti']=' '
            t.append(res)
        return t
        
    def get_push(self,obj):
        uom = self.env['product.uom']
        uom_obj = uom.browse(self.ids)
        val = uom_obj.factor_inv
        return val
        
    def get_tax_name(self,obj):
        #~ ids = self.context.get('active_ids')
       
        self.env.cr.execute("""
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
                         """ %(obj.ids[0]))
        t = self.env.cr.dictfetchall()
        ta = t[0]['tax']
        t[0]['tax'] = str(ta) + '%'
        return t
        
    def get_com(self,obj):
       na = obj.company_id.name
       if na[0:3] == 'AEA':
           
           na = 'Associated Electrical Agencies'
       else:
           na = 'Apex Agencies'
       return na
        
    def get_gro_amd(self,obj):
        #~ ids = self.context.get('active_ids')
        rnd = 0.0
        gro = obj.amount_untaxed
        f=obj.round_amount
        for line in obj.invoice_line:
            if line.product_id.type == 'service':
                rnd += line.price_unit
        val = gro - rnd    
        return val
        
    def get_csh(self,obj):
        #~ ids = self.context.get('active_ids')
        self.env.cr.execute("""
              SELECT 
                  sum(ceiling(ail.quantity / pt.case_qty)) as case_qty
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_uom pu ON (pu.id = ail.uos_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(obj.ids[0]))
        t = self.env.cr.dictfetchall()
        return t[0]['case_qty']

    def get_amd_tax(self, val):
        ge = "%0.2f" % val
        return ge
        
    def get_amd_tot(self, val):
        ge = "%0.2f" % val
        return ge


    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_aea_report.report_invoice')
        leave_form=self.env['account.invoice'].browse(self._ids)
        docargs = {
            'doc': leave_form,
            'doc_model': report.model,
            'docs': self,
            'doc_ids':self._ids,
        }
        return report_obj.render('fnet_aea_report.report_invoice', docargs)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
