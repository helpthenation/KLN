from openerp import models,fields,api,_
import openerp.addons.decimal_precision as dp

class account_invoice_line(models.Model):
    _inherit = "account.invoice.line"    
    
    mrp_price = fields.Float(string="MRP Price",digits= dp.get_precision('Product Price'),)

    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        result = super(account_invoice_line,self).product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None)
        values={}
        product = self.env['product.product'].browse(product)
        self.mrp_price = product.mrp_price
        return result
