
from openerp.osv import fields, osv
from openerp import models,fields,api,_
import openerp.addons.decimal_precision as dp


class Purchase_Order_line(models.Model):
    _inherit='purchase.order.line'   
        
    discounts = fields.Float('Discount',digits=dp.get_precision('Account'),default=0.00)
    disc_price_unit = fields.Float('Disc. Unit Price',digits=dp.get_precision('Account'))
    gross_amount = fields.Float('Gross Amount')
    product_discount = fields.Float('Product Discount')
         
    
    @api.one
    @api.onchange('discounts','product_qty','price_unit')
    def _discount_compute_amount(self):  
        self.gross_amount=self.product_qty*self.price_unit
        self.disc_price_unit = self.price_unit - self.discounts       
        self.product_discount=self.product_qty*self.discounts
    
    def _calc_line_base_price(self, cr, uid, line, context=None):
        return line.price_unit - line.discounts     

