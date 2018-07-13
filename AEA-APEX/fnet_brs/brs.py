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
from openerp import _
from openerp.exceptions import ValidationError,Warning
from openerp.osv import fields, osv
from datetime import datetime, timedelta, date
import time
import openerp.addons.decimal_precision as dp
import dateutil.relativedelta
from datetime import datetime
from datetime import timedelta
from datetime import date
from dateutil.rrule import rrule, DAILY
from dateutil.parser import parse
from itertools import groupby
import itertools
from operator import itemgetter
class bank_reconsile_statement(osv.osv):

    _name = 'bank.reconsile'

    _columns={
        'name':fields.char('Name',required=True),
        'active':fields.boolean('Active'),
        'brs_line':fields.one2many('brs.line','line_id','Choose Journal')
    }

    _defaults = {
         'active': True,

    }

class bank_reconsile_line(osv.osv):

    _name = 'brs.line'

    _columns={
        'line_id':fields.many2one('bank.reconsile', 'BRS'),
        'journal_id':fields.many2one('account.journal', 'Journal',required=True),
        'company_id':fields.many2one('res.company','Company',required=True),
    }

    def onchange_journal_id(self, cr, uid, ids,journal_id,context):
        if not journal_id:
            return False
        if context is None:
            context = {}
        journal_pool = self.pool.get('account.journal')
        journal = journal_pool.browse(cr, uid, journal_id, context=context)
        vals = {'value':{} }
        vals['value'].update({'company_id':journal.company_id.id})
        return vals

