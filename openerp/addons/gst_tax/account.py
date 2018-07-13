# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
import time

import openerp
from openerp import SUPERUSER_ID, api
from openerp import tools
from openerp.osv import fields, osv, expression
from openerp.tools.translate import _
from openerp.tools.float_utils import float_round as round
from openerp.tools.safe_eval import safe_eval as eval

import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class account_account_template(osv.osv):
    _inherit = "account.account.template"
    def generate_account(self, cr, uid, chart_template_id, tax_template_ref, acc_template_ref, code_digits, company_id, context=None):

        """
        This method for generating accounts from templates.

        :param chart_template_id: id of the chart template chosen in the wizard
        :param tax_template_ref: Taxes templates reference for write taxes_id in account_account.
        :paramacc_template_ref: dictionary with the mappping between the account templates and the real accounts.
        :param code_digits: number of digits got from wizard.multi.charts.accounts, this is use for account code.
        :param company_id: company_id selected from wizard.multi.charts.accounts.
        :returns: return acc_template_ref for reference purpose.
        :rtype: dict
        """
        if context is None:
            context = {}
        obj_acc = self.pool.get('account.account')
        cr.execute("select distinct id from res_company")
        com_id=cr.dictfetchall()
        print'com_id',com_id
        for i in com_id:
            company_name = self.pool.get('res.company').browse(cr, uid, i['id'], context=context).name
            template = self.pool.get('account.chart.template').browse(cr, uid, chart_template_id, context=context)
            #deactivate the parent_store functionnality on account_account for rapidity purpose
            ctx = context.copy()
            ctx.update({'defer_parent_store_computation': True})
            level_ref = {}
            children_acc_criteria = [('chart_template_id','=', chart_template_id)]
            if template.account_root_id.id:
                children_acc_criteria = ['|'] + children_acc_criteria + ['&',('parent_id','child_of', [template.account_root_id.id]),('chart_template_id','=', False)]
            children_acc_template = self.search(cr, uid, [('nocreate','!=',True)] + children_acc_criteria, order='id', context=context)
            for account_template in self.browse(cr, uid, children_acc_template, context=context):
                cr.execute("""select code from account_account_template where id=%d"""%(account_template.id))
                codes=cr.dictfetchone()

                # skip the root of COA if it's not the main one
                
                if (template.account_root_id.id == account_template.id) and template.parent_id:
                    continue
                tax_ids = []
                for tax in account_template.tax_ids:
                    tax_ids.append(tax_template_ref[tax.id])

                code_main = account_template.code and len(account_template.code) or 0
                code_acc = account_template.code or ''
                if code_main > 0 and code_main <= code_digits and account_template.type != 'view':
                    code_acc = str(code_acc) + (str('0'*(code_digits-code_main)))
                parent_id = account_template.parent_id and ((account_template.parent_id.id in acc_template_ref) and acc_template_ref[account_template.parent_id.id]) or False
                #the level as to be given as well at the creation time, because of the defer_parent_store_computation in
                #context. Indeed because of this, the parent_left and parent_right are not computed and thus the child_of
                #operator does not return the expected values, with result of having the level field not computed at all.
                cr.execute("""select code from account_account where code = '%s' and company_id=%d """%(code_acc,i['id']))
                my=cr.dictfetchone()
                if my == None:
                    if parent_id:
                        level = parent_id in level_ref and level_ref[parent_id] + 1 or obj_acc._get_level(cr, uid, [parent_id], 'level', None, context=context)[parent_id] + 1
                    else:
                        level = 0
                    vals={
                        'name': (template.account_root_id.id == account_template.id) and company_name or account_template.name,
                        'currency_id': account_template.currency_id and account_template.currency_id.id or False,
                        'code': code_acc,
                        'type': account_template.type,
                        'user_type': account_template.user_type and account_template.user_type.id or False,
                        'reconcile': account_template.reconcile,
                        'shortcut': account_template.shortcut,
                        'note': account_template.note,
                        'financial_report_ids': account_template.financial_report_ids and [(6,0,[x.id for x in account_template.financial_report_ids])] or False,
                        'parent_id': parent_id,
                        'tax_ids': [(6,0,tax_ids)],
                        'company_id': i['id'],
                        'level': level,
                    }
                   
                    new_account = obj_acc.create(cr, uid, vals, context=ctx)
                    acc_template_ref[account_template.id] = new_account
                    level_ref[new_account] = level

        #reactivate the parent_store functionnality on account_account
        obj_acc._parent_store_compute(cr)
        return acc_template_ref

