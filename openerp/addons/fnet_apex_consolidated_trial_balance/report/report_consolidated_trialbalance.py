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
class report_consolidated_trialbalance(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context=None):
        super(report_consolidated_trialbalance, self).__init__(cr, uid, name, context=context)
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
        print'DARAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',data['form']
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'chart_account_id' in data['form'] and [data['form']['chart_account_id']] or []
            print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',new_ids
            objects = self.pool.get('account.account').browse(self.cr, self.uid, new_ids)
            print'######################################',objects
        return super(report_consolidated_trialbalance, self).set_context(objects, data, new_ids, report_type=report_type)

    def lines(self, form, ids=None, done=None):
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
        child_ids = obj_account._get_children_and_consol(self.cr, self.uid, ids, ctx)
        if child_ids:
            ids = child_ids
        accounts = obj_account.read(self.cr, self.uid, ids, ['type','code','name','debit','credit','balance','parent_id','level','child_id','company_id'], ctx)

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
        if test != []:
            order_line=sorted(test,key=itemgetter('code'))
            grouped_code={}
            for key,value in itertools.groupby(order_line,key=itemgetter('code')):
                for i in value:
                    grouped_code.setdefault(key, []).append(i)
            #~ print'ORDERRRRRRRRRRRRRRRRRRRRRRRR',  grouped_code
            for key,value in grouped_code.iteritems():
                com_val={}
                bal=[]
                for i in value:
                    com_val.update({i['company_id'][0]:i['balance']})
                    bal.append(i['balance'])
                i['name'] = str(i['name']).replace("OB","",1)
                i['name'] = str(i['name']).replace("OS","",1)
                i['name'] = str(i['name']).replace("TL","",1)
                i['name'] = str(i['name']).replace("AP","",1)
                i['name'] = str(i['name']).replace("HO","",1)
                com_val.update({'code':key,'name':i['name'],'balance':sum(bal)})
                if 3 not in com_val:
                    com_val.update({3:'0.00'})
                if 4 not in com_val:
                    com_val.update({4:'0.00'})
                if 5 not in com_val:
                    com_val.update({5:'0.00'})
                if 6 not in com_val:
                    com_val.update({6:'0.00'})
                if 8 not in com_val:
                    com_val.update({8:'0.00'})
                return_list.append(com_val)
        #~ for rec in return_list:
            #~ print'RECCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC',rec
        total_lines = sorted(return_list, key=lambda k: k['code'])
        #~ print total_lines
        d = 0
        f = 0
        vat = []
        igst0 = []
        igst5 = []
        igst12 = []
        igst18 = []
        igst28 = []

        sgst0 = []
        sgst25 = []
        sgst6 = []
        sgst9 = []
        sgst14 = []

        cgst0 = []
        cgst25 = []
        cgst6 = []
        cgst9 = []
        cgst14 = []

        total_lines_final= []

        def sum_dict(d1, d2):
            for key, value in d1.items():
                print "5555",key
                if key == 'name':
                     #~ d1[key] =  ' '.join(OrderedDict((w,w) for w in re.sub("Payable|Receivable", " ", value + d2.get(key, 0)).split()).keys())    #ok
                     d1[key] = ' '.join(OrderedDict.fromkeys(re.sub("Payable|Receivable", " ", value + d2.get(key, 0)).split()))    #ok

                    #~ d1[key] =  ''.join(OrderedDict.fromkeys(re.sub("Payable|Receivable", " ", value + d2.get(key, 0))))  # working but sgst to sgt elemnating repeating character
                elif key == 'code':
                    d1[key] = value +"  " + d2.get(key, 0)
                else:
                    d1[key] = value + d2.get(key, 0)

            return d1

        for k in total_lines:

            if  "VAT" in k['name']:
                vat.append(k)

            elif  "IGST 0%" in k['name']:
                igst0.append(k)
            elif  "IGST 5%" in k['name']:
                igst5.append(k)
            elif  "IGST 12%" in k['name']:
                igst12.append(k)
            elif  "IGST 18%" in k['name']:
                igst18.append(k)
            elif  "IGST 28%" in k['name']:
                igst28.append(k)

            elif  "SGST 0%" in k['name']:
                sgst0.append(k)
            elif  "SGST 2.5%" in k['name']:
                sgst25.append(k)
            elif  "SGST 6%" in k['name']:
                sgst6.append(k)
            elif  "SGST 9%" in k['name']:
                sgst9.append(k)
            elif  "SGST 14%" in k['name']:
                sgst14.append(k)


            elif  "CGST 0%" in k['name']:
                cgst0.append(k)
            elif  "CGST 2.5%" in k['name']:
                cgst25.append(k)
            elif  "CGST 6%" in k['name']:
                cgst6.append(k)
            elif  "CGST 9%" in k['name']:
                cgst9.append(k)
            elif  "CGST 14%" in k['name']:
                cgst14.append(k)
            else:
                total_lines_final.append(k)
        print "44444444444444",vat
        if vat:
            total_lines_final.append(reduce(sum_dict, vat))

        if igst0:
            total_lines_final.append(reduce(sum_dict, igst0))
        if igst5:
            total_lines_final.append(reduce(sum_dict, igst5))
        if igst12:
           total_lines_final.append(reduce(sum_dict, igst12))
        if igst18:
            total_lines_final.append(reduce(sum_dict, igst18))
        if igst28:
            total_lines_final.append(reduce(sum_dict, igst28))

        if cgst0:
            total_lines_final.append(reduce(sum_dict, cgst0))
        if cgst25:
            total_lines_final.append(reduce(sum_dict, cgst25))
        if cgst6:
            total_lines_final.append(reduce(sum_dict, cgst6))
        if cgst9:
           total_lines_final.append(reduce(sum_dict, cgst9))
        if cgst14:
           total_lines_final.append(reduce(sum_dict, cgst14))

        if sgst0:
            total_lines_final.append(reduce(sum_dict, sgst0))
        if sgst25:
            total_lines_final.append(reduce(sum_dict, sgst25))
        if sgst6:
            total_lines_final.append(reduce(sum_dict, sgst6))
        if sgst9:
            total_lines_final.append(reduce(sum_dict, sgst9))
        if sgst14:
            total_lines_final.append(reduce(sum_dict, sgst14))

        #~ print total_lines_final

        for  g in total_lines_final:
            print g
            for k,v in g.items():               
               if v == "0.000.00":
                   g.update({k:0.00})
               elif v == "0.00":
                   g.update({k:0.00})
            print g
                    
        #~ print total_lines_final
        return total_lines_final


class report_consolidated_trial_balance(osv.AbstractModel):
    _name = 'report.fnet_apex_consolidated_trial_balance.report_consolidated_trialbalance'
    _inherit = 'report.abstract_report'
    _template = 'fnet_apex_consolidated_trial_balance.report_consolidated_trialbalance'
    _wrapped_report_class = report_consolidated_trialbalance



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
