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
import locale
from openerp.osv import osv
from openerp.report import report_sxw
import math
from datetime import datetime
class invoice_report1(report_sxw.rml_parse):
    
    counter=0
    def __init__(self, cr, uid, name, context):
        if context is None:
            context = {}
        super(invoice_report1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
                'get_dispatch': self.get_dispatch,
                'invoice_line': self._invoice_line,
                'get_invoice_tn_obj': self.get_invoice_tn_obj,
                'numtowords': self._numtowords,
                'get_amount': self._get_amount,
                'get_job_no': self._get_job_no,
                'get_int': self._get_int,
                'get_date': self._get_date,
                'get_com': self.get_com,
                'get_dc': self.get_dc,
                'get_qty': self.get_qty,
                'get_gro_amd': self.get_gro_amd,
                'get_csh': self.get_csh,
                'get_amd_tax': self.get_amd_tax,
                'get_amd_tot': self.get_amd_tot,
                'get_total_obj': self.get_total_obj,
                'get_round': self.get_round,
                'get_tot': self.get_tot,
                'get_weight': self.get_weight,
                'get_tax_name': self.get_tax_name,
        })
        self.context = context
        
        
    def _get_date(self,val):
        if val:
            return datetime.strptime(str(val), '%Y-%m-%d').strftime('%d-%m-%Y')
            
            
    def _get_int(self,val):
        if val:
            return int(val)
            
    def _get_job_no(self,val):
        if val:
            sale_obj = self.pool['sale.order']
            sale_obj_id = sale_obj.search(self.cr, self.uid,[('name','=',val)], context=self.context)
            if sale_obj_id:
                sale_re=sale_obj.browse(self.cr,self.uid,sale_obj_id)
                return sale_re.job_id
        
    def _get_amount(self,val):
        count=0
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        if inv_br_obj:
            self.cr.execute(" select count(id) as value from account_invoice_line "\
                                "where invoice_id= %s" % (str(inv_br_obj.id)))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list[0]['value']:
            count= math.ceil(float(count + line_list[0]['value'])/float(4.0))
        
        if (count-1) == val:
            val='{0:.2f}'.format(inv_br_obj.amount_total)
            amount='{:20,.2f}'.format(float(val))
            return amount
        else:
            return "Continued"
        
    def _numtowords(self,num,join=True):
        '''words = {} convert an integer number into words'''
        units = ['','One','Two','Three','Four','Five','Six','Seven','Eight','Nine']
        teens = ['','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen', \
                 'Seventeen','Eighteen','Nineteen']
        tens = ['','Ten','Twenty','Thirty','Forty','Fifty','Sixty','Seventy', \
                'Eighty','Ninety']
        thousands = ['','Thousand','Million','Billion','Trillion','Quadrillion', \
                     'Quintillion','Sextillion','Septillion','oOtillion', \
                     'Nonillion','Decillion','Undecillion','Duodecillion', \
                     'Tredecillion','Quattuordecillion','Sexdecillion', \
                     'Septendecillion','Octodecillion','Novemdecillion', \
                     'Vigintillion']
        words = []
        num=round(num)
        if num==0: words.append('zero')
        else:
            numStr = '%d'%num
            numStrLen = len(numStr)
            groups = (numStrLen+2)/3
            numStr = numStr.zfill(groups*3)
            for i in range(0,groups*3,3):
                h,t,u = int(numStr[i]),int(numStr[i+1]),int(numStr[i+2])
                g = groups-(i/3+1)
                if h>=1:
                    words.append(units[h])
                    words.append('hundred')
                if t>1:
                    words.append(tens[t])
                    if u>=1: words.append(units[u])
                elif t==1:
                    if u>=1: words.append(teens[u])
                    else: words.append(tens[t])
                else:
                    if u>=1: words.append(units[u])
                if (g>=1) and ((h+t+u)>0): words.append(thousands[g])
        if words:
           words.append( " Only")
        if join: return ' '.join(words)
        return words 
          
    def _invoice_line(self):
        count=0
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        if inv_br_obj:
            self.cr.execute("""
                        SELECT count(ai.id) as value
                        FROM account_invoice ai
                        JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
                        JOIN product_product pp ON (pp.id = ail.product_id)
                        JOIN product_uom pu ON (pu.id = ail.uos_id)
                        JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                        WHERE ai.id = '%s' and pt.type != 'service' """% (str(inv_br_obj.id)))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list[0]['value'] <= 4:
            count= count + 1
        elif line_list[0]['value'] > 4:
            count= math.ceil(float(count + line_list[0]['value'])/float(4.0))
        value=[]
        if count <= 1:
            value.append(0)
        else:
            for val in range(0,int(count)):
                value.append(val)
        print'valllllllllllllllllllllllllllllllllllllllllllllllllll',value        
        return value
        
    def get_invoice_tn_obj(self,val):
        print'vaaaaaaaaaaaaaaaaaaaaaa',val
        ids = self.context.get('active_ids')
        inv_obj = self.pool['account.invoice']
        inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        print'inv_br_obj',inv_br_obj
        if inv_br_obj:
            limit= 4
            offset= val * 4
            self.cr.execute("""
                  SELECT 
                      ai.id,
                      pp.name_template as prod,
                      ail.quantity as qty,
                      pu.name as uom,
                      pu.id as pus,
                      ail.price_unit as rate,
                      ceiling(ail.quantity / pt.case_qty) as case_qty,
                      pt.mrp_price as mrp,
                      ail.price_subtotal as value
                FROM account_invoice ai
                JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
                JOIN product_product pp ON (pp.id = ail.product_id)
                JOIN product_uom pu ON (pu.id = ail.uos_id)
                JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                WHERE ai.id = '%s' and pt.type != 'service'  limit %s offset %s
                             """ %(str(inv_br_obj.id),str(limit),str(offset)))
        line_list = [i for i in self.cr.dictfetchall()]
        count=0
        if val < 1:
            count=val+1
        elif val >= 1:
            count= val*4 + 1
        for val in line_list:
            val['serial_no']=count
            count=count+1
        if line_list:
            print'line_list',line_list
            return line_list         
        
    def get_com(self,obj):
       ids = self.context.get('active_ids')
       inv_obj = self.pool['account.invoice']
       inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
       na = inv_br_obj.company_id.name
       if na[0:3] == 'AEA':
           
           na = 'Associated Electrical Agencies'
       else:
           na = 'Apex Agencies'
       return na        
    def get_dispatch(self,obj):
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
                         """ %(inv_br_obj.ids[0]))
        t = self.cr.dictfetchall()
        if not t:
            res['dis']=' '
            res['tpt_name']=' '
            res['lr_no']=' '
            res['date']=' '
            res['desti']=' '
            t.append(res)
        return t        

    def get_dc(self,obj):
        self.cr.execute("""
                  SELECT 
                      sp.name as name,
                      to_char(sp.date,  'DD-MM-YYYY') as date
                FROM sale_order_invoice_rel soil
                JOIN sale_order so ON (so.id = soil.order_id)
                JOIN stock_picking sp ON (sp.group_id = so.procurement_group_id)
                WHERE soil.invoice_id = '%s'
                             """ %(obj.ids[0]))
        t = self.cr.dictfetchall()
        return t    

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
        self.cr.execute("""
              SELECT 
                  sum(ceiling(ail.quantity / pt.case_qty)) as case_qty
            FROM account_invoice ai
            JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
            JOIN product_product pp ON (pp.id = ail.product_id)
            JOIN product_uom pu ON (pu.id = ail.uos_id)
            JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
            WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(obj.ids[0]))
        t = self.cr.dictfetchall()
        return t[0]['case_qty']

    def get_amd_tax(self, val):
        ge = "%0.2f" % val
        return ge
        
    def get_amd_tot(self, val):
        ge = "%0.2f" % val
        return ge
    def get_total_obj(self,obj):
        #~ ids = self.context.get('active_ids')
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
                         """ %(obj.ids[0]))
        t = self.cr.dictfetchall()
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
        tot = obj.amount_total
        if obj.currency_id.name == 'INR':
            res=india_amount.convertNumberToWords(tot)  
        else:
            res= amount_to_text(tot,obj.currency_id.name)
        return res
        
    def get_weight(self,obj):
        self.cr.execute("""
             SELECT
                 SUM(ail.quantity * pt.weight) as weight  
             FROM account_invoice ai
             JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
             JOIN product_product pp ON (pp.id = ail.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE ai.id = '%s'
                         """ %(obj.ids[0]))
        g = self.cr.dictfetchall()
        t = g[0]['weight']
        return t
        
    def get_qty(self,obj):
        self.cr.execute("""
             SELECT
                 SUM(ail.quantity) as product_qty
             FROM account_invoice ai
             JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
             JOIN product_product pp ON (pp.id = ail.product_id)
             JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
             WHERE ai.id = '%s' and pt.type != 'service'
                         """ %(obj.ids[0]))
        g = self.cr.dictfetchall()
        t = g[0]['product_qty']
        return t        
    def get_tax_name(self,obj):
        #~ ids = self.context.get('active_ids')
       
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
                         """ %(obj.ids[0]))
        t = self.cr.dictfetchall()
        ta = t[0]['tax']
        t[0]['tax'] = str(ta) + '%'
        return t        
class wrapped_report_invoice(osv.AbstractModel):
    _name = 'report.fnet_gst_invoice.report_invoice'
    _inherit = 'report.abstract_report'
    _template = 'fnet_gst_invoice.report_invoice'
    _wrapped_report_class = invoice_report1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
