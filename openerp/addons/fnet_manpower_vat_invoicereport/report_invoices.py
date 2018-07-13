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
from openerp import api, models,_
import datetime
import math
from openerp.exceptions import except_orm,ValidationError,Warning
from datetime import datetime
class ParticularReport(models.AbstractModel):
    _name = 'report.fnet_manpower_vat_invoicereport.report_invoices' 
    
    def get_date(self,val):
        if val:
            return datetime.strptime(str(val), '%Y-%m-%d').strftime('%b %d, %Y')
            
            
    def get_int(self,val):
        if val:
            return int(val)
            
    def get_job_no(self,val):
        if val:
            sale_obj = self.env['sale.order']
            sale_obj_id = sale_obj.search([('name','=',val)])
            if sale_obj_id:
                sale_re=sale_obj.browse(sale_obj_id.id)
                return sale_re.job_id
        
    def get_amount(self,obj,val):
        count=0
        if obj:
            self.env.cr.execute("""select ail.name as name         
                             from account_invoice_line ail 
                             left join product_uom pu on (pu.id=ail.uos_id)
                             left join product_product pp on (pp.id= ail.product_id) 
                             left join product_template pt on (pt.id= pp.product_tmpl_id) 
                             where ail.invoice_id=%s order by ail.id asc"""% (str(obj.ids[0])))
        line_list = [i for i in self.env.cr.dictfetchall()]
        desc_len=[]
        for i in line_list:
            txt=i['name'].split('\n')
            desc_len.append(len(txt))  
        if sum(desc_len):
            count= math.ceil(float(count + sum(desc_len))/float(12.0))        
        if (count-1) == val:
            val='{0:.2f}'.format(obj.amount_total)
            amount='{:20,.2f}'.format(float(val))
            return amount
        else:
            return "Continued"
        
    def numtowords(self,num,join=True):
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
          
    def invoice_line(self,obj):
        count=0
        lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
        if obj:
            self.env.cr.execute("""select ail.name as name         
                             from account_invoice_line ail 
                             left join product_uom pu on (pu.id=ail.uos_id)
                             left join product_product pp on (pp.id= ail.product_id) 
                             left join product_template pt on (pt.id= pp.product_tmpl_id) 
                             where ail.invoice_id=%s order by ail.id asc"""% (str(obj.ids[0])))
        line_list = [i for i in self.env.cr.dictfetchall()]
        desc_len=[]
        for i in line_list:
            txt=i['name'].split('\n')
            desc_len.append(len(txt))               
        #~ print'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',sum(desc_len)
        if sum(desc_len) <= 12:
            count= count + 1
        elif sum(desc_len) > 12:
            count= math.ceil(float(count + sum(desc_len))/float(12.0))
        value=[]
        if count <= 1:
            value.append(0)
        else:
            for val in range(0,int(count)):
                value.append(val)
        return value
        
        
    def get_invoice_line(self,obj,val):      
        if obj:
            limit= 4
            self.env.cr.execute(" select ail.id,ail.name as name, "\
                            " pu.name as uom ,ail.quantity as quantity , ail.price_unit as price_unit,"\
                            " ail.price_subtotal as total from account_invoice_line ail "\
                            " left join product_uom pu on (pu.id=ail.uos_id)"\
                            " left join product_product pp on (pp.id= ail.product_id) "\
                            " left join product_template pt on (pt.id= pp.product_tmpl_id) "\
                            "where ail.invoice_id=%s  order by ail.id asc" % (str(obj.ids[0])))
        line_list = [i for i in self.env.cr.dictfetchall()]
        print'line_list',line_list
        desc=[]
        lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
        final=[]
        for i in line_list:
            txt=i['name'].split('\n')
            desc.append({'prod_desc':txt,'prod_qty':i['quantity'],'prod_uom':i['uom'],'price':i['price_unit'],'subtotal':i['total']})
        print'$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$',desc
        for i in desc:
            lop=[]
            lop=lol(i['prod_desc'],12)
            bob=[]
            for j in range(len(lop)):
                  if j == 0:
                      for k in lop[j]:
                            bob.append({'desc':k,'qty':None,'sno':None,'uom':None,'price':None,'subtotal':None})
                      if  bob[0]['desc']:
                          bob[0]['qty']=int(i['prod_qty'])
                          bob[0]['uom']=i['prod_uom']
                          bob[0]['price']=i['price']
                          bob[0]['subtotal']=i['subtotal']
                      else:
                          bob[1]['qty']=int(i['prod_qty'])
                          bob[1]['uom']=i['prod_uom']
                          bob[1]['price']=i['price']
                          bob[1]['subtotal']=i['subtotal']   
                  else:
                      for k in lop[j]:
                            bob.append({'desc':k,'qty':None,'sno':None,'uom':None,'price':None,'subtotal':None})
            final.extend(bob)              
        print'VVVVVVVVVVVVVVVVVVVVVVVV',final
        count=0
        for i in range(len(final)):
            if final[i]['qty'] != None:
                count+=1
                final[i]['desc']=final[i]['desc']              
                final[i]['sno']= str(count)  
        return_list=lol(final,12)    
        print'VALLLLLLLLLLLLLLLLLLL',val
        print'return_list',return_list
        return return_list[val]
        
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_manpower_vat_invoicereport.report_invoices')
        stock_pick=self.env['account.invoice'].browse(self.ids)
        #~ sale_order=self.env['sale.order'].search([('name','=',stock_pick.origin)])
        for order in stock_pick.browse(self.ids):
            if order.amount_tax <= 0.0:
                raise except_orm(_('Sorry!!!'), _("You Can't Print Non Tax Invoice."))          
            docargs = {
                'doc_ids': stock_pick,
                #~ 'sale':sale_order,
                'doc_model': report.model,
                'docs': self,
            }
            
            return report_obj.render('fnet_manpower_vat_invoicereport.report_invoices', docargs)
            