class bank_reconsile_state(osv.osv):

    _name='brs.statement'

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('brs.statement.line').browse(cr, uid, ids, context=context):
            result[line.brs_id.id] = True
        return result.keys()

    def _unreconcile_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'debit': 0.0,
                'credit': 0.0,
                'unreconcile_debit': 0.0,
                'unreconcile_credit': 0.0,
            }
            val = val1 = val2 = val3=0.0
            for line in order.statement_line:
                if line.reconcile:
                    val += line.balance #credit
                    val1 += line.credit
                else:
                    val2 += line.balance
                    val3 += line.credit
            res[order.id]['credit'] = val1
            res[order.id]['debit'] = val
            res[order.id]['unreconcile_debit'] = val2
            res[order.id]['unreconcile_credit'] = val3
        return res


    def _balance_amount(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.opening_balance + ( line.credit  -  line.debit)
        return res

    def _check_date(self, cr, uid, ids, context=None):
        if context == None:
            context = {}
        obj_task = self.browse(cr, uid, ids[0], context=context)
        start = obj_task.from_date or False
        end = obj_task.to_date or False
        if start and end :
            DATETIME_FORMAT = "%Y-%m-%d"  ## Set your date format here
            from_dt = datetime.strptime(start, DATETIME_FORMAT)
            to_dt = datetime.strptime(end, DATETIME_FORMAT)
            if to_dt < from_dt:
                return False
        return True
    _columns={
        'share':fields.char('Paid'),
        'brs_id':fields.many2one('bank.reconsile','BRS Journal',required=True),
        'from_date':fields.date('From Date',required=True),
        'to_date':fields.date('To Date',required=True),
        'bank_balance':fields.float('Bank Statement Balance'),
        'opening_balance':fields.float('Opening Balance'),
        'is_imported':fields.boolean('Imported Entry'),
        'statement_line':fields.one2many('brs.statement.line','brs_id','Account Entry'),
        'unreconcile_balance': fields.function(_balance_amount, string='Reconcile Balance', digits_compute= dp.get_precision('Discount')),
        'debit': fields.function(_unreconcile_amount, digits_compute=dp.get_precision('Discount'), string='Debit',
            store={
                'brs.statement': (lambda self, cr, uid, ids, c={}: ids, ['statement_line'], 10),
                'brs.statement.line': (_get_order, ['reconcile', 'balance', 'credit'], 10),
            },
            multi='sums'),
        'credit': fields.function(_unreconcile_amount, digits_compute=dp.get_precision('Discount'), string='Credit',
            store={
                'brs.statement': (lambda self, cr, uid, ids, c={}: ids, ['statement_line'], 10),
                'brs.statement.line': (_get_order, ['reconcile', 'balance', 'credit'], 10),
            },
            multi='sums'),
        'unreconcile_debit': fields.function(_unreconcile_amount, digits_compute=dp.get_precision('Discount'), string='Unreconcile Debit',
            store={
                'brs.statement': (lambda self, cr, uid, ids, c={}: ids, ['statement_line'], 10),
                'brs.statement.line': (_get_order, ['reconcile', 'balance', 'credit'], 10),
            },
            multi='sums'),
        'unreconcile_credit': fields.function(_unreconcile_amount, digits_compute=dp.get_precision('Discount'), string='Unreconcile Credit',
            store={
                'brs.statement': (lambda self, cr, uid, ids, c={}: ids, ['statement_line'], 10),
                'brs.statement.line': (_get_order, ['reconcile', 'balance', 'credit'], 10),
            },
            multi='sums'),
        'state':fields.selection([
            ('draft', 'Draft'),
            ('progress', 'Progress'),
            ('cancel', 'Cancel'),
            ('done', 'Done'),
            ],'Status',  select=True, readonly=True, copy=False), 
    }

    _defaults = {
         'state': 'draft',
         'is_imported': False,
    }

    _constraints = [
            (_check_date, '\n Error !  \n To Date must be greater then From Date', ['from_date','to_date']),
        ]
    #~ def onchange_todate(self, cr, uid, ids, to_date,context=None):
        #~ result = {}
        #~ if to_date and ids != []:
            #~ cr.execute("select max(id) as max  from brs_statement where id != %d" %(ids[0]))
            #~ ID=cr.dictfetchone()
            #~ if ID:
                #~ if ID['max']:
                    #~ cr.execute("select to_date from brs_statement where id = %d"%(ID['max']))
                    #~ dat=cr.dictfetchone()
                    #~ result['value'] = {'from_date':dat['to_date']}
        #~ elif to_date and ids == []:
            #~ cr.execute("select max(id) as max from brs_statement")
            #~ ID=cr.dictfetchone()
            #~ if ID:
                #~ if ID['max']:
                    #~ cr.execute("select to_date from brs_statement where id = %d"%(ID['max']))
                    #~ dat=cr.dictfetchone()
                    #~ result['value'] = {'from_date':dat['to_date']}
        #~ else:
            #~ result['value'] = {'from_date':'2017-09-19'}
        #~ return result
    def select_all(self, cr, uid, ids,context):
        brs_pool = self.pool.get('brs.statement').browse(cr,uid,ids)
        for line in brs_pool.statement_line:
            if not line.reconcile:
                self.pool.get('brs.statement.line').write(cr, uid, line.id, {'reconcile':True,'reconsile_date':line.date},context=context)



    def validate(self,cr,uid,ids,context):
        brs_pool = self.pool.get('brs.statement').browse(cr,uid,ids)
        cr.execute("""select id as id from brs_statement where id != %d and state = 'draft' """%(brs_pool.id))
        previous=cr.fetchall()
        if previous != []:
            raise osv.except_osv(_('ValidateError'), _('Previous Form Need To Be Validated!!'))
        if  str(brs_pool.unreconcile_balance) == str(brs_pool.bank_balance):            
            for line in brs_pool.statement_line:
                cr.execute("""select group_brs_rel.g_id,reconcile from brs_statement_line
                left join group_brs_rel on group_brs_rel.brs_id = brs_statement_line.id
                where id = %d"""%(line['id']))
                group = [i for i in cr.dictfetchall()]              
                for i in group:
                    if i['g_id'] != None and i['reconcile']==True:
                        move_pool=self.pool.get('account.move')
                        account_move_line_obj = self.pool.get('account.move.line')
                        move_rec=move_pool.browse(cr,uid,i['g_id'])
                        if move_rec.state == 'draft':
                            user_id=sorted(self.pool.get('res.users').search(cr,uid,[('company_id','=',move_rec.company_id.id)]))[0]
                            move_pool.button_validate(cr,user_id,i['g_id'],context=None)
                            move_pool.write(cr, uid, i['g_id'], {'reconcile':True,'bank_date':line.reconsile_date},context=context)
                        elif move_rec.state == 'posted':
                            move_pool.write(cr, uid, i['g_id'], {'reconcile':True,'bank_date':line.reconsile_date},context=context)                       
                if line.reconcile:
                    move_pool=self.pool.get('account.move')
                    account_move_line_obj = self.pool.get('account.move.line')
                    move_rec=move_pool.browse(cr,uid,line.move_id.id)
                    if move_rec.state == 'draft':
                        user_id=sorted(self.pool.get('res.users').search(cr,uid,[('company_id','=',line.company_id.id)]))[0]
                        move_pool.button_validate(cr,user_id,line.move_id.id,context=None)
                        move_pool.write(cr, uid, line.move_id.id, {'reconcile':True,'bank_date':line.reconsile_date},context=context)
                    elif move_rec.state == 'posted':
                        move_pool.write(cr, uid, line.move_id.id, {'reconcile':True,'bank_date':line.reconsile_date},context=context)
            brs_state = self.pool.get('brs.statement').search(cr,uid,[('state','=','progress')])
            if brs_state != []:
                for line in brs_state:
                      self.pool.get('brs.statement').write(cr, uid, line, {'state':'cancel'},context=context)
            self.write(cr, uid, ids, {'state':'done'},context=context)
        else:
            raise osv.except_osv(_('ValidateError'), _('Bank Statement amount and Unreconcile amount is not equal.'))


    def reset_to_draft(self, cr, uid, ids,context):
        brs_pool = self.pool.get('brs.statement').browse(cr,uid,ids)
        cr.execute("""select id from brs_statement where id != %d and state = 'done' """%(brs_pool.id))
        next_form=cr.fetchall()
        if next_form != []:
            raise osv.except_osv(_('ValidateError'), _('Reset Successor Form To Draft!!'))
        for line in brs_pool.statement_line:
            if line.reconcile:
                self.pool.get('account.move').write(cr, uid, line.move_id.id, {'reconcile':False,'bank_date':False},context=context)
            else:
                self.pool.get('account.move').write(cr, uid, line.move_id.id, {'reconcile':False,'bank_date':False},context=context)
        self.write(cr, uid, ids, {'state':'draft'},context=context)
        
    def unlink(self, cr, uid, ids, context=None):
        brs_state = self.read(cr, uid, ids, ['state'], context=context)
        unlink_ids = []
        for s in brs_state:
            if s['state'] in ['draft']:
                unlink_ids.append(s['id'])
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete this BRS!'))
        if unlink_ids != []:
            for i in unlink_ids:
                cr.execute("""DELETE FROM brs_statement WHERE id=%d"""%(i))
                cr.execute("""DELETE FROM brs_statement_line WHERE brs_id is null""")
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context)  

    def cancel(self, cr, uid, ids,context):
        brs_pool = self.pool.get('brs.statement').browse(cr,uid,ids)
        for line in brs_pool.statement_line:
            if line.reconcile:
                self.pool.get('account.move').write(cr, uid, line.move_id.id, {'reconcile':False},context=context)
            else:
                self.pool.get('account.move').write(cr, uid, line.move_id.id, {'reconcile':False},context=context)
            cr.execute("""DELETE FROM brs_statement_line WHERE id=%d"""%(line.id))   
        self.write(cr, uid, ids, {'state':'cancel'},context=context)
        
    def unreconcile(self, cr, uid, ids,context):
        brs_pool = self.pool.get('brs.statement').browse(cr,uid,ids)
        for line in brs_pool.statement_line:
            if line.deselect:
                self.pool.get('account.move').write(cr, uid, line.move_id.id, {'reconcile':False,'bank_date':False},context=context)
                line.write({'reconsile_date':False,'reconcile':False}) 
        self.write(cr, uid, ids, {'state':'progress'},context=context)


    def generate(self, cr, uid, ids,context):
        brs_pool = self.pool.get('brs.statement').browse(cr,uid,ids)
        journal_lists=[]
        for i in brs_pool.brs_id.brs_line:
            journal_lists.append(i.journal_id.id)
        company_list=[]
        company_ids = self.pool.get('res.users')._get_company(cr, uid, context=context)
        val=self.pool.get('res.company').search(cr, uid,[])
        rec=[i for i in val if i!=company_ids ]
        company_list.extend(rec)
        from_date=datetime.strptime(brs_pool.from_date,'%Y-%m-%d')
        to_date=datetime.strptime(brs_pool.to_date,'%Y-%m-%d')
        previous_from_date=from_date + dateutil.relativedelta.relativedelta(months=-1)
        previous_to_date=from_date + dateutil.relativedelta.relativedelta(days=-1,hours=23)+timedelta(minutes = 59,seconds=59)
        cr.execute(
            "select (sum(aml.debit)-sum(aml.credit)) as balance  " \
            "from account_move am  " \
            "join account_move_line aml on (aml.move_id=am.id) " \
            "join account_account aa on (aml.account_id=aa.id)" \
            "join account_account_type aat on (aa.user_type=aat.id)"\
            "join account_journal aj on (aj.id=am.journal_id)"\
                " where aat.code in ('receivable','payable','bank') and aa.active= True and aj.type='bank' and " \
                #~ " aml.reconcile_id IS NULL and " \
                #~ " aml.reconcile_partial_id IS NULL and " \
                " am.company_id in %s "\
                " and am.reconcile != 'True' "\
                " and am.date = '%s' and aj.id in %s " \
                " order by 1"% (tuple(company_list),str(to_date),tuple(journal_lists)))
        balnce_list = [i for i in cr.dictfetchall()]
        for line in balnce_list:
            self.write(cr, uid, ids, {'opening_balance':line['balance']},context=context)
        brs_rec = self.pool.get('bank.reconsile')
        brs_val=brs_rec.browse(cr,uid,brs_pool.brs_id.id)
        lines=[]
        for rec in brs_val.brs_line:
            if brs_pool.to_date == brs_pool.from_date: 
                cr.execute("""select distinct on(aml.move_id) am.date, aml.debit,aml.credit, am.ref as cheque, am.consolidate_cheque_no as consolidate_cheque_no,
                        am.company_id,am.id as move_id,
                        am.narration,aml.partner_id,am.bank_date
                        from account_move am
                        join account_move_line aml on (aml.move_id = am.id)
                        join account_journal aj on (aj.id=am.journal_id)  where
                        aml.debit > 0 and aml.account_id = aj.default_debit_account_id and am.company_id=%s
                        and am.date = '%s' and am.date = '%s' and am.journal_id=%s and ((am.reconcile is null) or (am.reconcile = False)) and am.bank_date is null
                        order by aml.move_id """ % (rec.company_id.id,brs_pool.to_date,brs_pool.from_date,rec.journal_id.id))
                line_list = [i for i in cr.dictfetchall()]
                lines.extend(line_list)
                cr.execute("""select distinct on(aml.move_id) am.date, aml.debit,aml.credit, am.ref as cheque, am.company_id,am.id as move_id,am.narration,aml.partner_id,am.consolidate_cheque_no as consolidate_cheque_no,am.bank_date
                        from account_move am
                        join account_move_line aml on (aml.move_id = am.id)
                        join account_journal aj on (aj.id=am.journal_id)  where
                        aml.credit > 0 and aml.account_id = aj.default_credit_account_id and am.company_id=%s
                        and am.date = '%s' and am.date = '%s' and am.journal_id=%s and ((am.reconcile is null) or (am.reconcile = False)) and am.bank_date is null
                        order by aml.move_id """ % (rec.company_id.id,brs_pool.to_date,brs_pool.from_date,rec.journal_id.id))
                line_list = [i for i in cr.dictfetchall()]
                lines.extend(line_list)
            else:
                cr.execute("""select distinct on(aml.move_id) am.date, aml.debit,aml.credit, am.ref as cheque, 
                        am.company_id,am.id as move_id,
                        am.narration,aml.partner_id,am.consolidate_cheque_no as consolidate_cheque_no,am.bank_date
                        from account_move am
                        join account_move_line aml on (aml.move_id = am.id)
                        join account_journal aj on (aj.id=am.journal_id)  where
                        aml.debit > 0 and aml.account_id = aj.default_debit_account_id and am.company_id=%s
                        and am.date >= '%s' and am.date <= '%s' and am.journal_id=%s  and ((am.reconcile is null) or (am.reconcile = False)) and am.bank_date is null
                        order by aml.move_id """ % (rec.company_id.id,brs_pool.from_date,brs_pool.to_date,rec.journal_id.id))
                line_list = [i for i in cr.dictfetchall()]
                lines.extend(line_list)
                cr.execute("""select distinct on(aml.move_id) am.date, aml.debit,aml.credit, am.ref as cheque, am.consolidate_cheque_no as consolidate_cheque_no,am.company_id,am.id as move_id,am.narration,aml.partner_id,am.consolidate_cheque_no as consolidate_cheque_no,am.bank_date
                        from account_move am
                        join account_move_line aml on (aml.move_id = am.id)
                        join account_journal aj on (aj.id=am.journal_id)  where
                        aml.credit > 0 and aml.account_id = aj.default_credit_account_id and am.company_id=%s
                        and am.date >= '%s' and am.date <= '%s' and am.journal_id=%s and ((am.reconcile is null) or (am.reconcile = False)) and am.bank_date is null
                        order by aml.move_id """ % (rec.company_id.id,brs_pool.from_date,brs_pool.to_date,rec.journal_id.id))
                line_list = [i for i in cr.dictfetchall()]
                lines.extend(line_list)                 
        if lines != []:
            sss=sorted(lines,key=itemgetter('consolidate_cheque_no','partner_id'))
            r={}
            for key,value in itertools.groupby(sss,key=itemgetter('consolidate_cheque_no','partner_id')):
                for i in value:
                    r.setdefault(key, []).append(i)
            for key,value in r.iteritems():
                if len(value) > 1:
                    if key[0]:
                        d=[]
                        c=[]
                        com=''
                        grp=[]
                        for i in value:
                              grp.append(i['move_id'])
                              d.append(i['debit'])
                              c.append(i['credit'])
                              com+=str(self.pool.get('res.company').browse(cr,uid,i['company_id']).name)+ '  '
                        vals = {
                           'brs_id':brs_pool.id,
                           'cheque':i['cheque'],
                           'date':i['date'],
                           'balance':sum(c),
                           'credit':sum(d),
                           'company_id':i['company_id'],
                           'move_id':i['move_id'],
                           'description':com,
                           'partner_id':i['partner_id'],
                           'reconsile_date':i['bank_date'],
                           'group_ids':[(4,grp)]
                         }
                        if vals['reconsile_date']:
                            vals.update({'reconcile':True})
                        ent_obj = self.pool.get('brs.statement.line').create(cr,uid,vals,context=None)
                    else:   
                        for val in value:
                            vals = {
                                   'brs_id':brs_pool.id,
                                   'cheque':val['cheque'],
                                   'date':val['date'],
                                   'balance':val['credit'],
                                   'credit':val['debit'],
                                   'company_id':val['company_id'],
                                   'move_id':val['move_id'],
                                   'description':val['narration'],
                                   'partner_id':val['partner_id'],
                                   'reconsile_date':val['bank_date']
                            }
                            if vals['reconsile_date']:
                                vals.update({'reconcile':True})                    
                            self.pool.get('brs.statement.line').create(cr,uid,vals,context=None)                        
                else:
                    vals = {
                           'brs_id':brs_pool.id,
                           'cheque':value[0]['cheque'],
                           'date':value[0]['date'],
                           'balance':value[0]['credit'],
                           'credit':value[0]['debit'],
                           'company_id':value[0]['company_id'],
                           'move_id':value[0]['move_id'],
                           'description':value[0]['narration'],
                           'partner_id':value[0]['partner_id'],
                           'reconsile_date':value[0]['bank_date']
                    }
                    if vals['reconsile_date']:
                        vals.update({'reconcile':True})                    
                    self.pool.get('brs.statement.line').create(cr,uid,vals,context=None)
        self.write(cr, uid, ids, {'state':'progress'},context=context)


