from openerp import api,fields,models,_
from datetime import datetime
from openerp.exceptions import Warning
import time
from datetime import datetime
from dateutil import relativedelta

class ka_sale_report(models.Model):
    
    _name="ka.sale.report"    
    

            
    from_date =fields.Date("From Date" ,required="True")
    to_date=fields.Date("To Date" ,required="True")
    categ_id=fields.Many2one('product.category','Product Category')
    company_id=fields.Many2one('res.company',default=lambda self: self.env['res.company'].browse(self.env['res.company']._company_default_get('ka.sale.report')))
    ka_so_tax_ids=fields.One2many('ka.sale.tax.details','tax_id',"Sale Tax Return",readonly="True")
    inpopup=fields.Boolean('Inview',default=True)

    _defaults = {
         'from_date': lambda *a: time.strftime('%Y-%m-01'),
         'to_date': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
    }
    @api.multi
    def get_report(self):
        
        self.ka_so_tax_ids.unlink()   
        vals={}
        if self.from_date and self.to_date:
            if self.from_date<=self.to_date:  
                self.env.cr.execute(" select distinct ai.number,so.partner_id, rp.tin_vat_no, ai.id as invoice_id, ai.date_invoice,  "\
                            " so.amount_total, so.amount_tax, so.amount_untaxed  from sale_order so"\
                            " join sale_order_invoice_rel soil on (soil.order_id = so.id) "\
                            " join account_invoice ai on (ai.id = soil.invoice_id)"\
                            " join account_invoice_line ail on (ail.invoice_id = ai.id)"\
                            " join product_category pc on (pc.id = ai.category_id)"\
                            " join res_partner rp on (rp.id=so.partner_id)"\
                            " where ai.state in ('paid','open') and "\
                            "ai.date_invoice >= '%s' and ai.date_invoice <= '%s' "\
                            "and ai.category_id=%s order by 1" % (str(self.from_date),str(self.to_date),self.categ_id.id))
                line_list = [i for i in self.env.cr.dictfetchall()]
                for line in line_list:
                    vals={
                        'ka_so_tax_ids':[(0,0,{
                        'partner_id':line['partner_id'],
                        'buyer_tin':line['tin_vat_no'],
                        'invoice_id':line['invoice_id'],
                        'invoice_date':line['date_invoice'],
                        'amount_untaxed':line['amount_untaxed'],
                        'other_charges':0.0,
                        'amount_total':line['amount_total'],
                        'amount_taxed':line['amount_tax'],
                  
                    })] }
                    self.write(vals)  
            
            else:
                raise Warning(_('To Date Always Greater Than From Date '))
        self.write({'inpopup':False})
   
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ka.sale.report',
            'res_id':self.id,
            'target': 'current',
            'context': self.env.context,
        }
    

    
class ka_sale_tax_details(models.Model):
    
    _name="ka.sale.tax.details"
    
    tax_id=fields.Many2one('ka.sale.report')
    partner_id=fields.Many2one('res.partner',"Name Of Buyer")
    buyer_tin=fields.Char('Buyer Tin')
    invoice_id=fields.Many2one('account.invoice',"Invoice No")
    invoice_date=fields.Date('Invoice Date')
    amount_untaxed=fields.Float('Net Value')
    amount_taxed=fields.Float('Tax Value')
    other_charges=fields.Float('Other Charges')
    amount_total=fields.Float('Total Value')
    
        
