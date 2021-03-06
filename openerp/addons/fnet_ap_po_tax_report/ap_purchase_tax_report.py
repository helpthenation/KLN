from openerp import api,fields,models,_
from datetime import datetime
from openerp.exceptions import Warning
import time
from datetime import datetime
from dateutil import relativedelta

class ap_po_report(models.Model):
    
    _name="ap.po.report"    
    

            
    from_date =fields.Date("From Date" ,required="True")
    to_date=fields.Date("To Date" ,required="True")
    categ_id=fields.Many2one('product.category','Product Category')
    company_id=fields.Many2one('res.company',default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('ap.po.report')))
    ap_po_tax_ids=fields.One2many('ap.purchase.tax.details','tax_id',"Purchase Tax Return",readonly="True")
    inpopup=fields.Boolean('Inview',default=True)

    _defaults = {
         'from_date': lambda *a: time.strftime('%Y-%m-01'),
         'to_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }
    @api.multi
    def get_report(self):
        
        self.ap_po_tax_ids.unlink()   
        vals={}
        if self.from_date and self.to_date:
            if self.from_date<=self.to_date: 
                print self.categ_id.name    
                self.env.cr.execute(" select distinct ai.name,po.partner_id, rp.tin_vat_no, ai.id as invoice_id, ai.date_invoice,  "\
                            " po.amount_total from purchase_order po"\
                            " join purchase_invoice_rel pir on (pir.purchase_id = po.id) "\
                            " join account_invoice ai on (ai.id = pir.invoice_id)"\
                            " join account_invoice_line ail on (ai.id = ail.invoice_id)"\
                            " join product_product pp on (pp.id = ail.product_id)"\
                            " join product_template pt on (pt.id = pp.product_tmpl_id)"\
                            " join product_category pc on (pc.id = pt.categ_id)"\
                            " join res_partner rp on (rp.id=po.partner_id)"\
                            " where ai.state in ('paid','open') and pt.type!='service' and "\
                            "ai.date_invoice >= '%s' and ai.date_invoice <= '%s' "\
                            "and pt.categ_id=%s order by 1" % (str(self.from_date),str(self.to_date),self.categ_id.id))
                line_list = [i for i in self.env.cr.dictfetchall()]
                for line in line_list:
                    vals={
                        'ap_po_tax_ids':[(0,0,{
                        'seller_tin':line['tin_vat_no'],
                        'invoice_id':line['invoice_id'],
                        'invoice_date':line['date_invoice'],
                        'tax_rate':14.50,
                        'amount_total':line['amount_total'],
                        'categ_id':self.categ_id.id,
                    })] }
                    self.write(vals)  
            
            else:
                raise Warning(_('To Date Always Greater Than From Date '))
        self.write({'inpopup':False})
   
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ap.po.report',
            'res_id':self.id,
            'target': 'current',
            'context': self.env.context,
        }
    

    
class ap_purchase_tax_details(models.Model):
    
    _name="ap.purchase.tax.details"
    
    tax_id=fields.Many2one('ap.po.report')
    seller_tin=fields.Char('Seller Tin')
    invoice_id=fields.Many2one('account.invoice',"Invoice No")
    invoice_date=fields.Date('Invoice Date')
    categ_id=fields.Many2one('product.category','Name of the commadity')
    tax_rate=fields.Float('Rate of Tax %')
    amount_total=fields.Float('Total Value Including VAT in Rupees')
    
        
