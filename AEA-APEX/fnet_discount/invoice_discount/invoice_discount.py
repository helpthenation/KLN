from __future__ import division
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en


class invoice_discount(models.Model):
    _inherit = 'account.invoice.line'
    
    discounts = fields.Float('Discount',digits= dp.get_precision('Account'))
    disc_price_unit = fields.Float('Disc. Unit Price',digits= dp.get_precision('Account'))
    gross_amount = fields.Float('Gross Amount',digits=dp.get_precision('Discount'))
    product_discount = fields.Float('Product Discount',digits= dp.get_precision('Discount'))
        
    @api.one
    @api.depends('price_unit', 'discount', 'discounts', 'invoice_line_tax_id', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0 ) / 100.0) - self.discounts
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)


    @api.one
    @api.onchange('discounts','quantity','price_unit')
    def _discount_compute_amount(self):
        self.disc_price_unit = self.price_unit - self.discounts
        self.gross_amount=self.quantity*self.price_unit
        self.product_discount=self.quantity*self.discounts
