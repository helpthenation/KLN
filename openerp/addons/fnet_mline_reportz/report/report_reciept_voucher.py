from openerp import api, models
from openerp.osv import osv
from openerp import api,_
from openerp.tools.amount_to_text_en import amount_to_text

class ParticularReport(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.report_reciept_voucher'
     
    
    #~ def _get_amd2text(self,obj):
        #~ tot = 0.0
        #~ if obj.partner_id.customer:
            #~ for rec in obj.line_cr_ids:
                #~ tot= tot + rec.amount
        #~ elif obj.partner_id.supplier:
            #~ for rec in obj.line_dr_ids:
                #~ tot= tot + rec.amount
        #~ res = self._amount_to_text(tot, obj.currency_id.id)
        #~ return res
        
    #~ def _amount_to_text(self, amount, currency):
        #~ cur = self.env['res.currency'].browse(currency)
        #~ if cur.name.upper() == 'AED':
            #~ currency_name = 'Dirham'
        #~ elif cur.name.upper() == 'INR':
            #~ currency_name = 'Rupees'
        #~ else:
            #~ currency_name = cur.name
        #~ #TODO : generic amount_to_text is not ready yet, otherwise language (and country) and currency can be passed
        #~ #amount_in_word = amount_to_text(amount, context=context)
        #~ return amount_to_text(amount, currency=currency_name)
        
    def numToWords(self,obj,join=True):
        '''words = {} convert an integer number into words'''
        amt=0.00
        if obj.partner_id.customer:
            for rec in obj.line_cr_ids:
                amt= amt + rec.amount
        elif obj.partner_id.supplier:
            for rec in obj.line_dr_ids:
                amt= amt + rec.amount
        num=0
        cent=0
        if '.' in str(("%.2f" % round(amt,2))):
            amount = str(amt).split('.')
            num = num + int(amount[0])
            cent = cent + int(amount[1])
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
        if cent >= 1 and cent < 10:
            cent= cent * 10
            words.append( "and "+ str(cent) +"/100 Only")
        elif cent < 1 and cent >= 10:
            words.append( "and "+ str(cent) +"/100 Only")
        if join: return ' '.join(words)
        return words

    def calculate_total(self,obj):
        if obj:
            num=0.0
            if obj.partner_id.customer:
                for rec in obj.line_cr_ids:
                    num= num + rec.amount
                return num 
            elif obj.partner_id.supplier:
                for rec in obj.line_dr_ids:
                    num= num + rec.amount
                return num 
            
    def amount(self,obj,line):
        if obj.partner_id.customer:
            for rec in obj.line_cr_ids:
                if rec.id == line.id:
                    return line.amount
        elif obj.partner_id.supplier:
            for rec in obj.line_dr_ids:
                if rec.id == line.id:
                    return line.amount
            
            
            
    @api.multi
    def render_html(self, data=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('fnet_mline_reportz.report_reciept_voucher')
        voucher_obj=self.env['account.voucher'].search([('id','=',self.id)])
        docargs = {
            'doc_ids': voucher_obj,
            'doc_model': report.model,
            'docs': self,
        }
        return report_obj.render('fnet_mline_reportz.report_reciept_voucher', docargs)                                                                                                                                                        
            
    
    

            
