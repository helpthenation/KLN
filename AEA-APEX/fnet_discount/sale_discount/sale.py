
from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow


class sale_order_line(osv.osv):
    _inherit='sale.order.line'
    
    #~ def _calc_line_base_price(self, cr, uid, line, context=None):
        #~ return line.disc_price_unit * (1 - (line.discount or 0.0) / 100.0)
    def _calc_line_base_price(self, cr, uid, line, context=None):
        print'+++++++++++++++++++++++++++++++++', self.pool['res.company']._get_default_company('sale.order.line') 
        return line.price_unit * (1 - (line.discount or 0.0) / 100.0) - line.discounts     
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = self._calc_line_base_price(cr, uid, line, context=context)
            qty = self._calc_line_quantity(cr, uid, line, context=context)
            taxes = tax_obj.compute_all(cr, uid, line.tax_id, price, qty,
                                        line.product_id,
                                        line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res
        

