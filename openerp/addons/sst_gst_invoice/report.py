from openerp import api, models,_
from openerp.osv import osv,fields
from openerp.tools.amount_to_text_en import amount_to_text
from datetime import datetime
from itertools import groupby
from operator import itemgetter
import re
from  amt_to_txt  import Number2Words
var = []
from openerp.tools.float_utils import float_is_zero, float_compare,float_round
from openerp.tools import float_repr, float_round, frozendict, html_sanitize
import __builtin__
import openerp.addons.decimal_precision as dp
class ParticularReport(models.AbstractModel):
   
    _name = 'report.sst_gst_invoice.report_invoice'
    _inherit = 'account.voucher'    

    def  product_name(self,obj):
        s=' '
        self.env.cr.execute("""select distinct name_template from account_invoice_line
                                        join account_invoice on account_invoice.id = account_invoice_line.invoice_id 
                                        left join product_product as pt on pt.id = account_invoice_line.product_id
                                        left join product_template as pp on pp.id = pt.product_tmpl_id
                                        where account_invoice_line.invoice_id = %d and pp.code IS NULL"""%(obj))
        q=self.env.cr.fetchall()
        for i in range(len(q)):         
                s+=str(q[i][0])+ ", "  
        s1=s.rindex(',')      
        s2=s[:s1] +'.'  
        return s2             
    def  hsn_code(self,obj):
        s=' '
        self.env.cr.execute("""select distinct pc.hsn_code from account_invoice_line
                                        join account_invoice on account_invoice.id = account_invoice_line.invoice_id 
                                        left join product_product as pt on pt.id = account_invoice_line.product_id
                                        left join product_template as pp on pp.id = pt.product_tmpl_id
                                        left join product_category as pc on pc.id = pp.categ_id
                                        where account_invoice_line.invoice_id = %d and pp.code IS NULL"""%(obj))
        q=self.env.cr.fetchall()
        for i in range(len(q)):         
                s+=str(q[i][0])+ ", "  
        s1=s.rindex(',')      
        s2=s[:s1] +'.'  
        return s2                                       
    def  tax_name(self,obj):
        res=[]
        igst=None
        value=''
        for i in obj.tax_line:
            res.append({'name':i.name,'amount':i.amount})
            if i.name[0:4].upper() != 'IGST':
                igst=False
        for i in res[0]['name'].split():
            for j in range(len(i)):
                if i[j].isdigit():
                    print i[j]
                    value+=str(i[j])
        if igst == False:
            tax='IGST Output @' + str( int(float(value)+float(value))) +'%'
            res.append({'name':tax,'amount':0.00})
        else:
            res.append({'name':'CGST Output @ '+str(int(float(value)/2))+'%','amount':0.00})
            res.append({'name':'SGST Output @ '+str(int(float(value)/2))+'%','amount':0.00})
        return res  
        
    def job_id(self,s):
        self.env.cr.execute("""select al.price_subtotal from account_invoice_line  as al
                                        left join product_product as pt on pt.id = al.product_id
                                        left join product_template as pp on pp.id = pt.product_tmpl_id
                                        where al.invoice_id = %d and pp.code = 'TP' """%(s))   
        ss = self.env.cr.fetchall()
        if ss == []:
            return 0.00
        else:
            e = ss[0][0]
            return e
    def numToWords(self,obj,join=True):
        self.env.cr.execute('''select distinct amount_total from account_invoice
                                                    join account_invoice_line
                                                    on account_invoice.id = account_invoice_line.invoice_id 
                                                    where account_invoice_line.invoice_id =%d'''%(obj))
        tqty=self.env.cr.fetchall()
        num = tqty[0][0]
        wGenerator = Number2Words()
        return wGenerator.convertNumberToWords(num)
        
    def amount_untaxed(self,obj):
        split_num = str(obj).split('.')
        int_part = int(split_num[0])
        decimal_part = int(split_num[1])
        if decimal_part == 0:
            number_days = str(int_part) + '.00'
            return number_days

    def amount_total(self,obj,currency='INR'):
        if obj:
            amount = obj.amount_total
            currency_id = obj.currency_id.id
            return amount_to_text(amount, currency_id)

    def date_invoice(self,obj):
        if obj:
            leave_form = self.env['account.invoice'].search([('name','=',obj.origin)])
            date_time = datetime.strptime((obj.date_invoice), '%Y-%m-%d').strftime('%d-%m-%Y')
            return date_time
 
    def product_date(self,obj):     
        self.env.cr.execute('''select sale_order_line.name,account_invoice_line.product_id,quantity  from account_invoice_line join sale_order_line on sale_order_line.product_id = account_invoice_line.product_id where invoice_id =%d'''%(obj))
        j = self.env.cr.fetchall()
        self.env.cr.execute("""select product_id 
                                        from account_invoice_line 
                                        join account_invoice on account_invoice.id = account_invoice_line.invoice_id 
                                        left join product_product as pt on pt.id = account_invoice_line.product_id
                                        left join product_template as pp on pp.id = pt.product_tmpl_id
                                        where account_invoice_line.invoice_id = %d and pp.code IS NULL """%(obj))
        d = self.env.cr.fetchall()
        d1=list(set(d))
        l=[]
        ll=[]
        for i in range(len(d1)):
                    self.env.cr.execute(''' SELECT 
                                            PP.ID,
                                            PP.NAME_TEMPLATE,
                                            STRING_AGG((AV.NAME), ',' ORDER BY AV.ATTRIBUTE_ID ) ATT,
                                            (select sum(quantity)  from account_invoice_line where product_id=%d and invoice_id=%d ),
                                            AVI.PRICE_UNIT
                                            FROM
                                            PRODUCT_PRODUCT PP
                                            INNER JOIN PRODUCT_TEMPLATE PT ON PP.PRODUCT_TMPL_ID = PT.ID
                                            LEFT JOIN PRODUCT_ATTRIBUTE_VALUE_PRODUCT_PRODUCT_REL PR ON PP.ID = PR.PROD_ID
                                            LEFT JOIN PRODUCT_ATTRIBUTE_VALUE AV ON PR.ATT_ID = AV.ID
                                            LEFT JOIN ACCOUNT_INVOICE_LINE AVI ON PP.ID = AVI.PRODUCT_ID
                                            WHERE
                                            PP.ID = %d AND AVI.INVOICE_ID = %d AND  
                                            PP.ACTIVE = TRUE
                                            GROUP BY PP.ID, PP.NAME_TEMPLATE, AVI.PRICE_UNIT
                                            ORDER BY PP.NAME_TEMPLATE '''%(d1[i][0],obj,d1[i][0],obj))
                    p=self.env.cr.fetchall()
                    l.extend(p)        

        d2=[]
        s=[]
        at=[]
        for i in range(len(l)):
                if l[i][2] != None:
                            sf=re.sub('[()]',' ',l[i][2])
                            ff=sf.split(',')
                            f=sorted(set(ff), key=lambda x: ff.index(x))
                            if len(f)>=2:
                                llp=(l[i][0],l[i][1],f[0],f[1],l[i][3],l[i][4])
                                s.append(llp)
                            elif len(f)==1:
                                d=' '
                                llp=(l[i][0],l[i][1],f[0],d,l[i][3],l[i][4])
                                s.append(llp)
                                    
                elif l[i][2] == None:
                           d=' ' 
                           d1=' '
                           llp=(l[i][0],l[i][1],d,d1,l[i][3],l[i][4]) 
                           s.append(llp)
        for i in range(len(l)):
                if l[i][2] != None:
                            sf=re.sub('[()]',' ',l[i][2])
                            ff=sf.split(',')
                            f=sorted(set(ff), key=lambda x: ff.index(x))
                            if len(f)>=2:
                                llp=(l[i][0],l[i][1],f[0],f[1],l[i][3],l[i][4])
                                at.append(llp)
                            elif len(f)==1:
                                d=' '
                                llp=(l[i][0],l[i][1],f[0],d,l[i][3],l[i][4])
                                at.append(llp)
                elif l[i][2] == None:
                           d=' ' 
                           d1=' '
                           llp=(l[i][0],l[i][1],d,d1,l[i][3],l[i][4])
                           at.append(llp)
        ss= sorted(at,reverse=True)
        print ss
        data = sorted(s, key=itemgetter(1,2))
        a = {k: list(v) for k, v in groupby(data, key=itemgetter(1,2))}
        lol = lambda lst, sz: [lst[i:i+sz] for i in range(0, len(lst), sz)]
        new_res=[]
        res=[]
        new=[]
        for key, value in a.iteritems():
            if len(value) > 6:
                lop=lol(value,6)
                for j in lop: 
                     test=[]
                     for g in j:             
                          test.append({'id': g[0],
                          'product':g[1],
                          'color': g[2],
                          'size': str(g[3]),
                          'qty': g[4],
                          'price':g[5]})
                     new.append({key:test})
            else:
                best=[]
                for g in value:
                  best.append({'id': g[0],
                  'product':g[1],
                  'color': g[2],
                  'size': str(g[3]),
                  'qty': g[4],
                  'price':g[5]})    
                new.append({key:best})
        for i in range(len(new)):
            g=new[i]  
            for key,value in g.iteritems():
                for i in value:
                    if i['size'].isdigit():
                        i['size'] = int(i['size'])
                        i.update({'asc':int(i['size'])})
                    elif i['size'].isalpha():
                        i['size'] = str(i['size'])
                        i.update({'asc':str(i['size'])})
                    elif i['size'] == ' ':
                        i['size']=None
                        i.update({'asc':' '})
                    elif not i['size'].isalnum():
                        i['size'] = str(i['size'])  
                        for o in i['size']:
                            if not o.isalnum():
                                hh=o
                        h=i['size'].split(hh)
                        if h[0].isdigit():
                            i.update({'asc':int(h[0])})
                        elif h[0].isalpha():
                            i.update({'asc':str(h[0])})
                        else:
                            i.update({'asc':' '})       
                    else:
                        i.update({'asc':' '})   
                                                      
                if key == ' ':
                     pass
   
                else:
                     new_res.append({
                                                       'product': key[0],
                                                       'color': key[1],
                                                       'attribute':sorted(value,key=lambda k: k['asc'])})
        for i in new_res:
 
            i.update({'price':i['attribute'][0]['price']})
        return new_res                                            
                                              
    def total_qty(self,obj):
        self.env.cr.execute('''select sum(quantity) from account_invoice_line
                                                   join account_invoice on account_invoice.id = account_invoice_line.invoice_id 
                                                   left join product_product as pt on pt.id = account_invoice_line.product_id
                                                left join product_template as pp on pp.id = pt.product_tmpl_id
                                                where account_invoice_line.invoice_id = %d and pp.code IS NULL;'''%(obj))
        tqty=self.env.cr.fetchall()
        return int(tqty[0][0])                                            

    def total(self,obj):
        result = __builtin__.float(obj or 0.0)
        precision, scale = (16, 2)
        result = float_repr(float_round(result, precision_digits=scale), precision_digits=scale)
        return result
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sst_gst_invoice.report_invoice')
        leave_form=self.env['account.invoice'].browse(self.ids)
        #~ sale_order=self.env['sale.order'].search([('name','=',leave_form.origin)])
        #~ print '*************', sale_order
        account_inv = self.env['account.invoice.line'].search([('id','=',self.ids)])
        for order in leave_form.browse(self.ids):
            if order.state:
                if order.state == 'draft':
                    raise osv.except_osv(_("Warning!"), _("You Cannot Print Report In Draft State ...!! "))
        #_amount_to_text = self.env['account.voucher']._amount_to_text(amount, currency_id)

            docargs = {
                'doc_ids': self._ids,
                #~ 'sale':sale_order,
                'doc':leave_form,
                'account':account_inv,
                'doc_model': report.model,
                'docs': self,
            }

            return report_obj.render('sst_gst_invoice.report_invoice', docargs)


#~ product_product.name_template :: text not ILIKE 'Service%'
