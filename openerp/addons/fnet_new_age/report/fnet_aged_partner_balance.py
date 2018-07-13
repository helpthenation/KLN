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
from openerp.osv import osv
from openerp.report import report_sxw
from common_report_header import common_report_header
from datetime import datetime
from itertools import groupby
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
import itertools
from operator import itemgetter
from dateutil.parser import parse
class fnet_aged_partner_report(report_sxw.rml_parse, common_report_header):

    def __init__(self, cr, uid, name, context):
        super(fnet_aged_partner_report, self).__init__(cr, uid, name, context=context)
        self.total_account = []
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
            'get_total': self._get_total,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'get_account': self._get_account,
            'get_fiscalyear': self._get_fiscalyear,
            'get_target_move': self._get_target_move,
        })

    def set_context(self, objects, data, ids, report_type=None):
        obj_move = self.pool.get('account.move.line')
        ctx = data['form'].get('used_context', {})
        ctx.update({'fiscalyear': False, 'all_fiscalyear': True})
        self.query = obj_move._query_get(self.cr, self.uid, obj='l', context=ctx)
        self.direction_selection = data['form'].get('direction_selection', 'past')
        self.target_move = data['form'].get('target_move', 'all')
        self.date_from = data['form'].get('date_from', time.strftime('%Y-%m-%d'))
        if (data['form']['result_selection'] == 'customer' ):
            self.ACCOUNT_TYPE = ['receivable']
        elif (data['form']['result_selection'] == 'supplier'):
            self.ACCOUNT_TYPE = ['payable']
        else:
            self.ACCOUNT_TYPE = ['payable','receivable']
        self.cr.execute(
            "SELECT a.id " \
            "FROM account_account a " \
            "LEFT JOIN account_account_type t " \
                "ON (a.type=t.code) " \
                'WHERE a.type IN %s' \
                "AND a.active", (tuple(self.ACCOUNT_TYPE), ))
        self.account_ids = [a for (a,) in self.cr.fetchall()]  
        self.journal_ids=self.pool.get('account.journal').search(self.cr, self.uid ,[])
        return super(fnet_aged_partner_report, self).set_context(objects, data, ids, report_type=report_type)

    def _get_lines(self, form):
        res = []
        move_state = ['draft','posted']
        if self.target_move == 'posted':
            move_state = ['posted']
        self.cr.execute('SELECT DISTINCT res_partner.id AS id,\
                    res_partner.name AS name, \
                    res_partner.city AS city \
                FROM res_partner,account_move_line AS l, account_account, account_move am\
                WHERE (l.account_id=account_account.id) \
                    AND (l.move_id=am.id) \
                    AND (am.state IN %s)\
                    AND (account_account.type IN %s)\
                    AND account_account.active\
                    AND ((reconcile_id IS NULL)\
                       OR (reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))\
                    AND (l.partner_id=res_partner.id)\
                    AND (l.date <= %s)\
                    AND ' + self.query + ' \
                ORDER BY res_partner.name', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, self.date_from,))
        partners = self.cr.dictfetchall()
        partner_ids=[]
        if form['selection'] == 'sales':
            if len(form['sr_id']) > 1:
                self.cr.execute("""SELECT distinct rp.id, rc.name as branch, 
                                            rp.name as partner,
                                            rp.name as salesperson
                                            FROM account_invoice ai 
                                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                                            JOIN res_company rc ON (rc.id = ai.company_id)
                                            LEFT JOIN res_users ru ON (ru.id = rp.user_id)
                                            WHERE rp.user_id IN %s """ %(tuple(form['sr_id']),))
                sale_person=self.cr.dictfetchall()
                selected_partner_ids = [x['id'] for x in sale_person]
            elif len(form['sr_id']) == 1:
                self.cr.execute("""SELECT distinct rp.id, rc.name as branch, 
                                            rp.name as partner,
                                            rp.name as salesperson
                                            FROM account_invoice ai 
                                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                                            JOIN res_company rc ON (rc.id = ai.company_id)
                                            LEFT JOIN res_users ru ON (ru.id = rp.user_id)
                                            WHERE rp.user_id = %s """ %(form['sr_id'][0]))
                sale_person=self.cr.dictfetchall()
                selected_partner_ids = [x['id'] for x in sale_person]
        elif form['selection'] == 'executive':
            selected_partner_ids = form['stockiest_ids']       
        elif form['selection'] == 'team':                
            if len(form['manager_id']) > 1:
                self.cr.execute("""SELECT distinct rp.id, rc.name as branch,
                                            rp.name as partner,
                                            rp.name as salesperson
                                            FROM account_invoice ai 
                                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                                            JOIN res_company rc ON (rc.id = ai.company_id)
                                            JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)
                                            WHERE css.user_id IN %s """%(tuple(form['manager_id']),))
                sale_person=self.cr.dictfetchall()  
                selected_partner_ids = [x['id'] for x in sale_person]
            elif len(form['manager_id']) == 1:
                self.cr.execute("""SELECT distinct rp.id, rc.name as branch,
                                            rp.name as partner,
                                            rp.name as salesperson
                                            FROM account_invoice ai 
                                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                                            JOIN res_company rc ON (rc.id = ai.company_id)
                                            JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)
                                            WHERE css.user_id = %s """%(form['manager_id'][0]))
                sale_person=self.cr.dictfetchall()  
                selected_partner_ids = [x['id'] for x in sale_person]
                
        elif form['selection']=='all':
            selected_partner_ids=[x['id'] for x in partners]
                                    
        for x in partners:
             if x['id'] in selected_partner_ids:
                 partner_ids.append(x['id'])
        if not partner_ids:
            return []

        info=[] 
        # This dictionary will store the future or past of all partners
        future_past = {}
        if self.direction_selection == 'future':
            self.cr.execute('SELECT l.partner_id,SUM(l.debit-l.credit) ,l.reconcile_partial_id, l.date,aj.code,l.ref,l.reconcile_id\
                        FROM account_move_line AS l, account_account, account_move am \
                        JOIN account_journal AS aj ON(aj.id=am.journal_id)\
                        WHERE (l.account_id=account_account.id) AND (l.move_id=am.id) \
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity, l.date) < %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s)\
                        GROUP BY l.partner_id, l.reconcile_partial_id,l.ref,aj.code,l.date,l.reconcile_id', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids),self.date_from, self.date_from,))
            t = self.cr.fetchall()
            for i in t:
                info.append({'partner_id':i[0],'code':i[4],'dates':i[3],'amt':i[1],'journal':i[5],'part_rec':i[2],'rec_id':i[6]})
                future_past[i[0]] = i[1]
                
        elif self.direction_selection == 'past': # Using elif so people could extend without this breaking
            self.cr.execute('SELECT l.partner_id, SUM(l.debit-l.credit) ,l.reconcile_partial_id, l.date,aj.code,l.ref,l.reconcile_id\
                    FROM account_move_line AS l, account_account, account_move am \
                    JOIN account_journal AS aj ON(aj.id=am.journal_id)\
                    WHERE (l.account_id=account_account.id) AND (l.move_id=am.id)\
                        AND (am.state IN %s)\
                        AND (account_account.type IN %s)\
                        AND (COALESCE(l.date_maturity,l.date) > %s)\
                        AND (l.partner_id IN %s)\
                        AND ((l.reconcile_id IS NULL)\
                        OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s  AND not recon.opening_reconciliation)))\
                        AND '+ self.query + '\
                        AND account_account.active\
                    AND (l.date <= %s )\
                        GROUP BY l.partner_id, l.reconcile_partial_id,l.reconcile_id,l.ref,aj.code,l.date \
                        ORDER BY l.date::DATE desc', (tuple(move_state), tuple(self.ACCOUNT_TYPE), self.date_from, tuple(partner_ids), self.date_from, self.date_from,))
            t = self.cr.fetchall()
            for i in t:
                info.append({'partner_id':i[0],'code':i[4],'dates':i[3],'amt':i[1],'journal':i[5],'part_rec':i[2],'rec_id':i[6]})
                future_past[i[0]] = i[1]
        history = []       
        another=[]
        qwt=[]
        unbal=[]
        add=0.0
        for j in range(6):
            args_list = (tuple(move_state), tuple(self.ACCOUNT_TYPE), tuple(partner_ids),self.date_from,)
            dates_query = '(COALESCE(l.date_maturity,l.date)'
            if form[str(j)]['start'] and form[str(j)]['stop']:
                dates_query += ' BETWEEN %s AND %s)'
                args_list += (form[str(j)]['start'], form[str(j)]['stop'])
            elif form[str(j)]['start']:
                dates_query += ' >= %s)'
                args_list += (form[str(j)]['start'],)
            else:
                dates_query += ' <= %s)'
                args_list += (form[str(j)]['stop'],)
            args_list += (self.date_from,)
            self.cr.execute('''SELECT l.partner_id,SUM(l.debit-l.credit) ,l.reconcile_partial_id
                    FROM account_move_line AS l, account_account, account_move am 
                    WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                        AND (am.state IN %s)
                        AND (account_account.type IN %s)
                        AND (l.partner_id IN %s)
                        AND ((l.reconcile_id IS NULL)
                          OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))
                        AND ''' + self.query + '''
                        AND account_account.active
                        AND ''' + dates_query + '''
                    AND (l.date <= %s)
                    GROUP BY l.partner_id, l.reconcile_partial_id''', args_list)
            partners_partial = self.cr.fetchall()
            partners_amount = dict((i[0],0) for i in partners_partial)
            partnerID=list(i[0] for i in partners_partial)
            chk=[]
            u=[]

            for partner_info in partners_partial:
                if partner_info[2]:
                    # in case of partial reconciliation, we want to keep the left amount in the oldest period
                    self.cr.execute('''SELECT MIN(COALESCE(date_maturity,date)) FROM account_move_line WHERE reconcile_partial_id = %s''', (partner_info[2],))
                    date = self.cr.fetchall()
                    partial = False
                    if 'BETWEEN' in dates_query:
                        partial = date and args_list[-3] <= date[0][0] <= args_list[-2]
                    elif '>=' in dates_query:
                        partial = date and date[0][0] >= form[str(j)]['start']
                    else:
                        partial = date and date[0][0] <= form[str(j)]['stop']
                    if partial:
                        # partial reconcilation
                        limit_date = 'COALESCE(l.date_maturity,l.date) %s %%s' % ('<=' if self.direction_selection == 'past' else '>=',)
                        self.cr.execute('''SELECT l.partner_id,(l.debit-l.credit)
                                           FROM account_move_line AS l, account_move AS am
                                           WHERE l.move_id = am.id AND am.state in %s
                                           AND l.reconcile_partial_id = %s
                                           AND ''' + limit_date, (tuple(move_state), partner_info[2], self.date_from))                                           
                        unreconciled_amount = self.cr.fetchall()
                        self.cr.execute('''SELECT l.partner_id as id ,aj.code as code ,ai.date_invoice as date,(l.debit-l.credit) as amount,l.ref as journal
                                           FROM account_move_line AS l, account_move AS am
                                           JOIN account_journal AS aj ON(aj.id=am.journal_id)
                                           JOIN account_invoice as ai ON (ai.move_id=am.id)
                                           WHERE l.move_id = am.id AND am.state in %s
                                           AND l.reconcile_partial_id = %s
                                           AND ''' + limit_date, (tuple(move_state), partner_info[2], self.date_from))
                        amount = self.cr.dictfetchall()
                        if amount == [] and unreconciled_amount != []:    
                            data = sorted(unreconciled_amount, key=itemgetter(0))   
                            a = {k: list(v) for k, v in groupby(data, key=itemgetter(0))}                    
                            tet=[]
                            count=0.0
                            for i in unreconciled_amount:
                                count+=i[1]
                            for i in info:                                  
                                  if a.has_key(i['partner_id']):
                                      for k in a[i['partner_id']]:
                                          if i['amt']+count > 0:
                                                tet=i  
                            if tet != []:                                 
                               tet['amt']=tet['amt']+count 
                               if tet['code'] == 'SAJ':
                                   info.append(tet)
                        elif amount != []:
                            cnt=0.0
                            for i in unreconciled_amount:
                                cnt+=i[1]
                            amount[0]['amount']= cnt
                            if amount[0]['code'] == 'SAJ':
                                info.append({'partner_id':amount[0]['id'],'code':amount[0]['code'],'dates':amount[0]['date'],'amt':amount[0]['amount'],'journal':amount[0]['journal']})
                        #~ partners_amount[partner_info[0]] += unreconciled_amount[0][0]
                else:                    
                    partners_amount[partner_info[0]] += partner_info[1]
                    args = (tuple(move_state), tuple(self.ACCOUNT_TYPE),self.date_from,)
                    if form[str(j)]['start'] and form[str(j)]['stop']:
                        args += (form[str(j)]['start'], form[str(j)]['stop'])
                    elif form[str(j)]['start']:
                        args += (form[str(j)]['start'],)
                    else:
                        args += (form[str(j)]['stop'],)
                    args += (self.date_from,)
                    args+=(partner_info[0],)
                    self.cr.execute('''SELECT l.partner_id as partner_id,SUM(l.debit-l.credit) as amt, l.date as dates,aj.code as code,l.ref as journal,l.reconcile_id as reconcile,l.reconcile_partial_id as part_id
                                            FROM account_move_line AS l, account_account, account_move am 
                                            JOIN account_journal AS aj ON(aj.id=am.journal_id)
                                            WHERE (l.account_id = account_account.id) AND (l.move_id=am.id)
                                                AND (am.state IN %s)
                                                AND (account_account.type IN %s)
                                                AND ((l.reconcile_id IS NULL)
                                                  OR (l.reconcile_id IN (SELECT recon.id FROM account_move_reconcile AS recon WHERE recon.create_date > %s AND not recon.opening_reconciliation)))
                                                AND ''' + self.query + '''
                                                AND account_account.active
                                                AND ''' + dates_query + '''
                                                AND (l.date <= %s)
                                                AND (l.partner_id = %s)
                                            GROUP BY l.partner_id, l.reconcile_id,l.ref,aj.code,l.date,l.reconcile_partial_id
                                            ORDER BY l.date::DATE desc ''', args)
                    qwerty = self.cr.dictfetchall()
                    for q in qwerty:
                        if q['code']=='SAJ' and q['reconcile'] == None:
                            info.append(q)
                        elif q['code'] != 'SAJ' and q['reconcile'] != None:
                            qwt.append({'id':q['partner_id'],'amt':q['amt'],'recon_id':q['reconcile']})                            
                        elif q['code'] == 'SAJ' and q['reconcile'] != None:
                            unbal.append(q)
                        else:
                            get=[]
                            for i in info:
                                  if i['partner_id'] == q['partner_id']  and q['reconcile'] == None and q['part_id'] == None:
                                       get=i
                                  elif i.has_key('rec_id') and i['partner_id'] == q['partner_id'] and q['part_id'] == None:
                                       if q['reconcile'] == i['rec_id']:
                                            get=i  
                            if get != []:
                                get['amt']=get['amt']+q['amt']
                                if get['code'] == 'SAJ':
                                    info.append(get)

        see = set()
        new_bal = []
        for d in unbal:
            t = tuple(d.items())
            if t not in see:
                see.add(t)
                new_bal.append(d)
        seem = set()
        check_info = []
        for d in info:
            t = tuple(d.items())
            if t not in seem:
                seem.add(t)
                check_info.append(d)  
        r={}
        sss=sorted(qwt,key=itemgetter('recon_id'))
        bal_rec=[]
        for key,value in itertools.groupby(sss,key=itemgetter('id','recon_id')):
            for i in value:
                r.setdefault(key, []).append(i)
        for key,value in r.iteritems():           
            count=0.0
            for i in value:
                 count+=i['amt']
            bal_rec.append({'partner_id':key[0],'recon_id':key[1],'amount':count})  
        new_qwt=[]
        for i in bal_rec:
            count=0.0
            let=[]
            for q in new_bal:
                if q['partner_id']==i['partner_id'] and q['reconcile'] == i['recon_id']:
                    new_qwt.append(q['reconcile'])
                    count=i['amount'] 
                    let=q
                else:
                    info.append(q) 
            if let != []:
                let['amt']= let['amt']+count
                info.append(let)
        if  bal_rec != [] and check_info != []:
            for i in bal_rec:
                count=0.0
                let=[]
                for q in check_info:
                    if q.has_key('rec_id'):
                        if q['partner_id']==i['partner_id'] and q['rec_id'] == i['recon_id']:
                            new_qwt.append(i['recon_id'])
                            q['amt']=q['amt']+i['amount'] 
                            let=q

        seen = set()
        new_l = []
        for d in info:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        journal_list=[]
        for i in new_l:
              journal_list.append(i['journal'])
        journal=list(set(journal_list))
        for i in new_l:
            if i['code'] == 'SAJ':
                  TODAY = datetime.strptime(self.date_from, '%Y-%m-%d')
                  dat=parse(i['dates'])
                  DAY = datetime.strptime(str(dat), '%Y-%m-%d %H:%M:%S')
                  AGE=DAY - TODAY  
                  i['dates']=DAY.strftime('%d-%m-%Y')
                  i.update({'age':abs(AGE.days)+1})
            else:
                  TODAY = datetime.strptime(self.date_from, '%Y-%m-%d')
                  dat=parse(i['dates'])
                  DAY = datetime.strptime(str(dat), '%Y-%m-%d %H:%M:%S')
                  AGE=DAY - TODAY  
                  i['dates']=DAY.strftime('%d-%m-%Y')
                  i.update({'age':abs(AGE.days)+1})
        g={}
        new_g=[]
        lols=sorted(new_l,key=itemgetter('journal'))
        for key,value in itertools.groupby(lols,key=itemgetter('journal')):
            for i in value:
                 g.setdefault(key, []).append(i)
        for i in journal:
            if len(g.get(i)) == 1:
                new_g.append(g.get(i)[0])
            elif  len(g.get(i)) > 1:
                k=[]
                k.append(g.get(i)[0])
                amount=[]
                for h in g.get(i):
                    amount.append(h['amt'])
                k[0]['amt']=min(amount)   
                new_g.append(k[0])
        new=[]
        for i in new_g:
            if int(i['amt']) > 0:
                new.append(i)

        v={}
        lolsss=sorted(new,key=itemgetter('partner_id'))
        for key,value in itertools.groupby(lolsss,key=itemgetter('partner_id')):
            for i in value:
                 v.setdefault(key, []).append(i)
        l1=form['1']['name'].split('-')
        l2=form['2']['name'].split('-')
        l3=form['3']['name'].split('-')        
        l4=form['4']['name'].split('-')        
        l5=form['5']['name'].split('-')
        for key,value in v.iteritems():
              for i in value:
                   if i.has_key('age'):
                       if int(l5[0]) <=  i['age'] <= int(l5[1]):
                           i.update({'0':0.0,'1':0.0,'2':0.0,'3':0.0,'4':0.0,'5':i['amt']})               
                       elif int(l4[0]) <=  i['age'] <= int(l4[1]):
                           i.update({'0':0.0,'1':0.0,'2':0.0,'3':0.0,'4':i['amt'],'5':0.0})
                       elif int(l3[0]) <= i['age'] <= int(l3[1]):
                           i.update({'0':0.0,'1':0.0,'2':0.0,'3':i['amt'],'4':0.0,'5':0.0})
                       elif int(l2[0]) <=  i['age'] <= int(l2[1]):
                           i.update({'0':0.0,'1':0.0,'2':i['amt'],'3':0.0,'4':0.0,'5':0.0})
                       elif int(l1[0]) <= i['age'] <= int(l1[1]):
                           i.update({'0':0.0,'1':i['amt'],'2':0.0,'3':0.0,'4':0.0,'5':0.0})
                       else:  
                           i.update({'0':i['amt'],'1':0.0,'2':0.0,'3':0.0,'4':0.0,'5':0.0})
                   else:
                          TODAY = datetime.strptime(self.date_from, '%Y-%m-%d')
                          dat=parse(i['dates'])
                          DAY = datetime.strptime(str(dat), '%Y-%m-%d %H:%M:%S')
                          AGE=DAY - TODAY  
                          i['dates']=DAY.strftime('%d-%m-%Y')
                          i.update({'age':abs(AGE.days)+1})
                          if int(l5[0]) <=  i['age'] <= int(l5[1]):
                               i.update({'0':0.0,'1':0.0,'2':0.0,'3':0.0,'4':0.0,'5':i['amt']})               
                          elif int(l4[0]) <=  i['age'] <= int(l4[1]):
                               i.update({'0':0.0,'1':0.0,'2':0.0,'3':0.0,'4':i['amt'],'5':0.0})
                          elif int(l3[0]) <= i['age'] <= int(l3[1]):
                               i.update({'0':0.0,'1':0.0,'2':0.0,'3':i['amt'],'4':0.0,'5':0.0})
                          elif int(l2[0]) <=  i['age'] <= int(l2[1]):
                               i.update({'0':0.0,'1':0.0,'2':i['amt'],'3':0.0,'4':0.0,'5':0.0})
                          elif int(l1[0]) <= i['age'] <= int(l1[1]):
                               i.update({'0':0.0,'1':i['amt'],'2':0.0,'3':0.0,'4':0.0,'5':0.0})
                          else:  
                               i.update({'0':i['amt'],'1':0.0,'2':0.0,'3':0.0,'4':0.0,'5':0.0})
                               
        for key,value in v.iteritems():
            ad=[]
            for val in value:
                ad.append(val['amt'])
            v[key].append({'total':sum(ad)})
        result=[]
        for partner in partners:
              values={}
              if v.has_key(partner['id']):   
                  values['name'] = partner['name']  
                  values['city'] = partner['city']  
                  get_total=v[partner['id']].pop()
                  values['total']=get_total['total']
                  values['details'] =  v[partner['id']]
              result.append(values)   
        final=[]
        if form['selection'] == 'sales':
                for k in form['sr_id']:
                    self.cr.execute("""SELECT distinct rp.id as id,rp.name
                                                FROM account_invoice ai 
                                                JOIN res_partner rp ON (rp.id = ai.partner_id) 
                                                JOIN res_company rc ON (rc.id = ai.company_id)
                                                LEFT JOIN res_users ru ON (ru.id = rp.user_id)
                                                WHERE rp.user_id = %s """ %(k))
                    person=self.cr.dictfetchall()
                    person_ids = [x['name'] for x in person]
                    self.cr.execute("""select name,city from res_partner join res_users on res_users.partner_id=res_partner.id where res_users.id=%d"""%(k))
                    s=self.cr.fetchone()
                    final.append({s:person_ids})

        elif form['selection'] == 'team':
            for k in form['manager_id']:
                    self.cr.execute("""SELECT distinct rp.id, rc.name as branch,
                                            rp.name as name,
                                            rp.name as salesperson
                                            FROM account_invoice ai 
                                            JOIN res_partner rp ON (rp.id = ai.partner_id) 
                                            JOIN res_company rc ON (rc.id = ai.company_id)
                                            JOIN crm_case_section css ON (css.id = rp.section_id) JOIN res_users ru ON (ru.id = css.user_id)
                                            WHERE css.user_id = %s """%(k))
                    person=self.cr.dictfetchall()
                    person_ids = [x['name'] for x in person]
                    self.cr.execute("""select name,city from res_partner join res_users on res_users.partner_id=res_partner.id where res_users.id=%d"""%(k))
                    s=self.cr.fetchone()
                    final.append({s:person_ids})
        done=[]
        res=[]
        for r in result:
            if r != {}:
                res.append(r)
        for k in final:
              for key,value in k.iteritems():
                    f=[]
                    for v in res:
                          if v['name'] in value:
                              f.append(v)
                    if f != []:
                        done.append({'person':key[0],'customer':f}) 
        if form['selection'] == 'sales':
            return done
        elif form['selection'] == 'team':
            return done
        elif form['selection'] == 'all':        
            return res
        elif form['selection'] == 'executive':      
            return res             


    def _get_total(self,form):
        h=self._get_lines(form)
        five=[]
        four=[]
        three=[]
        two=[]
        one=[]
        zero=[]
        tot=[]
        for i in h:
             if i.has_key('customer'):
                for key,value in i.iteritems():
                     for val in value:
                           if type(val) == dict:
                                for amt in  val['details']:
                                    five.append(amt['5'])
                                    four.append(amt['4'])
                                    three.append(amt['3'])
                                    two.append(amt['2'])
                                    one.append(amt['1'])
                                    zero.append(amt['0'])
                                    
             else:
                 for key,value in i.iteritems():
                     if type(value) == list:
                         for amt in value:
                                five.append(amt['5'])
                                four.append(amt['4'])
                                three.append(amt['3'])
                                two.append(amt['2'])
                                one.append(amt['1'])
                                zero.append(amt['0'])                                             
        res=[]
        values={}
        values['zero']=sum(zero)
        values['one']=sum(one)
        values['two']=sum(two)
        values['three']=sum(three)
        values['four']=sum(four)
        values['five']=sum(five)
        values['total']=  sum(zero) +  sum(one) + sum(two) +  sum(three) + sum(four) + sum(five)
        res.append(values)  
        return res
class report_fnetagedpartnerbalance(osv.AbstractModel):
    _name = 'report.fnet_new_age.report_fnetagedpartnerbalance'
    _inherit = 'report.abstract_report'
    _template = 'fnet_new_age.report_fnetagedpartnerbalance'
    _wrapped_report_class = fnet_aged_partner_report

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
