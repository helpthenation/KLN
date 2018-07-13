
from openerp.osv import fields, osv
from openerp import models,fields,api,_
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_is_zero, float_compare,float_round
from openerp.tools import float_repr, float_round, frozendict, html_sanitize
import __builtin__


class Sale_Order_line(models.Model):
    _inherit='sale.order.line'   
        
    discounts = fields.Float('Discount',digits=dp.get_precision('Account'),default=0.00)
    disc_price_unit = fields.Float('Disc. Unit Price',digits=dp.get_precision('Account'))
    gross_amount = fields.Float('Gross Amount')
    product_discount = fields.Float('Product Discount')
         
    
    @api.one
    @api.onchange('discounts','product_uom_qty','price_unit')
    def _discount_compute_amount(self):
        self.gross_amount=self.product_uom_qty*self.price_unit
        self.disc_price_unit = self.price_unit - self.discounts       
        self.product_discount=self.product_uom_qty*self.discounts
        #~ self.write({'product_discount':self.product_uom_qty*self.discounts})
    
    def _calc_line_base_price(self, cr, uid, line, context=None):
         return line.price_unit * (1 - (line.discount or 0.0) / 100.0) - line.discounts
    

