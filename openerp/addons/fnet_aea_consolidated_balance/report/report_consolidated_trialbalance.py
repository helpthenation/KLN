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

import time
from collections import Counter,OrderedDict
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.account.report.common_report_header import common_report_header
from itertools import groupby
import itertools
import re
from operator import itemgetter
class report_consolidated_balance(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(report_consolidated_balance, self).__init__(cr, uid, name, context=context)
        self.sum_debit = 0.00
        self.sum_credit = 0.00
        self.date_lst = []
        self.date_lst_string = ''
        self.result_acc = []
        self.localcontext.update({
            'time': time,
            'lines': self.lines,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_fiscalyear':self._get_fiscalyear,
            'get_filter': self._get_filter,
            'get_start_period': self.get_start_period,
            'get_end_period': self.get_end_period ,
            'get_account': self._get_account,
            'get_journal': self._get_journal,
            'get_start_date':self._get_start_date,
            'get_end_date':self._get_end_date,
            'get_target_move': self._get_target_move,
        })
        self.context = context

    def set_context(self, objects, data, ids, report_type=None):
        #~ print'DARAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',data['form']
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            #~ print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',new_ids
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
            #~ print'######################################',objects
        return super(report_consolidated_balance, self).set_context(objects, data, new_ids, report_type=report_type)

    def lines(self, form, ids=None, done=None):
        #~ print "777777777777",ids,form, self.ids
        total_lines=[]
        test=[]
        return_list=[]
        def _process_child(accounts, disp_acc, parent):
                #~ print'ACCCCCCCCCCCCCCCCCCCC',accounts
                account_rec = [acct for acct in accounts if acct['id']==parent][0]
                currency_obj = self.pool.get('res.currency')
                acc_id = self.pool.get('account.account').browse(self.cr, self.uid, account_rec['id'])
                currency = acc_id.currency_id and acc_id.currency_id or acc_id.company_id.currency_id
                res = {
                    'id': account_rec['id'],
                    'type': account_rec['type'],
                    'code': account_rec['code'],
                    'name': account_rec['name'],
                    'level': account_rec['level'],
                    'debit': account_rec['debit'],
                    'credit': account_rec['credit'],
                    'balance': account_rec['balance'],
                    'parent_id': account_rec['parent_id'],
                    'company_id': account_rec['company_id'],
                    'bal_type': '',
                }
                self.sum_debit += account_rec['debit']
                self.sum_credit += account_rec['credit']
                if disp_acc == 'movement':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['credit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['debit']) or not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                elif disp_acc == 'not_zero':
                    if not currency_obj.is_zero(self.cr, self.uid, currency, res['balance']):
                        self.result_acc.append(res)
                else:
                    self.result_acc.append(res)
                if account_rec['child_id']:
                    for child in account_rec['child_id']:
                        _process_child(accounts,disp_acc,child)

        obj_account = self.pool.get('account.account')
        if not ids:
            ids = self.ids
        if not ids:
            return []
        if not done:
            done={}

        ctx = self.context.copy()

        ctx['fiscalyear'] = form['fiscalyear_id']
        if form['filter'] == 'filter_period':
            ctx['period_from'] = form['period_from']
            ctx['period_to'] = form['period_to']
        elif form['filter'] == 'filter_date':
            ctx['date_from'] = form['date_from']
            ctx['date_to'] =  form['date_to']
        ctx['state'] = form['target_move']
        parents = ids
        #~ print "11",ctx,ids
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        #~ print child_ids
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id','company_id'], ctx)
        #~ print "33",parents
        #~ print "444",accounts
        for parent in parents:
                if parent in done:
                    continue
                done[parent] = 1
                _process_child(accounts,form['display_account'],parent)
        #~ print'REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE',self.result_acc
        for rec in self.result_acc:
            if rec['type'] != 'view' and rec['type'] != 'consolidation' :
                test.append(rec)
        #~ print'TESTTTTTTTTTTTTTTTTTTT',test
        #~ print "33333333333333333",test
        order_line =[]
        if test != []:
            order_line = sorted(test, key=itemgetter('code'))
        total_lines = sorted(order_line, key=lambda k: k['code'])

        #~ print total_lines
        report_final_lines = []
        lnd = []
        vhl = []
        mch = []
        equip = []
        fur = []
        inves = []
        loan = []
        open_stock = []
        sundry_deb = []
        bank_bal = []
        cash_bal = []
        deposit = []
        lons_advance = []
        part_acc = []
        sec_loan = []
        unsec_loan = []
        cap_ac = []
        othrs = []


        for tl in total_lines:
            if tl['code'] in ('120101'):
                lnd.append(tl)
            elif tl['code'] in ('120105','120102','120108','12165','12166'):
                vhl.append(tl)
            elif tl['code'] in ('120110','120113','120106','120114','120522','120112'):
                mch.append(tl)
            elif tl['code'] in ('120107','121250'):
                equip.append(tl)
            elif tl['code'] in ('120104'):
                fur.append(tl)
            elif tl['code'] in ('120200','120210','120220','120230','120240','120250','120260','121100','121110','121120','121130','121140','121150'):
                inves.append(tl)
            elif tl['code'] in ():
                loan.append(tl)
            elif tl['code'] in ('121200','121205','121201','121202','121203','121204'):
                open_stock.append(tl)
            elif tl['code'] in ('121330','121331','121332','121333','121334'):
                sundry_deb.append(tl)
            elif tl['code'] in ('1214213','121413','121414'):
                bank_bal.append(tl)
            elif tl['code'] in ('121411','121412','1214211'):
                cash_bal.append(tl)
            elif tl['code'] in ('121631','121632','121633'):
                deposit.append(tl)
            elif tl['code'] in ('1215111','1215121','121513','121514','121515',
            '121516','121517','121518','121519','121520','121521','121522','121523','121524','121525',
            '121526','121527','121528','121529', '121530','121531','121532','121533','121534','121535',
            '121536','121537','121538','121539','121540','121541','121542','121543','121544',
            '121521','121522','121523','121524','121525','121526','121527','121528','121529'):
                lons_advance.append(tl)
            elif tl['code'] in ('11441','11442'):
                part_acc.append(tl)
            elif tl['code'] in ('114011','114020','114030','114040','114013'):
                sec_loan.append(tl)
            elif tl['code'] in ('114120','114121','114122','114123','114110','114112','114113','114114','114115','114116','114118','114119'):
                unsec_loan.append(tl)
            elif tl['code'] in ('11101','11102'):
                cap_ac.append(tl)
            else:
                othrs.append(tl)
        #~ print "5555555555555",lnd
        def unique_list(l):
            ulist = []
            [ulist.append(x) for x in l if x not in ulist]
            return ulist        
        def sum_dict(dicts):
            code = []
            for i in dicts:
                for k,l in i.items():
                    if k == 'code':
                        code.append(str(l))
            print code
            fin_dict = []
            #~ for a in dicts:
                #~ print a
            for q in set(code):
                debit = 0
                credit = 0
                name = ""
                
                for a in dicts:
                    print  a['name']
                    if a['code'] == q:
                        print "1111!!!",q,a['code']
                        debit += a['debit']
                        credit += a['credit']
                        name +=  " " + str(a['name'])
                print "444444444",name,name.split() 
                f_name = ' '.join(unique_list(name.split()))

                print "444444444........",f_name
                fin_dict.append({'code':q,'name':f_name,'debit':debit,'credit':credit})
                
                   
            return fin_dict

        print "22222222222222", sum_dict( lnd)


        report_final_lines.extend([{'Land and Building ': sum_dict(lnd)},{'Vehicles':sum_dict (vhl)},{'Machinery':sum_dict(mch)},{'Office Equipments': sum_dict(equip) },
        {'Furnitures and Fixtures ': sum_dict(fur)},{'Investments': sum_dict(inves)},{'Loans and Advances': sum_dict(loan)},{'Opening Stock': sum_dict(open_stock)},
        {'Sundry Debtors':sum_dict(sundry_deb)},{'Bank  Balance': sum_dict(bank_bal)},{'Cash Balance': sum_dict(cash_bal)},{'Deposits': sum_dict(deposit)},
        {'Loans and Advances': sum_dict(lons_advance)},{'Partner Current Account':sum_dict(part_acc)},{'Secured Loans':sum_dict(sec_loan)},
        {'Unsecured Loans': sum_dict(unsec_loan)},{'Partner Capital Account': sum_dict(cap_ac)},
        #~ {'Others':othrs}
        ])
        #~ print report_final_lines
        #~ for i in report_final_lines:
            #~ print "444444444444444",i
            #~ for j in i[i.keys()[0]]:
                #~ for l in j.values():
                    #~ print "11111111111111111",l

        return report_final_lines


class report_consolidated_tb_balance(osv.AbstractModel):
    _name = 'report.fnet_aea_consolidated_balance.report_consolidated_balance'
    _inherit = 'report.abstract_report'
    _template = 'fnet_aea_consolidated_balance.report_consolidated_balance'
    _wrapped_report_class = report_consolidated_balance



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