class account_tax_code_template(osv.osv):

    _inherit = 'account.tax.code.template'
    
    def generate_tax_code(self, cr, uid, tax_code_root_id, company_id, context=None):
        print'tax_code_root_id%%%%%%%%%%%%%%%%%%%%%%%%%%%',tax_code_root_id
        print'company_id%%%%%%%%%%%%%%%%%%%%%%%%%%%',company_id
        '''
        This function generates the tax codes from the templates of tax code that are children of the given one passed
        in argument. Then it returns a dictionary with the mappping between the templates and the real objects.

        :param tax_code_root_id: id of the root of all the tax code templates to process
        :param company_id: id of the company the wizard is running for
        :returns: dictionary with the mappping between the templates and the real objects.
        :rtype: dict
        '''
        obj_tax_code_template = self.pool.get('account.tax.code.template')
        obj_tax_code = self.pool.get('account.tax.code')
        tax_code_template_ref = {}
        cr.execute("select distinct id from res_company")
        com_id=cr.dictfetchall()
        print'com_id',com_id
        for i in com_id:        
            company = self.pool.get('res.company').browse(cr, uid, i['id'], context=context)

            #find all the children of the tax_code_root_id
            children_tax_code_template = tax_code_root_id and obj_tax_code_template.search(cr, uid, [('parent_id','child_of',[tax_code_root_id])], order='id') or []
            for tax_code_template in obj_tax_code_template.browse(cr, uid, children_tax_code_template, context=context):
                vals = {
                    'name': (tax_code_root_id == tax_code_template.id) and company.name or tax_code_template.name,
                    'code': tax_code_template.code,
                    'info': tax_code_template.info,
                    'parent_id': tax_code_template.parent_id and ((tax_code_template.parent_id.id in tax_code_template_ref) and tax_code_template_ref[tax_code_template.parent_id.id]) or False,
                    'company_id': i['id'],
                    'sign': tax_code_template.sign,
                    'sequence': tax_code_template.sequence,
                }
                #check if this tax code already exists
                rec_list = obj_tax_code.search(cr, uid, [('name', '=', vals['name']),('code', '=', vals['code']),('company_id', '=', vals['company_id'])], context=context)
                if not rec_list:
                    #if not yet, create it
                    new_tax_code = obj_tax_code.create(cr, uid, vals)
                    #recording the new tax code to do the mapping
                    tax_code_template_ref[tax_code_template.id] = new_tax_code
            return tax_code_template_ref

