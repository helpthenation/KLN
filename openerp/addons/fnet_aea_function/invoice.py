
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from openerp.tools import float_compare
import openerp.addons.decimal_precision as dp

import itertools
from lxml import etree

class account_invoice(models.Model):
    _inherit = 'account.invoice'

    category_id = fields.Many2one('product.category', string='Product Category',
        readonly=True, states={'draft': [('readonly', False)]},
        help="The partner account used for this invoice.")
    
    category_ref_id = fields.Many2one('product.category', string='Product Category',
        help="The partner account used for this invoice.")
        
    payment_term = fields.Many2one('account.payment.term', string='Payment Terms',
        readonly=True, states={'draft': [('readonly', False)]},
        help="If you use payment terms, the due date will be computed automatically at the generation "
             "of accounting entries. If you keep the payment term and the due date empty, it means direct payment. "
             "The payment term may compute several due dates, for example 50% now, 50% in one month.")
        
    number = fields.Char(related='move_id.name', store=True, readonly=True, copy=False)
    categ_number = fields.Char(string='Category Number', store=True, readonly=True, copy=False)
    categ_number_ref = fields.Char(string='Category Number Ref', store=True, readonly=True, copy=False)
    del_method = fields.Selection([('van', 'Van'),('lorry', 'Lorry'),('direct', 'Direct')], 'Delivery Method', required=True)
    tpt_name = fields.Many2one('res.partner', string='TPT.Co. Name')
    dispatch = fields.Boolean(string='Dispatched',readonly=True)
    

    @api.multi
    def _category_number(self):
        print self.categ_number
        print self.category_ref_id.id
        if self.categ_number_ref is False and self.category_ref_id.id is False:
            seq = self.env['ir.sequence'].next_by_code(str(self.category_id.category_code)) or 'New'
            self.write({'categ_number': seq, 'category_ref_id':self.category_id.id, 'categ_number_ref':seq})
        elif self.category_id.id == self.category_ref_id.id:
            self.write({'categ_number': self.categ_number_ref})
        else:
            if self.category_id.id <> self.category_ref_id.id:
                dd = self.env['ir.sequence'].get(str(self.categ_number_ref))
        return True
    
    @api.multi
    def invoice_validate(self):
        self._category_number()
        return self.write({'state': 'open'})
    
class account_invoice_line(models.Model):

    _inherit = 'account.invoice.line'

    mrp_price = fields.Float(string='MRP Price', digits=dp.get_precision('Account'))
    
    @api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice',
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False,
            company_id=None):
        context = self._context
        company_id = company_id if company_id is not None else context.get('company_id', False)
        self = self.with_context(company_id=company_id, force_company=company_id)

        if not partner_id:
            raise except_orm(_('No Partner Defined!'), _("You must first select a partner!"))
        if not product:
            if type in ('in_invoice', 'in_refund'):
                return {'value': {}, 'domain': {'uos_id': []}}
            else:
                return {'value': {'price_unit': 0.0}, 'domain': {'uos_id': []}}

        values = {}

        part = self.env['res.partner'].browse(partner_id)
        fpos = self.env['account.fiscal.position'].browse(fposition_id)

        if part.lang:
            self = self.with_context(lang=part.lang)
        product = self.env['product.product'].browse(product)

        values['name'] = product.partner_ref
        if type in ('out_invoice', 'out_refund'):
            account = product.property_account_income or product.categ_id.property_account_income_categ
        else:
            account = product.property_account_expense or product.categ_id.property_account_expense_categ
        account = fpos.map_account(account)
        if account:
            values['account_id'] = account.id
        print '******************8'
        if type in ('out_invoice', 'out_refund'):
            taxes = product.taxes_id or account.tax_ids
            values['mrp_price'] = product.mrp_price
            values['discounts'] = product.discount_price
            if product.description_sale:
                values['name'] += '\n' + product.description_sale
        else:
            taxes = product.supplier_taxes_id or account.tax_ids
            values['discounts'] = product.purchase_discount
            if product.description_purchase:
                values['name'] += '\n' + product.description_purchase
        part_obj=self.env['res.partner'].browse(partner_id)
        com_obj=self.env['res.company'].browse(company_id)   
        news=[]
        if part_obj.state_id.code and com_obj.state_id.code  != False:
            if  part_obj.state_id.code != com_obj.state_id.code:
                for i in taxes:
                    if i.ref_code == '3':
                        news.append(i.ids[0])
            elif part_obj.state_id.code == com_obj.state_id.code:   
                for i in taxes:
                    if i.ref_code != '3':
                        news.append(i.ids[0]) 
            tax_obj=self.env['account.tax'].browse(news)    
            taxes=tax_obj
        else:
            taxes=taxes
        fp_taxes = fpos.map_tax(taxes)
        values['invoice_line_tax_id'] = fp_taxes.ids            
        if type in ('in_invoice', 'in_refund'):
            if price_unit and price_unit != product.standard_price:
                values['price_unit'] = price_unit
            else:
                values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.standard_price, taxes, fp_taxes.ids)
        else:
            values['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.lst_price, taxes, fp_taxes.ids)

        values['uos_id'] = product.uom_id.id
        if uom_id:
            uom = self.env['product.uom'].browse(uom_id)
            if product.uom_id.category_id.id == uom.category_id.id:
                values['uos_id'] = uom_id

        domain = {'uos_id': [('category_id', '=', product.uom_id.category_id.id)]}


        company = self.env['res.company'].browse(company_id)
        currency = self.env['res.currency'].browse(currency_id)

        if company and currency:
            if company.currency_id != currency:
                values['price_unit'] = values['price_unit'] * currency.rate

            if values['uos_id'] and values['uos_id'] != product.uom_id.id:
                values['price_unit'] = self.env['product.uom']._compute_price(
                    product.uom_id.id, values['price_unit'], values['uos_id'])
        return {'value': values, 'domain': domain}

    

    
