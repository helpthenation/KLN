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
import decimal
from openerp.osv import osv
from openerp.report import report_sxw
import math
from datetime import datetime
from  amt_to_txt  import Number2Words
from itertools import groupby
import itertools
from operator import itemgetter
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
                'CommaInIndiaFormat':self.CommaInIndiaFormat,
                'tax_name':self.tax_name,
                'dis_amt':self.dis_amt,
                'payment':self.payment,
                'untaxed_dis_amount':self.untaxed_dis_amount,
                'tax_breakup':self.tax_breakup,
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
        
    def _get_amount(self,val,obj):
        count=0
        #~ ids = self.context.get('active_ids')
        #~ inv_obj = self.pool['account.invoice']
        #~ inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        #~ if inv_br_obj:
        self.cr.execute("""
                        SELECT count(ai.id) as value
                        FROM account_invoice ai
                        JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
                        JOIN product_product pp ON (pp.id = ail.product_id)
                        JOIN product_uom pu ON (pu.id = ail.uos_id)
                        JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                        WHERE ai.id = '%s' and pt.type != 'service' """% (str(obj.ids[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list[0]['value']:
            count= math.ceil(float(count + line_list[0]['value'])/float(12.0))
        rnd = 0.0
        gro = obj.amount_untaxed
        for line in obj.invoice_line:
            if line.product_id.type == 'service':
                rnd += line.price_unit
        value = gro - rnd  
        if (count-1) == val:
            amount='{:20,.2f}'.format(float(value))
            return amount
        else:
            return "Continued.."
       
          
    def _invoice_line(self,obj):
        count=0
        #~ ids = self.context.get('active_ids')
        #~ inv_obj = self.pool['account.invoice']
        #~ inv_br_obj = inv_obj.browse(self.cr, self.uid, ids, context=self.context)
        #~ if inv_br_obj:
        self.cr.execute("""
                    SELECT count(ai.id) as value
                    FROM account_invoice ai
                    JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
                    JOIN product_product pp ON (pp.id = ail.product_id)
                    JOIN product_uom pu ON (pu.id = ail.uos_id)
                    JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                    WHERE ai.id = '%s' and pt.type != 'service' """% (str(obj.ids[0])))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list[0]['value'] <= 12:
            count= count + 1
        elif line_list[0]['value'] > 12:
            count= math.ceil(float(count + line_list[0]['value'])/float(12.0))
        value=[]
        if count <= 1:
            value.append(0)
        else:
            for val in range(0,int(count)):
                value.append(val)
        return value
        
    def get_invoice_tn_obj(self,val,obj):
        limit= 12
        offset= val * 12
        self.cr.execute("""
                      SELECT 
                          ai.id,
                          pp.name_template as prod,
                          ail.quantity as qty,
                          (COALESCE(ail.discounts,0.00)) as uom,
                          pu.id as pus,
                          pc.hsn_code as hsn,
                          ail.price_unit as rate,
                          ail.discount as discount,
                          ail.gross_amount as gross,
                          ail.product_discount as prod_discount,
                          ceiling(ail.quantity / pt.case_qty) as case_qty,
                          COALESCE(ail.mrp_price,0.00) as mrp,
                          ail.price_subtotal as value
                    FROM account_invoice ai
                    JOIN account_invoice_line ail ON (ail.invoice_id = ai.id)
                    JOIN product_product pp ON (pp.id = ail.product_id)
                    JOIN product_uom pu ON (pu.id = ail.uos_id)
                    JOIN product_template pt ON (pt.id = pp.product_tmpl_id)
                    JOIN PRODUCT_CATEGORY pc ON (pt.CATEG_ID=pc.ID)
                    WHERE ai.id = '%s' and pt.type != 'service'  limit %s offset %s
                                 """ %(str(obj.ids[0]),str(limit),str(offset)))
        line_list = [i for i in self.cr.dictfetchall()]
        count=0
        if val < 1:
            count=val+1
        elif val >= 1:
            count= val*12 + 1
        for val in line_list:
            val['serial_no']=count
            count=count+1
        if line_list:
            return line_list         
        
    def get_com(self,obj):

       na = obj.company_id.name
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
        
    def _numtowords(self,obj,join=True):
        dis_amount=self.dis_amt(obj)
        untax='{0:.2f}'.format(obj.amount_untaxed)  
        discount='{0:.2f}'.format(dis_amount)         
        tax_amt=0.0
        for i in obj.tax_line:
          tax_amt+=float('{0:.2f}'.format(i.amount))
        num=float(untax)+float(tax_amt)-float(discount)
        wGenerator = Number2Words()
        words=str(wGenerator.convertNumberToWords(num)) 
        #~ wGenerator.convertNumberToWords(num) 
        return  words      
        
    def CommaInIndiaFormat(self,obj,n):
      dis_amount=self.dis_amt(obj)
      untax='{0:.2f}'.format(obj.amount_untaxed)  
      discount='{0:.2f}'.format(dis_amount)         
      round_off='{0:.2f}'.format(obj.round_amount)         
      tax_amt=0.0
      for i in obj.tax_line:
          tax_amt+=float('{0:.2f}'.format(i.amount))
      n=float(untax)+float(tax_amt)-float(discount)+float(round_off)
      d = decimal.Decimal(str(n))
      if d.as_tuple().exponent < -2:
        s = str(n)
      else:
        s = str(n)
      l = len(s)
      i = l-1;
      res = ''
      flag = 0
      k = 0
      while i>=0:
        if flag==0:
          res = res + s[i]
          if s[i]=='.':
            flag = 1
        elif flag==1:
          k = k + 1
          res = res + s[i]
          if k==3 and i-1>=0:
            res = res + ','
            flag = 2
            k = 0
        else:
          k = k + 1
          res = res + s[i]
          if k==2 and i-1>=0:
            res = res + ','
            flag = 2
            k = 0
        i = i - 1
      spli_after=res[::-1].split('.')
      if  len(spli_after[-1]) == 1:
            return res[::-1]+'0'
      else:       
            return res[::-1]        

    def  tax_name(self,obj):
        res=[]
        igst=None
        value=[]
        for i in obj.tax_line:
            res.append({'name':i.name,'amount':i.amount})
            if i.name[0:4].upper() != 'IGST':
                igst=False
            self.cr.execute("""select COALESCE(amount*100 ,0.0) as percentage from account_tax where name='%s' and company_id=%d"""%(i.name,obj.company_id.id))        
            val=self.cr.dictfetchone()
            if val != None:
                value.append(val['percentage'])
        ignored_keys = ["amount"]
        filtered = {tuple((k, d[k]) for k in sorted(d) if k not in ignored_keys): d for d in res}
        new_res=list(filtered.values())
        for i in list(set(value)):
            if igst == False:
                tax='IGST Output @ ' + str((float(i)+float(i))) +'%'
                new_res.append({'name':tax,'amount':0.00})
            else:
                new_res.append({'name':'CGST Output @ '+str((float(i)/2))+'%','amount':0.00})
                new_res.append({'name':'SGST Output @ '+str((float(i)/2))+'%','amount':0.00})
        rdtmlist = sorted(new_res, key=lambda k: k['amount'],reverse=True)
        return rdtmlist   
        
    def tax_breakup(self,obj):    
        self.cr.execute("""DROP VIEW IF EXISTS tax_detail CASCADE""") 
        self.cr.execute("""CREATE or REPLACE VIEW tax_detail as (
                                      SELECT ail.id,
                                   MAX (CASE WHEN at.ref_code = '1' THEN 
                                       case when ai.disc_value > 0 and apl.days = 0  then 
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100))))
                                       when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100))))
                                       when apl.days > 0 then         
                                              (at.amount * ail.price_subtotal) 
                                        end 
                                        END) AS CGST,
                                   MAX (CASE WHEN at.ref_code = '2'  THEN  
                                       case when ai.disc_value > 0  and apl.days = 0 then 
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100))))
                                       when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100))))
                                       when apl.days > 0 then         
                                              (at.amount * ail.price_subtotal)        
                                       end
                                   END) AS SGST,
                                   MAX (CASE WHEN at.ref_code = '3' THEN 
                                       case when ai.disc_value > 0 and apl.days = 0 then 
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100))))
                                       when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                                      (at.amount * (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100))))
                                       when apl.days > 0 then         
                                              (at.amount * ail.price_subtotal)        
                                       end
                                    END) AS IGST,
                                MAX (CASE WHEN at.ref_code is Null THEN 
                                at.amount * ail.price_subtotal END ) AS VAT 
                            FROM account_invoice_line ail
                            JOIN account_invoice_line_tax atr on (atr.invoice_line_id = ail.id)
                            JOIN account_tax at ON (at.id = atr.tax_id)
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join res_company rc on (rc.id=ai.company_id)
                            join account_payment_term_line apl on apl.id = ai.payment_term
                            where ail.invoice_id=%d
                            GROUP BY ail.id
        )""" %(obj.ids[0]))
        self.cr.execute("""SELECT ail.id,ail.product_id,pc.hsn_code,gta.cgst,gta.sgst,gta.igst,gta.vat,
                            MAX(CASE WHEN ai.date_invoice >= '2017-07-01' THEN 
                            case when ai.disc_value > 0 and apl.days = 0  then 
                            (ail.price_subtotal - (ail.price_subtotal * (ai.disc_value / 100)))
                            when ai.disc_value::numeric = 0.0 and apl.days = 0 then                        
                            (ail.price_subtotal - (ail.price_subtotal * (rc.discount_value / 100)))
                            when apl.days > 0 then         
                            ( ail.price_subtotal) 
                            end 
                            WHEN ai.date_invoice < '2017-07-01' THEN ail.price_subtotal 
                            END) AS discount_price
                            FROM account_invoice_line ail                       
                            join account_invoice ai on (ai.id=ail.invoice_id)
                            join product_product pp on (ail.product_id = pp.id)
                            join product_template pt on (pp.product_tmpl_id = pt.id)
                            join product_category pc on (pt.categ_id = pc.id)
                            join res_company rc on (rc.id=ai.company_id)
                            join account_payment_term_line apl on apl.id = ai.payment_term  
                            join tax_detail gta on gta.id=ail.id
                            where ai.id=%d                        
                            GROUP BY ail.id,ail.product_id,pc.hsn_code,gta.cgst,gta.sgst,gta.igst,gta.vat"""%(obj.ids[0]))
        vals=[i for i in self.cr.dictfetchall()]      
        sss=sorted(vals,key=itemgetter('hsn_code'))        
        v={}
        for keys, values in itertools.groupby(sss, itemgetter('hsn_code')):
            for i in values:
                v.setdefault(keys, []).append(i)       
        new_res=[]
        tot=[]
        for key,value in v.iteritems():
            cgst=[]
            sgst=[]
            igst=[]
            amount=[]
            for i in value:
                  if i['cgst'] != None:
                      cgst.append(i['cgst'])
                  if i['sgst'] != None:
                      sgst.append(i['sgst'])                
                  if i['igst'] != None:
                      igst.append(i['igst'])
                  if i['discount_price'] != None:
                      amount.append(i['discount_price'])
            self.cr.execute("""select distinct at.amount*100 as percentage
            FROM account_invoice_line ail
            JOIN account_invoice ai on ai.id=ail.invoice_id
            JOIN account_invoice_line_tax atr on (atr.invoice_line_id = ail.id)
            JOIN account_tax at ON (at.id = atr.tax_id)
            LEFT JOIN product_product pp on ail.product_id=pp.id
            LEFT JOIN product_template pt on pt.id = pp.product_tmpl_id
            LEFT JOIN product_category pc on pc.id=pt.categ_id
            where  ai.id=%d and pc.hsn_code='%s' """%(obj.ids[0],key)
            )
            per=self.cr.dictfetchone()
            new_res.append(
            {
             'hsn':key,
             'cgst':round(sum(cgst),2),
             'sgst':round(sum(sgst),2),
             'igst':round(sum(igst),2),
             'amount':round(sum(amount),2),
             'total':round((sum(cgst)+sum(sgst)+sum(igst)),2),
             'percentage':per['percentage']
            }            
            )
            tot.append(round(sum(amount),2))
        if  round(self.untaxed_dis_amount(obj),2) != sum(tot):
            new_res[0]['amount']=new_res[0]['amount'] + round(self.untaxed_dis_amount(obj),2)-sum(tot)
        return  new_res                       
    def dis_amt(self,obj):
        day=self.pool['account.payment.term.line']
        fyear_ids=day.browse(self.cr, self.uid,obj.payment_term.id,context=self.context)[0]
        amount=0.00
        if str(fyear_ids.days) == '0' and obj.disc_value != 0.0:
            amount_to_dis = obj.amount_untaxed * (obj.disc_value / 100)
            amount = amount_to_dis
        elif str(fyear_ids.days) == '0' and obj.disc_value == 0.0:
            amount = obj.amount_untaxed * (obj.company_id.discount_value / 100)
        return amount    
    
    def untaxed_dis_amount(self,obj):
        dis_amount=self.dis_amt(obj)
        amount = obj.amount_untaxed -  dis_amount
        return amount        
    
    def payment(self,obj):
        day=self.pool['account.payment.term.line']
        fyear_ids=day.browse(self.cr, self.uid,obj.payment_term.id,context=self.context)[0]
        if str(fyear_ids.days) == '0':          
            return True
        else:
            return False
    

                   
class wrapped_report_invoice(osv.AbstractModel):
    _name = 'report.fnet_gst_invoice.report_invoice'
    _inherit = 'report.abstract_report'
    _template = 'fnet_gst_invoice.report_invoice'
    _wrapped_report_class = invoice_report1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