class account_tax_template(osv.osv):

    _inherit = 'account.tax.template'
    def _generate_tax(self, cr, uid, tax_templates, tax_code_template_ref, company_id, context=None):
        print'tax_templates*************************************8',tax_templates
        print'tax_code_template_ref',tax_code_template_ref
        print'Company_id',company_id
        """
        This method generate taxes from templates.

        :param tax_templates: list of browse record of the tax templates to process
        :param tax_code_template_ref: Taxcode templates reference.
        :param company_id: id of the company the wizard is running for
        :returns:
            {
            'tax_template_to_tax': mapping between tax template and the newly generated taxes corresponding,
            'account_dict': dictionary containing a to-do list with all the accounts to assign on new taxes
            }
        """
        if context is None:
            context = {}
        res = {}
        todo_dict = {}
        tax_template_to_tax = {}
        cr.execute("select distinct id from res_company")
        com_id=cr.dictfetchall()
        print'com_id',com_id
        for i in com_id:           
            for tax in tax_templates:
                print'taxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',tax.id
                cr.execute("""select name from account_tax_template where id = %d """%(tax.id))
                there=cr.dictfetchone()
                print'thereeeeeeeeeeeeeeeeee',there
                cr.execute("""select id from account_tax where name = '%s' and company_id=%d"""%(there['name'],i['id']))
                theres=cr.dictfetchone()
                print'QQQQQQQQQQQQQQQQQ',theres
                if theres == None:
                    vals_tax = {
                        'name':tax.name,
                        'sequence': tax.sequence,
                        'amount': tax.amount,
                        'type': tax.type,
                        'applicable_type': tax.applicable_type,
                        'domain': tax.domain,
                        'parent_id': tax.parent_id and ((tax.parent_id.id in tax_template_to_tax) and tax_template_to_tax[tax.parent_id.id]) or False,
                        'child_depend': tax.child_depend,
                        'python_compute': tax.python_compute,
                        'python_compute_inv': tax.python_compute_inv,
                        'python_applicable': tax.python_applicable,
                        'base_code_id': tax.base_code_id and ((tax.base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.base_code_id.id]) or False,
                        'tax_code_id': tax.tax_code_id and ((tax.tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.tax_code_id.id]) or False,
                        'base_sign': tax.base_sign,
                        'tax_sign': tax.tax_sign,
                        'ref_base_code_id': tax.ref_base_code_id and ((tax.ref_base_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_base_code_id.id]) or False,
                        'ref_tax_code_id': tax.ref_tax_code_id and ((tax.ref_tax_code_id.id in tax_code_template_ref) and tax_code_template_ref[tax.ref_tax_code_id.id]) or False,
                        'ref_base_sign': tax.ref_base_sign,
                        'ref_tax_sign': tax.ref_tax_sign,
                        'include_base_amount': tax.include_base_amount,
                        'description': tax.description,
                        'company_id': i['id'],
                        'type_tax_use': tax.type_tax_use,
                        'price_include': tax.price_include
                    }
                    new_tax = self.pool.get('account.tax').create(cr, uid, vals_tax)
                    print'newwwwwwwwwwwwwwwwwwwwwww',new_tax
                    tax_template_to_tax[tax.id] = new_tax
                    #as the accounts have not been created yet, we have to wait before filling these fields
                    todo_dict[new_tax] = {
                        'account_collected_id': tax.account_collected_id and tax.account_collected_id.id or False,
                        'account_paid_id': tax.account_paid_id and tax.account_paid_id.id or False,
                    }
        res.update({'tax_template_to_tax': tax_template_to_tax, 'account_dict': todo_dict})
        return res    

