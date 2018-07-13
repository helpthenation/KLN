from openerp import models,fields,api,_
    
    
class account_invoice(models.Model):
    
    _inherit='account.invoice'
        
    
    comment = fields.Char('Line',invisible=True)

        
    # OVERRIDE CONCEPT
    
    
    ''' 
   class account_invoice_line(models.Model):
    
    _inherit='account.invoice.line'
        
    
    line_ids = fields.Char('Line',invisible=True)
    @api.multi
    def name_get(self):
 
        res = super(res_partner, self).name_get()
        data = []
        for name in self:
            display_value = ''
            display_value += name.name or ""
            display_value += ',' 
            display_value += name.phone or ""
            
            data.append((name.id, display_value))
        return data
    '''