class bank_statement_line(osv.osv):

    _name='brs.statement.line'
    _columns={
        'brs_id':fields.many2one('brs.statement',ondelete='cascade'),
        'company_id':fields.many2one('res.company','Branch'),
        'move_id':fields.many2one('account.move'),
        'cheque':fields.char('Cheque No'),
        'date':fields.date('Value Date'),
        'reconsile_date':fields.date('Transaction Date'),
        'balance':fields.float('Debit'),
        'credit':fields.float('Credit'),
        'reconcile':fields.boolean('Reconcile'),
        'deselect':fields.boolean('Select'),
        'description':fields.text('Description'),
        'partner_id':fields.many2one('res.partner','Customer Name'),
        'partner_code':fields.related('partner_id','customer_id',type='char',string='Customer ID'),
        'state':fields.related('brs_id','state',type='char',string='state'),
        'group_ids':fields.many2many('account.move','group_brs_rel','brs_id','g_id',string="Group Line"),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying lines."),
    }
    _order = 'date'
    _defaults = {
        'sequence': 10,
       }

    def onchange_reconcile(self, cr, uid, ids, reconcile, reconsile_date,context=None):
        result = {}
        list_li=[]
        if reconcile:
            result['value'] = {'reconsile_date':''}
        elif reconcile == False:
            result['value'] = {'reconsile_date':''}
        return result
    def onchange_reconcile_date(self, cr, uid, ids,reconsile_date,date,context=None):
        result = {}
        list_li=[]
        if reconsile_date:
            DATETIME_FORMAT = "%Y-%m-%d"  ## Set your date format here
            reconsile_date = datetime.strptime(reconsile_date, DATETIME_FORMAT)
            date = datetime.strptime(date, DATETIME_FORMAT)
            if reconsile_date < date:
                return {'warning': {
                    'title': "Warning",
                    'message': "Invalid Transcation Date!",
                    },
                   'value': {'reconsile_date':''}
                }

    def unlink(self, cr, uid, ids, context=None):
        brs_pool = self.pool.get('brs.statement.line').browse(cr,uid,ids)
        unlink_ids = []
        for s in brs_pool:
            brs_obj=self.pool.get('brs.statement').browse(cr,uid,s.brs_id.id)
            if brs_obj.state == 'draft':
                unlink_ids.append(s.id)
            else:
                raise osv.except_osv(_('Invalid Action!'), _('You cannot delete brs line which is done state!'))
        if unlink_ids != []:
            for i in unlink_ids:
                cr.execute("""DELETE FROM brs_statement_line WHERE id=%d"""%(i))
        return osv.osv.unlink(self, cr, uid, unlink_ids, context=context) 
class account_move(osv.osv):

    _inherit= 'account.move'

    _columns={
        'reconcile':fields.boolean('Reconcile'),
        'is_consolidated':fields.boolean('Is Consolidated Entry'),
        'consolidate_cheque_no':fields.char('Reference No'),
        'bank_date':fields.date('Bank Book Date'),
    }
    _defaults={
        'reconcile':False,
        'is_consolidated':False,
        'bank_date':False,
    }    


