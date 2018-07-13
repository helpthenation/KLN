from __future__ import division
from openerp.osv import fields, osv
from openerp import models,fields,api,_
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_is_zero, float_compare,float_round
from openerp.tools import float_repr, float_round, frozendict, html_sanitize
import __builtin__
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from datetime import *; from dateutil.relativedelta import *
class saleorder_discount(models.Model):
    _inherit = 'sale.order'

    disc_value=fields.Float(string='Discount Percentage',digits=dp.get_precision('Discount'),default=0.0)
    cust_credit=fields.Float(string='Receivable Amount',related='partner_id.credit')
    discounted_amount = fields.Float(
    compute='disc_amount',digits=dp.get_precision('Discount'),
    string='Discounted Amount', readonly=True)
    amount_totals = fields.Float(string='Total', digits=dp.get_precision('Discount'),
                                compute='_compute_amounts'
                                )
    amount_taxs = fields.Float(string='Total', digits=dp.get_precision('Discount'),
                                compute='_compute_amounts'
                                )
    @api.multi
    @api.onchange('payment_term')
    def _discount_value(self):
        day=self.env['account.payment.term.line']
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        if str(fyear_ids.days) == '0':
            self.disc_value=self.company_id.discount_percentage
        self.write({'disc_value':self.company_id.discount_percentage})    

    def onchange_partner_id(self, cr, uid, ids, part, context=None):        
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}
        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        if  not part.gst_number:
            return {'warning': {
                    'title': "Warning",
                    'message': "Please Provide GSTIN Number For Selected Partner!!! \n OR \n Select Different Partner",
                    },
                   'value': {'partner_id':False}
                }      
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        invoice_part = self.pool.get('res.partner').browse(cr, uid, addr['invoice'], context=context)
        payment_term = invoice_part.property_payment_term and invoice_part.property_payment_term.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'user_id': dedicated_salesman,
        }
        delivery_onchange = self.onchange_delivery_id(cr, uid, ids, False, part.id, addr['delivery'], False,  context=context)
        val.update(delivery_onchange['value'])
        if pricelist:
            val['pricelist_id'] = pricelist
        if not self._get_default_section_id(cr, uid, context=context) and part.section_id:
            val['section_id'] = part.section_id.id
        sale_note = self.get_salenote(cr, uid, ids, part.id, context=context)
        if sale_note: val.update({'note': sale_note})
        day=self.pool['account.payment.term.line']
        fyear_ids=day.search(cr, uid, [('payment_id', '=', val['payment_term'])], context=context)
        #~ print'fyear_ids',day.browse(cr,uid,fyear_ids).days
        company_id=self.pool.get('res.company')._company_default_get(cr,uid,'sale.order')
        com_obj=self.pool.get('res.company').browse(cr, uid,company_id)
        if str(day.browse(cr,uid,fyear_ids).days) == '0':
            val['disc_value']=com_obj.discount_percentage   
        return {'value': val}
           
    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        sale_obj = self.browse(cr, uid)
        day=self.pool['account.payment.term.line']
        fyear_ids=day.search(cr, uid, [('payment_id', '=', line.order_id.payment_term.id)], context=context)
        company_id=self.pool.get('res.company')._company_default_get(cr,uid,'sale.order')
        com_obj=self.pool.get('res.company').browse(cr, uid,company_id)
        
        line_obj = self.pool['sale.order.line']
        price = line_obj._calc_line_base_price(cr, uid, line, context=context)
        if str(day.browse(cr,uid,fyear_ids).days) == '0' and line.order_id.disc_value != 0.0:
            prices = price * (1 - (line.order_id.disc_value or 0.00) / 100.0)
        elif str(day.browse(cr,uid,fyear_ids).days) == '0' and line.order_id.disc_value == 0.0:
            prices = price * (1 - (com_obj.discount_value or 0.00) / 100.0)            
        else:
            prices = price  
        qty = line_obj._calc_line_quantity(cr, uid, line, context=context)
        company_id=self.pool.get('res.company')._company_default_get(cr,uid,'sale.order.line')
        com_obj=self.pool.get('res.company').browse(cr, uid,company_id)
        
        for c in self.pool['account.tax'].compute_all(
                cr, uid, line.tax_id, prices, qty, line.product_id,
                line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0) or 0.0
        return val
        
    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            day=self.pool['account.payment.term.line']
            fyear_ids=day.search(cr, uid, [('payment_id', '=', order.payment_term.id)], context=context)
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            if str(day.browse(cr,uid,fyear_ids).days) == '0' and order.disc_value != 0.0:
                amount_to_dis = cur_obj.round(cr, uid, cur,((order.amount_untaxed) * (order.disc_value / 100)))
                res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] - amount_to_dis
            elif str(day.browse(cr,uid,fyear_ids).days) == '0' and order.disc_value == 0.0:
                amount_to_dis = cur_obj.round(cr, uid, cur,((order.amount_untaxed) * (order.company_id.discount_value / 100)))       
                res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] - amount_to_dis        
            else:           
                res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']
        return res        
    @api.one
    @api.depends('order_line.price_subtotal','disc_value','payment_term')
    def disc_amount(self):
        day=self.env['account.payment.term.line']
        TODAY = datetime.strptime(self.date_order, '%Y-%m-%d %H:%M:%S')       
        orders=TODAY.strftime('%Y-%m-%d') 
        order=datetime.strptime(orders,'%Y-%m-%d') 
        check_date=datetime.strptime('2017-07-01','%Y-%m-%d') 
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        if str(fyear_ids.days) == '0' and self.disc_value != 0.0 and order >= check_date:
            amount_to_dis = self.amount_untaxed * (self.disc_value / 100)
            self.discounted_amount = amount_to_dis
        elif str(fyear_ids.days) == '0' and self.disc_value == 0.0 and order >= check_date:
            amount_to_dis = self.amount_untaxed * (self.company_id.discount_value / 100)
            self.discounted_amount = amount_to_dis            
        else:
            self.discounted_amount = 0        

    @api.one
    @api.depends('order_line.price_subtotal','payment_term','amount_untaxed','amount_tax','order_line')
    def _compute_amounts(self):
        day=self.env['account.payment.term.line']
        TODAY = datetime.strptime(self.date_order, '%Y-%m-%d %H:%M:%S')       
        orders=TODAY.strftime('%Y-%m-%d') 
        order=datetime.strptime(orders,'%Y-%m-%d') 
        check_date=datetime.strptime('2017-07-01','%Y-%m-%d')         
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        self.amount_untaxed = sum(line.price_subtotal for line in self.order_line)
        val = 0
        for line in self.order_line:
            val += self._amount_line_tax(line)
        self.amount_tax=val
        if str(fyear_ids.days) == '0' and self.disc_value != 0.0 and order >= check_date:
            amount_to_dis = (self.amount_untaxed) * (self.disc_value / 100)
            self.amount_total = self.amount_untaxed + val - amount_to_dis
            print'IFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',self.amount_total
        elif str(fyear_ids.days) == '0' and self.disc_value == 0.0 and order >= check_date:
            amount_to_dis = (self.amount_untaxed) * (self.company_id.discount_value / 100)        
            self.amount_total = self.amount_untaxed + val - amount_to_dis            
            print'ELIFFFFFFFFFFFFFFFFFFFFFFFFF',self.amount_total
        else:
            self.amount_total = self.amount_untaxed + val
            print'ELSEEEEEEEEEEEEEEEEEEEEEEE',self.amount_total

saleorder_discount()
