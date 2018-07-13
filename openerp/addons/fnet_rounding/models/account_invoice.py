from __future__ import division
from openerp import api, fields, models, _
from openerp.tools.float_utils import float_is_zero, float_compare,float_round
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en
from openerp.tools import float_repr, float_round, frozendict, html_sanitize
import __builtin__
import math
class account_invoice(models.Model):

    _inherit='account.invoice'
    
    disc_value=fields.Float(string='Discount Percentage',default=0.0)
    discounted_amount = fields.Float('Discounted Amount',digits=dp.get_precision('Discount'),compute='disc_amount',readonly=True)
    untaxed_dis_amount = fields.Float(compute='disc_amount',  digits=dp.get_precision('Account'),string='Untaxed Amount',readonly=True)
    product_discount_amount = fields.Float('Product Amount',digits=dp.get_precision('Discount'),compute='_compute_discount',  readonly=True)
    gross_amount_total = fields.Float(compute='_compute_discount', string='Gross Amount', readonly=True,digits= dp.get_precision('Account'))
    round_amount=fields.Float('Round off',digits=dp.get_precision('Discount'))
    #~ amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                #~ store=True, readonly=True, compute='_compute_amount')
    @api.one
    @api.onchange('payment_term')
    def _discount_value(self):
        day=self.env['account.payment.term.line']
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        if str(fyear_ids.days) == '0':
            self.disc_value=self.company_id.discount_percentage
        self.write({'disc_value':self.company_id.discount_percentage})   

    @api.multi
    def onchange_payment_term_date_invoice(self, payment_term_id, date_invoice):
        day=self.env['account.payment.term.line']
        fyear_ids=day.search([('payment_id', '=', payment_term_id)])
        if not date_invoice:
            date_invoice = fields.Date.context_today(self)
        if not payment_term_id:
            # To make sure the invoice due date should contain due date which is
            # entered by user when there is no payment term defined
            return {'value': {'date_due': self.date_due or date_invoice}}
        pterm = self.env['account.payment.term'].browse(payment_term_id)
        pterm_list = pterm.compute(value=1, date_ref=date_invoice)[0]
        if pterm_list:
            if str(fyear_ids.days) == '0':
                return {'value': {'date_due': max(line[0] for line in pterm_list),'disc_value':self.company_id.discount_percentage}}
            else:
                return {'value': {'date_due': max(line[0] for line in pterm_list)}} 
        else:
            raise except_orm(_('Insufficient Data!'),
                _('The payment term of supplier does not have a payment term line.'))        


                
    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount','payment_term','disc_value')
    def disc_amount(self):
        day=self.env['account.payment.term.line']
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        day=self.env['account.payment.term.line']
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        if str(fyear_ids.days) == '0' and self.disc_value != 0.0 and self.date_invoice>='2017-07-01':
            amount_to_dis = self.amount_untaxed * (self.disc_value / 100)
            self.discounted_amount = amount_to_dis
        elif str(fyear_ids.days) == '0' and self.disc_value == 0.0 and self.date_invoice>='2017-07-01':
            amount_to_dis = self.amount_untaxed * (self.company_id.discount_value / 100)
            self.discounted_amount = amount_to_dis            
        else:
            self.discounted_amount = 0
        self.untaxed_dis_amount=self.amount_untaxed-self.discounted_amount
    

          
    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'currency_id', 'company_id',)
    def _compute_discount(self):  
        self.product_discount_amount = sum(line.product_discount for line in self.invoice_line)
        self.gross_amount_total = sum(line.gross_amount for line in self.invoice_line)               
    
    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'currency_id', 'company_id','payment_term')
    def _compute_amount(self):  
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)   
        self.amount_total = self.amount_untaxed + self.amount_tax-self.discounted_amount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            amount_total_company_signed = self.currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = self.currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
    
    @api.multi
    def compute_invoice_totals(self, company_currency, ref, invoice_move_lines):
        day=self.env['account.payment.term.line']
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        total = 0
        total_currency = 0
        for line in invoice_move_lines:
            if self.currency_id != company_currency:
                currency = self.currency_id.with_context(date=self.date_invoice or fields.Date.context_today(self))
                line['currency_id'] = currency.id
                line['amount_currency'] = currency.round(line['price'])
                line['price'] = currency.compute(line['price'], company_currency)
            else:
                line['currency_id'] = False
                line['amount_currency'] = False
                line['price'] = self.currency_id.round(line['price'])
            line['ref'] = ref
            if self.type in ('out_invoice','in_refund'):
                total += line['price']
                total_currency += line['amount_currency'] or line['price']
                line['price'] = - line['price']
            else:
                total -= line['price']
                total_currency -= line['amount_currency'] or line['price']
        if str(fyear_ids.days) == '0' and self.type in ['out_invoice', 'out_refund']:        
        #~ if self.env.user.company_id.tax_calculation_rounding_method == 'rounding total amount' and self.type in ['out_invoice', 'out_refund']:
           total=total-self.discounted_amount
           return total,total_currency, invoice_move_lines
        else:
           return total,total_currency, invoice_move_lines
            #~ total=total-self.discounted_amount
        #~ return total,total_currency, invoice_move_lines
    
    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        day=self.env['account.payment.term.line']
        fyear_ids=day.search([('payment_id', '=', self.payment_term.id)])
        account_invoice_tax = self.env['account.invoice.tax']
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise except_orm(_('Error!'), _('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line:
                raise except_orm(_('No Invoice Lines!'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            company_currency = inv.company_id.currency_id
            # create the analytical lines, one move line per invoice line
            iml = inv._get_analytic_lines()
            # check if taxes are all computed
            compute_taxes = account_invoice_tax.compute(inv.with_context(lang=inv.partner_id.lang))
            inv.check_tax_lines(compute_taxes)

            # I disabled the check_total feature
            if self.env.user.has_group('account.group_supplier_inv_check_total'):
                if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding / 2.0):
                    raise except_orm(_('Bad Total!'), _('Please verify the price of the invoice!\nThe encoded total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise except_orm(_('Error!'), _("Cannot create the invoice.\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount. In order to avoid rounding issues, the latest line of your payment term must be of type 'balance'."))

            # one move line per tax line
            iml += account_invoice_tax.move_line_get(inv.id)

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, ref, iml)

            name = inv.supplier_invoice_number or inv.name or '/'
            totlines = []
            if inv.payment_term:
                totlines = inv.with_context(ctx).payment_term.compute(total, date_invoice)[0]
            if totlines:
                res_amount_currency = total_currency
                ctx['date'] = date_invoice
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'ref': ref
                })
          
            if str(fyear_ids.days) == '0' and self.type in ['out_invoice', 'out_refund']:
               iml.append({
                    'type': 'discount',
                    'name':_('Discount'),
                    'price': (self.discounted_amount),
                    'account_id': self.env.user.company_id.discount_calculation_account_id.id,
                    'date_maturity': inv.date_due,
                    #'amount_currency': diff_currency and total_currency,
                    #'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id,
               })
            disc_value=[]
            if self.env.user.company_id.group_product_discount == True and self.type in ['out_invoice', 'out_refund']:
                for i in iml:                   
                    if i['price'] != -0.0 and i['type'] == 'src':
                        disc_value.append(i['price_unit']*i['quantity']+i['price'])           
                        i['price']=-(i['price_unit']*i['quantity'])      
                
                iml.append({
                    'type': 'discount',
                    'name':_('Trading Discount'),
                    'price': (sum(disc_value)),
                    'account_id': self.env.user.company_id.product_discount_account_id.id,
                    'date_maturity': inv.date_due,
                    #'amount_currency': diff_currency and total_currency,
                    #'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id,
                })
            pur_disc = []   
            if self.env.user.company_id.group_purchase_discount == True and self.type in ['in_invoice', 'in_refund']:
                for i in iml:                   
                    if i['price'] != -0.0 and i['type'] == 'src':
                        pur_disc.append(i['price_unit']*i['quantity']-i['price'])           
                        i['price']=self.currency_id.round(i['price_unit']*i['quantity'])      
                print'pur_discpur_discpur_disc',pur_disc
                iml.append({
                    'type': 'discount',
                    'name':_('Trading Discount'),
                    'price': -(self.currency_id.round(sum(pur_disc))),
                    'account_id': self.env.user.company_id.purchase_discount_account_id.id,
                    'date_maturity': inv.date_due,
                    #'amount_currency': diff_currency and total_currency,
                    #'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id,
                })                  
            date = date_invoice

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            for i in iml:
                print i 
            line = [(0, 0, self.line_get_convert(l, part.id, date)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise except_orm(_('User Error!'),
                        _('You cannot create an invoice on a centralized journal. Uncheck the centralized counterpart box in the related journal from the configuration menu.'))

            line = inv.finalize_invoice_move_lines(line)

            move_vals = {
                'ref': inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal.id,
                'date': inv.date_invoice,
                'narration': inv.comment,
                'company_id': inv.company_id.id,
            }
            ctx['company_id'] = inv.company_id.id
            period = inv.period_id
            if not period:
                period = period.with_context(ctx).find(date_invoice)[:1]
            if period:
                move_vals['period_id'] = period.id
                for i in line:
                    i[2]['period_id'] = period.id

            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)

            move = account_move.with_context(ctx_nolang).create(move_vals)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'period_id': period.id,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            valu=move.post()

        self._log_event()
        return True