class wizard_multi_charts_accounts(osv.osv_memory):
    _inherit='wizard.multi.charts.accounts' 
    def generate_properties(self, cr, uid, chart_template_id, acc_template_ref, company_id, context=None):
        print'chart_template_id&&&&&&&&&&&&&&&&&&&&&&&&&&&&',chart_template_id
        print'acc_template_ref&&&&&&&&&&&&&&&&&&&&&&&&&&&&',acc_template_ref
        print'company_id&&&&&&&&&&&&&&&&&&&&&&&&&&&&',company_id
        """
        This method used for creating properties.

        :param chart_template_id: id of the current chart template for which we need to create properties
        :param acc_template_ref: Mapping between ids of account templates and real accounts created from them
        :param company_id: company_id selected from wizard.multi.charts.accounts.
        :returns: True
        """
        property_obj = self.pool.get('ir.property')
        field_obj = self.pool.get('ir.model.fields')
        todo_list = [
            ('property_account_receivable','res.partner','account.account'),
            ('property_account_payable','res.partner','account.account'),
            ('property_account_expense_categ','product.category','account.account'),
            ('property_account_income_categ','product.category','account.account'),
            ('property_account_expense','product.template','account.account'),
            ('property_account_income','product.template','account.account'),
        ]
        template = self.pool.get('account.chart.template').browse(cr, uid, chart_template_id, context=context)
        print'template@@@@@@@@@@@@@@@@@',template
        cr.execute("select distinct id from res_company")
        com_id=cr.dictfetchall()
        print'com_id',com_id
        for i in com_id:           
            for record in todo_list:
                print'record',record
                account = getattr(template, record[0])
                print'accountsssssssssssssssssssss',account
                if acc_template_ref.has_key(account.id):
                    value = account and 'account.account,' + str(acc_template_ref[account.id]) or False
                    print'valueeeeeeeeeeeeeeeeeee',value
                    if value:
                        field = field_obj.search(cr, uid, [('name', '=', record[0]),('model', '=', record[1]),('relation', '=', record[2])], context=context)
                        vals = {
                            'name': record[0],
                            'company_id': i['id'],
                            'fields_id': field[0],
                            'value': value,
                        }
                        property_ids = property_obj.search(cr, uid, [('name','=', record[0]),('company_id', '=', i['id'])], context=context)
                        if property_ids:
                            #the property exist: modify it
                            property_obj.write(cr, uid, property_ids, vals, context=context)
                        else:
                            #create the property
                            property_obj.create(cr, uid, vals, context=context)
            return True
    def execute(self, cr, uid, ids, context=None):
        '''
        This function is called at the confirmation of the wizard to generate the COA from the templates. It will read
        all the provided information to create the accounts, the banks, the journals, the taxes, the tax codes, the
        accounting properties... accordingly for the chosen company.
        '''
        if uid != SUPERUSER_ID and not self.pool['res.users'].has_group(cr, uid, 'base.group_erp_manager'):
            raise openerp.exceptions.AccessError(_("Only administrators can change the settings"))
        obj_data = self.pool.get('ir.model.data')
        ir_values_obj = self.pool.get('ir.values')
        obj_wizard = self.browse(cr, uid, ids[0])
        company_id = obj_wizard.company_id.id

        self.pool.get('res.company').write(cr, uid, [company_id], {'currency_id': obj_wizard.currency_id.id})

        # When we install the CoA of first company, set the currency to price types and pricelists
        if company_id==1:
            for ref in (('product','list_price'),('product','standard_price'),('product','list0'),('purchase','list0')):
                try:
                    tmp2 = obj_data.get_object_reference(cr, uid, *ref)
                    if tmp2: 
                        self.pool[tmp2[0]].write(cr, uid, tmp2[1], {
                            'currency_id': obj_wizard.currency_id.id
                        })
                except ValueError:
                    pass

        # If the floats for sale/purchase rates have been filled, create templates from them
        cr.execute("select distinct id from res_company")
        com_id=cr.dictfetchall()
        print'com_id',com_id
        for i in com_id:           
            self._create_tax_templates_from_rates(cr, uid, obj_wizard, i['id'], context=context)

            # Install all the templates objects and generate the real objects
            acc_template_ref, taxes_ref, tax_code_ref = self._install_template(cr, uid, obj_wizard.chart_template_id.id, i['id'], code_digits=obj_wizard.code_digits, obj_wizard=obj_wizard, context=context)

            # write values of default taxes for product as super user
            print'taxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',taxes_ref
            if obj_wizard.sale_tax and taxes_ref:
                if taxes_ref.has_key(obj_wizard.sale_tax.id):
                    ir_values_obj.set_default(cr, SUPERUSER_ID, 'product.template', "taxes_id", [taxes_ref[obj_wizard.sale_tax.id]], for_all_users=True, company_id=i['id'])
            if obj_wizard.purchase_tax and taxes_ref:
                if taxes_ref.has_key(obj_wizard.purchase_tax.id):
                    ir_values_obj.set_default(cr, SUPERUSER_ID, 'product.template', "supplier_taxes_id", [taxes_ref[obj_wizard.purchase_tax.id]], for_all_users=True, company_id=i['id'])

            # Create Bank journals
            self._create_bank_journals_from_o2m(cr, uid, obj_wizard, i['id'], acc_template_ref, context=context)
        return {}
    def _prepare_bank_account(self, cr, uid, line, new_code, acc_template_ref, ref_acc_bank, company_id, context=None):
        '''
        This function prepares the value to use for the creation of the default debit and credit accounts of a
        bank journal created through the wizard of generating COA from templates.

        :param line: dictionary containing the values encoded by the user related to his bank account
        :param new_code: integer corresponding to the next available number to use as account code
        :param acc_template_ref: the dictionary containing the mapping between the ids of account templates and the ids
            of the accounts that have been generated from them.
        :param ref_acc_bank: browse record of the account template set as root of all bank accounts for the chosen
            template
        :param company_id: id of the company for which the wizard is running
        :return: mapping of field names and values
        :rtype: dict
        '''
        obj_data = self.pool.get('ir.model.data')

        # Get the id of the user types fr-or cash and bank
        tmp = obj_data.get_object_reference(cr, uid, 'account', 'data_account_type_cash')
        cash_type = tmp and tmp[1] or False
        tmp = obj_data.get_object_reference(cr, uid, 'account', 'data_account_type_bank')
        bank_type = tmp and tmp[1] or False
        cr.execute("select distinct id from res_company")
        com_id=cr.dictfetchall()
        print'com_id',com_id
        for i in com_id:         
			if acc_template_ref.has_key(ref_acc_bank.id):
				return {
						'name': line['acc_name'],
						'currency_id': line['currency_id'],
						'code': new_code,
						'type': 'liquidity',
						'user_type': line['account_type'] == 'cash' and cash_type or bank_type,
						'parent_id': acc_template_ref[ref_acc_bank.id] or False,
						'company_id': i['id'],
				}        
    def _create_bank_journals_from_o2m(self, cr, uid, obj_wizard, company_id, acc_template_ref, context=None):
        '''
        This function creates bank journals and its accounts for each line encoded in the field bank_accounts_id of the
        wizard.

        :param obj_wizard: the current wizard that generates the COA from the templates.
        :param company_id: the id of the company for which the wizard is running.
        :param acc_template_ref: the dictionary containing the mapping between the ids of account templates and the ids
            of the accounts that have been generated from them.
        :return: True
        '''
        print'obj_wizard###################################',obj_wizard
        print'company_id###################################',company_id
        print'acc_template_ref###################################',acc_template_ref
        obj_acc = self.pool.get('account.account')
        obj_journal = self.pool.get('account.journal')
        code_digits = obj_wizard.code_digits

        # Build a list with all the data to process
        journal_data = []
        if obj_wizard.bank_accounts_id:
            for acc in obj_wizard.bank_accounts_id:
                vals = {
                    'acc_name': acc.acc_name,
                    'account_type': acc.account_type,
                    'currency_id': acc.currency_id.id,
                }
                journal_data.append(vals)
        ref_acc_bank = obj_wizard.chart_template_id.bank_account_view_id
        if journal_data and not ref_acc_bank.code:
            raise osv.except_osv(_('Configuration Error!'), _('You have to set a code for the bank account defined on the selected chart of accounts.'))

        current_num = 1
        cr.execute("select distinct id from res_company")
        com_id=cr.dictfetchall()
        print'com_id',com_id
        for i in com_id:         
			for line in journal_data:
				# Seek the next available number for the account code
				while True:
					new_code = str(ref_acc_bank.code.ljust(code_digits-len(str(current_num)), '0')) + str(current_num)
					ids = obj_acc.search(cr, uid, [('code', '=', new_code), ('company_id', '=', i['id'])])
					if not ids:
						break
					else:
						current_num += 1
				# Create the default debit/credit accounts for this bank journal
				vals = self._prepare_bank_account(cr, uid, line, new_code, acc_template_ref, ref_acc_bank, i['id'], context=context)
				print'valsssss!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',vals
				if  vals != None:
					default_account_id  = obj_acc.create(cr, uid, vals, context=context)

				#create the bank journal
					vals_journal = self._prepare_bank_journal(cr, uid, line, current_num, default_account_id, i['id'], context=context)
					obj_journal.create(cr, uid, vals_journal)
					current_num += 1
			return True        
