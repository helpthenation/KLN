from openerp import api, models

from openerp.osv import osv,fields

from openerp.tools.amount_to_text_en import amount_to_text
from openerp.tools import amount_to_text_en

import datetime

class ParticularReport(models.AbstractModel):
   
    _name = 'report.tax_invoice.report_complain'
    _inherit = 'account.voucher'   
  
    def order_no(self,obj):
        if obj:
            stock_move=self.env['stock.move'].search([('origin','=',obj.origin)])
            
            for rec in stock_move:
                
                return rec.name
   
    def name(self,obj):
        if obj:
            stock_pick=self.env['stock.picking'].search([('origin','=',obj.origin)])
            print'1111111111111111111111111' , stock_pick
            for rec in stock_pick:
                
                return rec.name      

    def min_date(self,obj):
        if obj:
            stock_picks = self.env['stock.picking'].search([('origin','=',obj.origin)])
            
            print'222222222222222222222222222222222222' , stock_picks
            for run in stock_picks:
                date_time = datetime.datetime.strptime((run.min_date), '%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y')
                return date_time 
                
    def acc_number(self,obj):
        if obj:
            bank_det = self.env['res.partner.bank'].search([('origin','=',obj.origin)])
            
            print'3333333333333333333333333333333333333333333333333333333333333' , bank_det
            for refn in stock_picks:
                
                return run.acc_number                            
            
    def document_no(self,obj):
        if obj:
            stock_move=self.env['stock.move'].search([('origin','=',obj.origin)])

            for res in stock_move:
                
                return res.origin
            
    
    
    def despatch_through(self,obj):
        if obj:
            sale_order=self.env['sale.order'].search([('name','=',obj.origin)])
            
            for rek in sale_order:
                
                return rek.incoterm.name
                
    def price_unit(self,obj):
        
        print "LLLLLLLLLLLL",obj    
        split_num = str(obj).split('.')
        int_part = int(split_num[0])
        decimal_part = int(split_num[1])
        print 'FFFFFF decimal_part',decimal_part
        if decimal_part == 0:
            number_days = str(int_part) + '.00' 
            print '*************** number_days' , number_days
            
            return number_days
            
    def price_subtotal(self,obj):
        
        
        split_num = str(obj).split('.')
        int_part = int(split_num[0])
        decimal_part = int(split_num[1])
        print 'FFFFFF decimal_part',decimal_part
        if decimal_part == 0:
            number_days = str(int_part) + '.00' 
            
            
            return number_days
            
    def amount_untaxed(self,obj):
        
        
        split_num = str(obj).split('.')
        int_part = int(split_num[0])
        decimal_part = int(split_num[1])
        
        if decimal_part == 0:
            number_days = str(int_part) + '.00' 
            print '99999999999999999999999999999999999999 number_days' , number_days
            
            return number_days  
            
    
    def amount_total(self,obj):
        if obj:
            amount = obj.amount_total
            currency_id = obj.currency_id.id
            return amount_to_text(amount, currency_id)
        #~ if obj:
            #~ amount = obj.amount_total
            #~ currency_id = obj.currency_id.id
          
            #~ return amount_to_text_en(amount, currency_id)
            
            #~ print 'RRRRRRRRRRR' , amount
            #~ print 'EEEEEEEEEEEEEEE' , currency_id
   
    def date_invoice(self,obj):    
        if obj:
            print 'YYYYYYYYYYYYYYYYYYYYYY' , obj.origin
            leave_form = self.env['account.invoice'].search([('name','=',obj.origin)])
            date_time = datetime.strptime((obj.date_invoice), '%Y-%m-%d').strftime('%d-%m-%Y')                                                                         
            print'!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! date_time' , date_time
            return date_time     
            
     
    
    
                  
    @api.multi
    def render_html(self, data=None):
        print 'UUUUUUUUUUUUUUUUUU', self.id
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('tax_invoice.report_complain')
        leave_form=self.env['account.invoice'].search([('id','=',self.id)])
        print '*********8', leave_form.partner_id
        print '*********8', leave_form.id
        #_amount_to_text = self.env['account.voucher']._amount_to_text(amount, currency_id)
        sale_order=self.env['sale.order'].search([('name','=',leave_form.origin)])
        print '*************', sale_order
        docargs = {
            'doc_ids': leave_form,
            'sale':sale_order,
            #'number':_amount_to_text,
            'doc_model': report.model,
            'docs': self,
        }
              
        return report_obj.render('tax_invoice.report_complain', docargs)


            
    
