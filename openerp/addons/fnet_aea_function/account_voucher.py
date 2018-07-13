
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
from openerp import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
import openerp.addons.decimal_precision as dp
import time

from openerp.tools.translate import _

class account_journal_in(osv.osv):
    _inherit = 'account.journal'
    _columns = {
         'allow_dd_writing': fields.boolean('Allow DD writing', help='Check this if the journal is to be used for writing Demand Draft.'),
         'allow_neft_writing': fields.boolean('Allow Bank writing', help='Check this if the journal is to be used for writing Demand Draft.'),
         'allow_rd_writing': fields.boolean('Allow RD'),
         'reciept_journal': fields.boolean('Reciept journal'),
        }
account_journal_in()

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    _columns = {
        'payment_term': fields.many2one('account.payment.term', 'Payment Term'),
        'amount': fields.float('Total', digits_compute=dp.get_precision('Account'), required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'partner_id':fields.many2one('res.partner', 'Partner', change_default=1, readonly=True, states={'draft':[('readonly',False)]}),
        'journal_id':fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'account_cheque_line':fields.one2many('account.date.cheque', 'cheque_acc_id', 'Cheque Line'),
        'supplier_cheque_line':fields.one2many('supplier.date.cheque', 'cheque_acc_id', 'Cheque Line'),
        'dd_amount':fields.float('Enter Amount', readonly=True),
        'credit_note':fields.boolean('Credit Note'),
        }



    def _customer_check_writing(self, cr, uid, ids, chk_obj, chk_line_obj, obj, context=None):
        chk_sr = chk_obj.search(cr, uid, [('voucher_id', '=', obj.id)], context=context)
        if not chk_sr:
            vals = {
                   'voucher_id':obj.id,
                   'amount':obj.amount,
                   'partner_id':obj.partner_id.id,
                   'company_id':obj.company_id.id,
                   'cus_type':'customer',
                   'date':obj.date,
                   }
            chk = chk_obj.create(cr, uid, vals, context=context)
            for inv_line in obj.line_cr_ids:
                if inv_line.amount <> 0.00:
                    val = {
                          'cheque_details_id':chk,
                          'invoice_id':inv_line.move_line_id.invoice.id,
                          'journal_line_id':inv_line.move_line_id.id,
                          'original_amount':inv_line.amount_original,
                          'open_amount':inv_line.amount_unreconciled,
                          'amount':inv_line.amount
                          }
                    chk_line_obj.create(cr, uid, val, context=context)
            chk_sr = self.pool.get('account.date.cheque').search(cr, uid, [('cheque_acc_id', '=', obj.id), ('select', '=', True)], context=context)
            if chk_sr:
                if len(chk_sr) == 1:
                    date_chk = self.pool.get('account.date.cheque').browse(cr, uid, chk_sr[0])
                    chk_obj.write(cr, uid, chk, {'cheque_id':date_chk.cheque_id.id, 'type':date_chk.type}, context=context)
                else:
                    raise osv.except_osv(_('Error!'), _('Please Select any One Cheque!'))
            else:
                raise osv.except_osv(_('Error!'), _('There is no Cheque selected Please select atleast one Cheque!'))
        else:
            for line in obj.account_cheque_line:
                if line.select == True:
                    self.pool.get('post.date.cheque').write(cr, uid, line.cheque_id.id, {'state':'done', 'amount':obj.amount}, context=context)
        return True

    def _customer_dd_writing(self, cr, uid, ids, chk_obj, chk_line_obj, obj, context=None):
        chk_sr = chk_obj.search(cr, uid, [('voucher_id', '=', obj.id)], context=context)
        if not chk_sr:
            vals = {
                   'voucher_id':obj.id,
                   'amount':obj.amount,
                   'partner_id':obj.partner_id.id,
                   'company_id':obj.company_id.id,
                   'cus_type':'customer',
                   'date':obj.date,
                   }
            chk = chk_obj.create(cr, uid, vals, context=context)
            for inv_line in obj.line_cr_ids:
                if inv_line.amount <> 0.00:
                    val = {
                          'cheque_details_id':chk,
                          'invoice_id':inv_line.move_line_id.invoice.id,
                          'journal_line_id':inv_line.move_line_id.id,
                          'original_amount':inv_line.amount_original,
                          'open_amount':inv_line.amount_unreconciled,
                          'amount':inv_line.amount
                          }
                    chk_line_obj.create(cr, uid, val, context=context)
            chk_sr = self.pool.get('account.date.cheque').search(cr, uid, [('cheque_acc_id', '=', obj.id), ('select', '=', True)], context=context)
            if chk_sr:
                if len(chk_sr) == 1:
                    date_chk = self.pool.get('account.date.cheque').browse(cr, uid, chk_sr[0])
                    chk_obj.write(cr, uid, chk, {'cheque_id':date_chk.cheque_id.id, 'type':date_chk.type}, context=context)
                else:
                    raise osv.except_osv(_('Error!'), _('Please Select any One DD!'))
            else:
                raise osv.except_osv(_('Error!'), _('There is no DD selected Please select atleast one Cheque!'))
        return True

    def _customer_neft_writing(self, cr, uid, ids, chk_obj, chk_line_obj, obj, context=None):
        chk_sr = chk_obj.search(cr, uid, [('voucher_id', '=', obj.id)], context=context)
        if not chk_sr:
            vals = {
                   'voucher_id':obj.id,
                   'amount':obj.amount,
                   'partner_id':obj.partner_id.id,
                   'company_id':obj.company_id.id,
                   'cus_type':'customer',
                   'date':obj.date,
                   }
            chk = chk_obj.create(cr, uid, vals, context=context)
            for inv_line in obj.line_cr_ids:
                if inv_line.amount <> 0.00:
                    val = {
                          'cheque_details_id':chk,
                          'invoice_id':inv_line.move_line_id.invoice.id,
                          'journal_line_id':inv_line.move_line_id.id,
                          'original_amount':inv_line.amount_original,
                          'open_amount':inv_line.amount_unreconciled,
                          'amount':inv_line.amount
                          }
                    chk_line_obj.create(cr, uid, val, context=context)
            chk_sr = self.pool.get('account.date.cheque').search(cr, uid, [('cheque_acc_id', '=', obj.id), ('select', '=', True)], context=context)
            if chk_sr:
                if len(chk_sr) == 1:
                    date_chk = self.pool.get('account.date.cheque').browse(cr, uid, chk_sr[0])
                    chk_obj.write(cr, uid, chk, {'cheque_id':date_chk.cheque_id.id, 'type':date_chk.type}, context=context)
                else:
                    raise osv.except_osv(_('Error!'), _('Please Select any One NEFT Bank!'))
            else:
                raise osv.except_osv(_('Error!'), _('There is no NEFT selected Please select atleast one NEFT Bank!'))
        return True

    def _supplier_check_writing(self, cr, uid, ids, chk_obj, chk_line_obj, obj, context=None):
        chk_sr = chk_obj.search(cr, uid, [('voucher_id', '=', obj.id)], context=context)
        if not chk_sr:
            vals = {
                   'voucher_id':obj.id,
                   'amount':obj.amount,
                   'partner_id':obj.partner_id.id,
                   'company_id':obj.company_id.id,
                   'cus_type':'supplier',
                   'date':obj.date,
                   }
            chk = chk_obj.create(cr, uid, vals, context=context)
            for inv_line in obj.line_dr_ids:
                if inv_line.amount <> 0.00:
                    val = {
                          'cheque_details_id':chk,
                          'invoice_id':inv_line.move_line_id.invoice.id,
                          'journal_line_id':inv_line.move_line_id.id,
                          'original_amount':inv_line.amount_original,
                          'open_amount':inv_line.amount_unreconciled,
                          'amount':inv_line.amount
                          }
                    chk_line_obj.create(cr, uid, val, context=context)
            chk_sr = self.pool.get('supplier.date.cheque').search(cr, uid, [('cheque_acc_id', '=', obj.id), ('select', '=', True)], context=context)
            if chk_sr:
                if len(chk_sr) == 1:
                    sup_chk = self.pool.get('supplier.date.cheque').browse(cr, uid, chk_sr[0])
                    pdc_val = {
                        'cheque_id':obj.partner_id.id,
                        'type':sup_chk.type,
                        'name':sup_chk.cheque_no,
                        'issue_date':sup_chk.issue_date,
                        'bank_name':sup_chk.bank_name,
                        'branch_name':sup_chk.branch_name,
                        'amount':obj.amount,
                        #~ 'user_id':obj.user_id.id,
                        #~ 'company_id':obj.coompany_id.id,
                        'state':'open',
                        }
                    pdc = self.pool.get('post.date.cheque').create(cr, uid, pdc_val, context=context)
                    chk_obj.write(cr, uid, chk, {'cheque_id':pdc, 'type':sup_chk.type}, context=context)
                else:
                    raise osv.except_osv(_('Error!'), _('Please Select any One Cheque!'))
            else:
                raise osv.except_osv(_('Error!'), _('There is no Cheque selected Please select atleast one Cheque!'))
        return True

    def check_details_create(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        chk_obj = self.pool.get('cheque.details')
        chk_line_obj = self.pool.get('cheque.details.line')
        if obj.partner_id.customer == True:
            if obj.journal_id.allow_check_writing is True:
                self._customer_check_writing(cr, uid, ids, chk_obj, chk_line_obj, obj, context=context)
            if obj.journal_id.allow_dd_writing is True:
                self._customer_dd_writing(cr, uid, ids, chk_obj, chk_line_obj, obj, context=context)
            if obj.journal_id.allow_neft_writing is True:
                self._customer_neft_writing(cr, uid, ids, chk_obj, chk_line_obj, obj, context=context)
        if obj.partner_id.supplier == True:
            if obj.journal_id.allow_check_writing is True:
                self._supplier_check_writing(cr, uid, ids, chk_obj, chk_line_obj, obj, context=context)
        return True

    def proforma_voucher(self, cr, uid, ids, context=None):
        self.action_move_line_create(cr, uid, ids, context=context)
        self.check_details_create(cr, uid, ids, context=context)
        return True

    def cheque_line(self, cr, uid, ids, partner_id, journal_id, context=None):
        res = {}
        list_of_dict = []
        jr = []
        if journal_id:
            jr_obj = self.pool.get('account.journal').browse(cr, uid, journal_id)
            print jr_obj, "CCCCCCCCCCCC"
            if jr_obj.allow_check_writing:
                jr.append('cheque')
                jr.append('oo')
            elif jr_obj.allow_dd_writing:
                jr.append('dd')
                jr.append('oo')
            elif jr_obj.allow_neft_writing:
                jr.append('neft')
                jr.append('oo')
            else:
                jr.append('neft')
                jr.append('oo')
        if partner_id:
            if jr:
                cr.execute("""
                             select
                                   id as cheque_id,
                                   type as type,
                                   issue_date as issue_date,
                                   expiry_date as expiry_date,
                                   bank_name as bank_name,
                                   amount as amount,
                                   branch_name as branch_name
                             from post_date_cheque
                             where cheque_id = '%s' and state = 'open' and type in %s
                                      """ % (partner_id, tuple(jr)))
                line_list = [i for i in cr.dictfetchall()]
                if line_list:
                    for fid in line_list:
                        list_of_dict.append({"cheque_id":fid['cheque_id'],
                                                "type":fid['type'],
                                                "issue_date":fid['issue_date'],
                                                "expiry_date":fid['expiry_date'],
                                                "bank_name":fid['bank_name'],
                                                "amount":fid['amount'],
                                                "branch_name":fid['branch_name']})
                        res['value'] = {'account_cheque_line':list_of_dict,}
                else:
                    res['value'] = {'account_cheque_line':[],}
        return res

    def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, payment_term, context=None):
        if not journal_id:
            return {}
        if context is None:
            context = {}
        #TODO: comment me and use me directly in the sales/purchases views
        res = self.basic_onchange_partner(cr, uid, ids, partner_id, journal_id, ttype, context=context)
        if ttype in ['sale', 'purchase']:
            return res
        ctx = context.copy()
        # not passing the payment_rate currency and the payment_rate in the context but it's ok because they are reset in recompute_payment_rate
        ctx.update({'date': date})
        vals = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, payment_term, context=ctx)
        vals2 = self.recompute_payment_rate(cr, uid, ids, vals, currency_id, date, ttype, journal_id, amount, context=context)
        vals3 = self.cheque_line(cr, uid, ids, partner_id, journal_id, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals2.keys():
            res[key].update(vals2[key])
        for key in vals3.keys():
            res[key].update(vals3[key])
        #TODO: can probably be removed now
        #TODO: onchange_partner_id() should not returns [pre_line, line_dr_ids, payment_rate...] for type sale, and not
        # [pre_line, line_cr_ids, payment_rate...] for type purchase.
        # We should definitively split account.voucher object in two and make distinct on_change functions. In the
        # meanwhile, bellow lines must be there because the fields aren't present in the view, what crashes if the
        # onchange returns a value for them
        if ttype == 'sale':
            del(res['value']['line_dr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
            del(res['value']['account_cheque_line'])
        elif ttype == 'purchase':
            del(res['value']['line_cr_ids'])
            del(res['value']['pre_line'])
            del(res['value']['payment_rate'])
            del(res['value']['account_cheque_line'])
        return res

    def _get_date_planned(self, cr, uid, ids, pay_days, context=None):
        start_date = time.strftime("%Y-%m-%d %H:%M:%S")
        date_planned = datetime.strptime(start_date, DEFAULT_SERVER_DATETIME_FORMAT) - timedelta(days=pay_days or 0.0)
        return date_planned


    def onchange_journal(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, payment_term, context=None):
        if context is None:
            context = {}
        if not journal_id:
            return False
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        if ttype in ('sale', 'receipt'):
            account_id = journal.default_debit_account_id
        elif ttype in ('purchase', 'payment'):
            account_id = journal.default_credit_account_id
        else:
            account_id = journal.default_credit_account_id or journal.default_debit_account_id
        tax_id = False
        if account_id and account_id.tax_ids:
            tax_id = account_id.tax_ids[0].id
        vals = {'value':{} }
        if ttype in ('sale', 'purchase'):
            vals = self.onchange_price(cr, uid, ids, line_ids, tax_id, partner_id, context)
            vals['value'].update({'tax_id':tax_id,'amount': amount})
        currency_id = False
        credit_note=False
        if journal.currency:
            currency_id = journal.currency.id
        else:
            currency_id = journal.company_id.currency_id.id
        if journal.code =='CN':
            credit_note=True
        period_ids = self.pool['account.period'].find(cr, uid, dt=date, context=dict(context, company_id=company_id))
        vals['value'].update({
            'credit_note': credit_note,
            'currency_id': currency_id,
            'payment_rate_currency_id': currency_id,
            'account_id': account_id.id,
            'period_id': period_ids and period_ids[0] or False
        })
        #in case we want to register the payment directly from an invoice, it's confusing to allow to switch the journal
        #without seeing that the amount is expressed in the journal currency, and not in the invoice currency. So to avoid
        #this common mistake, we simply reset the amount to 0 if the currency is not the invoice currency.
        if context.get('payment_expected_currency') and currency_id != context.get('payment_expected_currency'):
            vals['value']['amount'] = 0
            amount = 0
        if partner_id:
            res = self.onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, payment_term, context)
            for key in res.keys():
                vals[key].update(res[key])
        return vals

    def _due_payment_remove(self, cr, uid, ids, payment_term, account_move_lines, context=None):
        values = []
        payment_days = self.pool.get('account.payment.term.line').browse(cr, uid, payment_term)
        pay_date = self._get_date_planned(cr, uid, ids, payment_days.days, context=context)
        pay = pay_date.strftime('%Y-%m-%d')
        current_date = time.strftime("%Y-%m-%d")
        print pay_date, "PAY DATE"
        print pay, "PPPPAAAYYYY"
        print current_date, "MMMMMMMMMMMM"
        for value in account_move_lines:
            #~ if not value.date_maturity >= pay and value.date_maturity <= current_date:
            if not pay <= value.date_maturity and current_date >= value.date_maturity:
                values.append(value)
            else:
                if pay == current_date:
                    values.append(value)
        return values

    def onchange_amount(self, cr, uid, ids, amount, rate, partner_id, journal_id, currency_id, ttype, date, payment_rate_currency_id, company_id, payment_term, context=None):
        if context is None:
            context = {}
        ctx = context.copy()
        ctx.update({'date': date})
        #read the voucher rate with the right date in the context
        currency_id = currency_id or self.pool.get('res.company').browse(cr, uid, company_id, context=ctx).currency_id.id
        voucher_rate = self.pool.get('res.currency').read(cr, uid, [currency_id], ['rate'], context=ctx)[0]['rate']
        ctx.update({
            'voucher_special_currency': payment_rate_currency_id,
            'voucher_special_currency_rate': rate * voucher_rate})
        res = self.recompute_voucher_lines(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, payment_term, context=ctx)
        vals = self.onchange_rate(cr, uid, ids, rate, amount, currency_id, payment_rate_currency_id, company_id, context=ctx)
        vals3 = self.cheque_line(cr, uid, ids, partner_id, journal_id, context=context)
        for key in vals.keys():
            res[key].update(vals[key])
        for key in vals3.keys():
            res[key].update(vals3[key])
        return res

    def onchange_payment_term(self, cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, payment_term, context=None):
        if payment_term:
            res = self.onchange_journal(cr, uid, ids, journal_id, line_ids, tax_id, partner_id, date, amount, ttype, company_id, payment_term, context=context)
            return res

    def recompute_voucher_lines(self, cr, uid, ids, partner_id, journal_id, price, currency_id, ttype, date, payment_term, context=None):
        """
        Returns a dict that contains new values and context

        @param partner_id: latest value from user input for field partner_id
        @param args: other arguments
        @param context: context arguments, like lang, time zone

        @return: Returns a dict which contains new values, and context
        """
        def _remove_noise_in_o2m():
            """if the line is partially reconciled, then we must pay attention to display it only once and
                in the good o2m.
                This function returns True if the line is considered as noise and should not be displayed
            """
            if line.reconcile_partial_id:
                if currency_id == line.currency_id.id:
                    if line.amount_residual_currency <= 0:
                        return True
                else:
                    if line.amount_residual <= 0:
                        return True
            return False

        if context is None:
            context = {}
        context_multi_currency = context.copy()

        currency_pool = self.pool.get('res.currency')
        move_line_pool = self.pool.get('account.move.line')
        partner_pool = self.pool.get('res.partner')
        journal_pool = self.pool.get('account.journal')
        line_pool = self.pool.get('account.voucher.line')

        #set default values
        default = {
            'value': {'line_dr_ids': [], 'line_cr_ids': [], 'pre_line': False},
        }

        # drop existing lines
        line_ids = ids and line_pool.search(cr, uid, [('voucher_id', '=', ids[0])])
        for line in line_pool.browse(cr, uid, line_ids, context=context):
            if line.type == 'cr':
                default['value']['line_cr_ids'].append((2, line.id))
            else:
                default['value']['line_dr_ids'].append((2, line.id))

        if not partner_id or not journal_id:
            return default

        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        partner = partner_pool.browse(cr, uid, partner_id, context=context)
        currency_id = currency_id or journal.company_id.currency_id.id

        total_credit = 0.0
        total_debit = 0.0
        account_type = None
        if context.get('account_id'):
            account_type = self.pool['account.account'].browse(cr, uid, context['account_id'], context=context).type
        if ttype == 'payment':
            if not account_type:
                account_type = 'payable'
            total_debit = price or 0.0
        else:
            total_credit = price or 0.0
            if not account_type:
                account_type = 'receivable'

        if not context.get('move_line_ids', False):
            ids = move_line_pool.search(cr, uid, [('state','=','valid'), ('account_id.type', '=', account_type), ('reconcile_id', '=', False), ('partner_id', '=', partner_id)], context=context)
        else:
            ids = context['move_line_ids']
        invoice_id = context.get('invoice_id', False)
        company_currency = journal.company_id.currency_id.id
        move_lines_found = []

        #order the lines by most old first
        ids.reverse()
        account_move_lines = move_line_pool.browse(cr, uid, ids, context=context)

        #compute the total debit/credit and look for a matching open amount or invoice
        for line in account_move_lines:
            if _remove_noise_in_o2m():
                continue

            if invoice_id:
                if line.invoice.id == invoice_id:
                    #if the invoice linked to the voucher line is equal to the invoice_id in context
                    #then we assign the amount on that line, whatever the other voucher lines
                    move_lines_found.append(line.id)
            elif currency_id == company_currency:
                #otherwise treatments is the same but with other field names
                if line.amount_residual == price:
                    #if the amount residual is equal the amount voucher, we assign it to that voucher
                    #line, whatever the other voucher lines
                    move_lines_found.append(line.id)
                    break
                #otherwise we will split the voucher amount on each line (by most old first)
                total_credit += line.credit or 0.0
                total_debit += line.debit or 0.0
            elif currency_id == line.currency_id.id:
                if line.amount_residual_currency == price:
                    move_lines_found.append(line.id)
                    break
                total_credit += line.credit and line.amount_currency or 0.0
                total_debit += line.debit and line.amount_currency or 0.0

        remaining_amount = price
        #voucher line creation
        if payment_term:
            due_rem = self._due_payment_remove(cr, uid, ids, payment_term, account_move_lines, context=context)
            del(account_move_lines)
            account_move_lines = due_rem
        for line in account_move_lines:

            if _remove_noise_in_o2m():
                continue

            if line.currency_id and currency_id == line.currency_id.id:
                amount_original = abs(line.amount_currency)
                amount_unreconciled = abs(line.amount_residual_currency)
            else:
                #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                amount_original = currency_pool.compute(cr, uid, company_currency, currency_id, line.credit or line.debit or 0.0, context=context_multi_currency)
                amount_unreconciled = currency_pool.compute(cr, uid, company_currency, currency_id, abs(line.amount_residual), context=context_multi_currency)
            line_currency_id = line.currency_id and line.currency_id.id or company_currency
            rs = {
                'name':line.move_id.name,
                'type': line.credit and 'dr' or 'cr',
                'move_line_id':line.id,
                'account_id':line.account_id.id,
                'amount_original': amount_original,
                'amount': (line.id in move_lines_found) and min(abs(remaining_amount), amount_unreconciled) or 0.0,
                'date_original':line.date,
                'date_due':line.date_maturity,
                'amount_unreconciled': amount_unreconciled,
                'currency_id': line_currency_id,
            }
            remaining_amount -= rs['amount']
            #in case a corresponding move_line hasn't been found, we now try to assign the voucher amount
            #on existing invoices: we split voucher amount by most old first, but only for lines in the same currency
            if not move_lines_found:
                if currency_id == line_currency_id:
                    if line.credit:
                        amount = min(amount_unreconciled, abs(total_debit))
                        rs['amount'] = amount
                        total_debit -= amount
                    else:
                        amount = min(amount_unreconciled, abs(total_credit))
                        rs['amount'] = amount
                        total_credit -= amount

            if rs['amount_unreconciled'] == rs['amount']:
                rs['reconcile'] = True

            if rs['type'] == 'cr':
                default['value']['line_cr_ids'].append(rs)
            else:
                default['value']['line_dr_ids'].append(rs)

            if len(default['value']['line_cr_ids']) > 0:
                default['value']['pre_line'] = 1
            elif len(default['value']['line_dr_ids']) > 0:
                default['value']['pre_line'] = 1
            default['value']['writeoff_amount'] = self._compute_writeoff_amount(cr, uid, default['value']['line_dr_ids'], default['value']['line_cr_ids'], price, ttype)
        return default

account_voucher()

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'

    def _compute_balance(self, cr, uid, ids, name, args, context=None):
        currency_pool = self.pool.get('res.currency')
        rs_data = {}
        for line in self.browse(cr, uid, ids, context=context):
            ctx = context.copy()
            ctx.update({'date': line.voucher_id.date})
            voucher_rate = self.pool.get('res.currency').read(cr, uid, line.voucher_id.currency_id.id, ['rate'], context=ctx)['rate']
            ctx.update({
                'voucher_special_currency': line.voucher_id.payment_rate_currency_id and line.voucher_id.payment_rate_currency_id.id or False,
                'voucher_special_currency_rate': line.voucher_id.payment_rate * voucher_rate})
            res = {}
            company_currency = line.voucher_id.journal_id.company_id.currency_id.id
            voucher_currency = line.voucher_id.currency_id and line.voucher_id.currency_id.id or company_currency
            move_line = line.move_line_id or False

            if not move_line:
                res['amount_original'] = 0.0
                res['amount_unreconciled'] = 0.0
            elif move_line.currency_id and voucher_currency==move_line.currency_id.id:
                res['amount_original'] = abs(move_line.amount_currency)
                res['amount_unreconciled'] = abs(move_line.amount_residual_currency)
            else:
                #~ #always use the amount booked in the company currency as the basis of the conversion into the voucher currency
                res['amount_original'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, move_line.credit or move_line.debit or 0.0, context=ctx)
                res['amount_unreconciled'] = currency_pool.compute(cr, uid, company_currency, voucher_currency, abs(move_line.amount_residual), context=ctx)

            rs_data[line.id] = res
        return rs_data

    _columns = {

       'amount_unreconciled': fields.function(_compute_balance, multi='dc', type='float', string='Open Balance', store=True, digits_compute=dp.get_precision('Account')),

      }
account_voucher_line()

class account_cheque_line(osv.osv):
    _name = 'account.date.cheque'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'cheque_acc_id': fields.many2one('account.voucher', 'Cheque Line'),
        'type': fields.selection([('cheque', 'Cheque'),('dd', 'Demand Draft'),('neft', 'NEFT')],'Type', required=True),
        'select': fields.boolean('Select'),
        'credit_note': fields.boolean('Credit Note'),
        'cheque_id':fields.many2one('post.date.cheque', 'Cheque/DD No', required=True),
        'issue_date':fields.date('Issue Date'),
        'bank_name':fields.char('Bank Name', size=50),
        'amount':fields.float('Amount'),
        'branch_name':fields.char('Branch Name', size=50),
        'company_id': fields.many2one('res.company', 'Company'),
        }
    
    def _get_credit_note(self,cr,uid,context):
        if context.get('credit_note',False):
            return context['credit_note']
        else:
            return 0.0
            
    _defaults = {
        'company_id': _get_default_company,
        'credit_note':_get_credit_note,
        }

    def onchange_cheque_id(self, cr, uid, ids, cheque_id, context=None):
        result = {}
        if cheque_id:
            chk_obj = self.pool.get('post.date.cheque').browse(cr, uid, cheque_id)
            result['value'] = {
                    'type':chk_obj.type,
                    'issue_date':chk_obj.issue_date,
                    'bank_name':chk_obj.bank_name,
                    'branch_name':chk_obj.branch_name,
                    'company_id':chk_obj.company_id,
                    'amount':chk_obj.amount,
                    }
        return result
account_cheque_line()

class supplier_cheque_line(osv.osv):
    _name = 'supplier.date.cheque'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
        'cheque_acc_id': fields.many2one('account.voucher', 'Cheque Line'),
        'type': fields.selection([('cheque', 'Cheque'),('dd', 'Demand Draft'),('neft', 'NEFT')],'Type', required=True),
        'select': fields.boolean('Select'),
        'cheque_no':fields.char('Cheque/DD No', required=True),
        'issue_date':fields.date('Issue Date'),
        'bank_name':fields.char('Bank Name', size=50),
        'branch_name':fields.char('Branch Name', size=50),
        'company_id': fields.many2one('res.company', 'Company'),
        }

    _defaults = {
        'company_id': _get_default_company,
        'type': 'cheque',
        'select': True,
        'issue_date': time.strftime("%Y-%m-%d"),


        }
supplier_cheque_line()
