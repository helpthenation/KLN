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
from collections import defaultdict
from openerp.tools.translate import _
import logging
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from datetime import *; from dateutil.relativedelta import *
import calendar
from openerp.osv import fields, osv

_logger = logging.getLogger('rdclaim.wizard')

class common_header(object):
    def get_start_period_br(self, data):
        return self._get_info(data, 'period_from', 'account.period')
    def _get_filter(self, data):
        return self._get_form_param('filter', data)
    def get_end_period_br(self, data):
        return self._get_info(data, 'period_to', 'account.period')
    def get_manger_id(self, data):
        return self._get_info(data, 'manager_id', 'res.users')
    def get_prod_categ_id(self, data):
        return self._get_info(data, 'prod_categ_id', 'product.category')
    def get_period_id(self, data):
        return self._get_info(data, 'period_id', 'account.period')
    def get_saleperson_name(self, data):
        stockiest_name= ' '
        stockiest={}
        if data['form']['sr_id'] !=[] and len(data['form']['sr_id'])>1:
            self.cr.execute("""select name from res_partner
                                      join res_users on res_users.partner_id=res_partner.id where res_users.id IN %s"""%(tuple(data['form']['sr_id']),))
            stockiest= self.cr.dictfetchall()
        elif data['form']['sr_id'] !=[] and len(data['form']['sr_id'])  == 1:
            self.cr.execute("""select name from res_partner
                                      join res_users on res_users.partner_id=res_partner.id where res_users.id = %d"""%(data['form']['sr_id'][0]))
            stockiest= self.cr.dictfetchall()
        for i in stockiest:
          stockiest_name+=str(i['name'])+' '
        return  stockiest_name
    def _get_info(self, data, field, model):
        info = data.get('form', {}).get(field)
        if info:
            if type(info) == int:
                return self.pool.get(model).browse(self.cursor, self.uid, info)
            elif type(info) == list:
                return self.pool.get(model).browse(self.cursor, self.uid, info[0])
        return False
    def _get_date_from(self, data):
        return self._get_form_param('date_from', data)

    def _get_date_to(self, data):
        return self._get_form_param('date_to', data)
    def _get_sale_person(self,data):
        return self._get_form_param('sr_id', data)

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default)

    def _get_product_name(self,data):
        if data['form']['type']=='n':
            self.cr.execute("""SELECT DISTINCT
                                          rdl.scheme_qty,
                                         (coalesce(rdl.scheme_price,0.0)) as scheme_price,
                                          (coalesce(rdl.invoice_price,0.0)) as invoice_price,
                                          (coalesce(rdl.mrp_price,0.0)) as mrp_price,
                                          rdl.product_id,
                                          pp.name_template,
                                          pp.default_code,
                                          pt.categ_id
                                          FROM  rd_scheme rds
                                          JOIN  rd_scheme_line rdl  ON rds.id = rdl.scheme_id
                                          JOIN product_template pt ON rds.prod_categ_id = pt.categ_id
                                          JOIN product_product pp ON rdl.product_id = pp.id
                                          WHERE  rds.prod_categ_id=%d and rds.id=%d and pt.company_id=%s
                                          ORDER BY pp.default_code ASC"""%(data['form']['prod_categ_id'][0],data['form']['scheme_id'][0],data['form']['company_id'][0]))
            line_list = [i for i in self.cr.dictfetchall()]
            return line_list
    def _get_sale_entries_product(self,data):
        self.cr.execute("""SELECT DISTINCT
                                      pp.id as product_id,
                                      pp.name_template,
                                      pp.default_code,
                                      pt.categ_id
                                      From
                                      product_template pt
                                      JOIN product_product pp ON pp.product_tmpl_id = pt.id
                                      WHERE pt.categ_id=%d  and pt.company_id=%s
                                      ORDER BY pp.default_code ASC"""%(data['form']['prod_categ_id'][0],data['form']['company_id'][0]))
        line_list = [i for i in self.cr.dictfetchall()]
        return line_list


    def _get_sale_entries_partner_lines(self,data):
        self.cr.execute("""SELECT DISTINCT
                                      pp.id as product_id,
                                      pp.name_template,
                                      pp.default_code,
                                      pt.categ_id
                                      From
                                      product_template pt
                                      JOIN product_product pp ON pp.product_tmpl_id = pt.id
                                      WHERE pt.categ_id=%d  and pt.company_id=%s
                                      ORDER BY pp.default_code ASC"""%(data['form']['prod_categ_id'][0],data['form']['company_id'][0]))
        product_list = self.cr.dictfetchall()
        s=[]
        date_query=""
        if data['form']['date_from'] and data['form']['date_to']:
            date_query=" se.date_from >= '%s' and se.date_from <= '%s' "%(data['form']['date_from'],data['form']['date_to'])
            
        if data['form']['sr_id'] != []:
            for k in data['form']['sr_id']:
                plist=[]
                add=[]
                self.cr.execute("""SELECT DISTINCT
                              res_partner.name,res_partner.city,res_partner.id
                              FROM res_partner
                              JOIN res_users on res_users.id = res_partner.user_id where  res_users.id = %d and res_partner.company_id=%s
                              ORDER BY res_partner.id ASC"""%(k,data['form']['company_id'][0]))
                line_list =  self.cr.dictfetchall()
                self.cr.execute("""select name,city from res_partner join res_users on res_users.partner_id=res_partner.id where res_users.id=%d and res_partner.company_id=%s """%(k,data['form']['company_id'][0]))
                stockiest= self.cr.dictfetchall()
                for j in line_list:
                        print'JJJJJJJJJJJJJJJJJJJJJJJJJ',j
                        print'DATAAAAAAAAAAAAAAAAAAAAAAAA',data['form']
                        total=[]
                        self.cr.execute("""
                            SELECT pp.default_code as code,
                            coalesce(sum(sel.amount),0.0) as quantity,
                            coalesce(sum(sel.current_stock),0.0) as opening,
                            coalesce(sum(sel.sale_stock),0.0) as sale,
                            coalesce(sum(sel.current_stock)-sum(sel.amount),0.0) as closing
                            FROM  sale_entry  se
                            left join sale_entry_line sel on se.id = sel.sale_entry_id
                            left join product_product pp on pp.id = sel.product_id
                            where se.partner_id=%d and se.prod_categ_id=%d and se.company_id=%d and %s
                            group by pp.default_code
                            order by pp.default_code asc
                        
                        """%(j['id'],data['form']['prod_categ_id'][0],data['form']['company_id'][0],date_query))

                        line =  self.cr.dictfetchall()
                        print'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',line
                        self.cr.execute("""
                            SELECT pp.default_code as code,
                            coalesce(sum(sel.amount),0.0) as amount
                            FROM  sale_entry  se
                            left join sale_entry_line sel on se.id = sel.sale_entry_id
                            left join product_product pp on pp.id = sel.product_id
                            where se.partner_id=%d and se.prod_categ_id=%d and se.company_id=%d and %s
                            group by pp.default_code
                            order by pp.default_code asc
                        """%(j['id'],data['form']['prod_categ_id'][0],data['form']['company_id'][0],date_query))
                        amount= self.cr.dictfetchall()
                        if  line == []:
                            res=[]
                            for p in product_list:
                                res.append({
                                                    'code':p['default_code'],
                                                    'quantity':0,
                                                    'opening':0,
                                                    'sale':0,
                                                    'closing':0})
                                add.append({ p['default_code']:0})
                        elif line != []:
                            default=[]
                            res=[]
                            for i in line:
                                default.append(i['code'])
                                add.append({ i['code']:i['quantity']})
                            for p in product_list:
                                if  p['default_code'] not in default:
                                    res.append({
                                                    'code':p['default_code'],
                                                    'quantity':0 ,
                                                    'opening':0,
                                                    'sale':0,                                                    
                                                    'closing':0})
                                    add.append({ p['default_code']:0})
                            res.extend(line)

                        v={}
                        for i in range(len(add)):
                              for key, value in sorted(add[i].iteritems()):
                                    v.setdefault(key, []).append(value)
                        f=[]
                        for key,value in sorted(v.iteritems()):
                              f.append({'sum':sum(value)})


                        if amount != []:
                           amt_total=0
                           for amt in amount:
                               amt_total+=amt['amount']
                           plist.append({'name':j['name'],
                                                'city':j['city'],
                                                'amount':amt_total,
                                                'product_list':sorted(res),
                                                })
                        else:
                            plist.append({'name':j['name'],
                                                'city':j['city'],
                                                'amount':0.0,
                                                'product_list':sorted(res),
                                                })
                        for i in plist:
                              total.append(i['amount'])
                s.append({'saleperson':stockiest[0]['name'],
                                'sp_city':stockiest[0]['city'],
                                 'customer_details':plist,
                                 'add':f,
                                 'total':sum(total) })
        return s
    def _get_partner_lines(self,data):

        self.cr.execute("""SELECT DISTINCT
                                      rdl.scheme_qty,
                                      (coalesce(rdl.scheme_price,0.0)) as scheme_price,
                                      (coalesce(rdl.invoice_price,0.0)) as invoice_price,
                                      (coalesce(rdl.mrp_price,0.0)) as mrp_price,
                                      rdl.product_id,
                                      pp.name_template,
                                      pp.default_code,
                                      pt.categ_id
                                      FROM  rd_scheme rds
                                      JOIN  rd_scheme_line rdl  ON rds.id = rdl.scheme_id
                                      JOIN product_template pt ON rds.prod_categ_id = pt.categ_id
                                      JOIN product_product pp ON rdl.product_id = pp.id
                                      WHERE  rds.prod_categ_id=%d and rds.id=%d and pt.company_id=%s
                                      ORDER BY pp.default_code ASC"""%(data['form']['prod_categ_id'][0],data['form']['scheme_id'][0],data['form']['company_id'][0]))
        product_list = self.cr.dictfetchall()
        s=[]
        if data['form']['sr_id'] != []:
            for k in data['form']['sr_id']:
                plist=[]
                add=[]
                self.cr.execute("""SELECT DISTINCT
                              res_partner.name,res_partner.city,res_partner.id
                              FROM res_partner
                              JOIN res_users on res_users.id = res_partner.user_id where  res_users.id = %d and res_partner.company_id=%s
                              ORDER BY res_partner.id ASC"""%(k,data['form']['company_id'][0]))
                line_list =  self.cr.dictfetchall()
                self.cr.execute("""select name,city from res_partner join res_users on res_users.partner_id=res_partner.id where res_users.id=%d and res_partner.company_id=%s """%(k,data['form']['company_id'][0]))
                stockiest= self.cr.dictfetchall()
                for j in line_list:
                        total=[]
                        self.cr.execute("""SELECT DISTINCT
                        (coalesce(set.amount,0)) as quantity,
                        pp.default_code as code
                        FROM  scheme_entry_total  set
                        join sale_entry se on se.partner_id=set.partner_id
                        join product_template pt  on set.prod_categ_id = pt.categ_id
                        join product_product pp  on (pp.product_tmpl_id = pt.id and set.product_id = pp.id)
                        where set.partner_id=%d and set.prod_categ_id=%d and set.scheme_id = %d and pt.company_id=%s
                        """%(j['id'],data['form']['prod_categ_id'][0],data['form']['scheme_id'][0],data['form']['company_id'][0]))
                        line =  self.cr.dictfetchall()
                        self.cr.execute(""" SELECT DISTINCT
                        (coalesce(set.total,0.0)) as amount  ,
                        pp.default_code as code
                        FROM  scheme_entry_total  set
                        join sale_entry se on se.partner_id=set.partner_id
                        join product_template pt  on set.prod_categ_id = pt.categ_id
                        join product_product pp  on (pp.product_tmpl_id = pt.id and set.product_id = pp.id)
                        where set.partner_id=%d and set.prod_categ_id=%d  and set.scheme_id = %d and pt.company_id=%s
                        """%(j['id'],data['form']['prod_categ_id'][0],data['form']['scheme_id'][0],data['form']['company_id'][0]))
                        amount= self.cr.dictfetchall()
                        if  line == []:
                            res=[]
                            for p in product_list:
                                res.append({
                                                    'code':p['default_code'],
                                                    'quantity':0})
                                add.append({ p['default_code']:0})
                        elif line != []:
                            default=[]
                            res=[]
                            for i in line:
                                default.append(i['code'])
                                add.append({ i['code']:i['quantity']})
                            for p in product_list:
                                if  p['default_code'] not in default:
                                    res.append({
                                                    'code':p['default_code'],
                                                    'quantity':0 })
                                    add.append({ p['default_code']:0})
                            res.extend(line)

                        v={}
                        for i in range(len(add)):
                              for key, value in sorted(add[i].iteritems()):
                                    v.setdefault(key, []).append(value)
                        f=[]
                        for key,value in sorted(v.iteritems()):
                              f.append({'sum':sum(value)})


                        if amount != []:
                           amt_total=0
                           for amt in amount:
                               amt_total+=amt['amount']
                           plist.append({'name':j['name'],
                                                'city':j['city'],
                                                'amount':amt_total,
                                                'product_list':sorted(res),
                                                })
                        else:
                            plist.append({'name':j['name'],
                                                'city':j['city'],
                                                'amount':0.0,
                                                'product_list':sorted(res),
                                                })
                        for i in plist:
                              total.append(i['amount'])
                s.append({'saleperson':stockiest[0]['name'],
                                'sp_city':stockiest[0]['city'],
                                 'customer_details':plist,
                                 'add':f,
                                 'total':sum(total) })
        return s
    def _get_sale_entries_categ_name(self,data):
        self.cr.execute("""SELECT DISTINCT
                                  pc.id,
                                  pc.name
                                  FROM product_category pc
                                  where pc.company_id=%d
                                  ORDER BY pc.name ASC"""%(data['form']['company_id'][0]))
        categ_list=self.cr.dictfetchall()
        print'CATEGGGGGGGGGGGGGGGGGGGGGGGGGGGGG',categ_list
        return  categ_list
    def _get_categ_name(self,data):
        self.cr.execute("""SELECT DISTINCT
                                  pc.id,
                                  pc.name
                                  FROM scheme_entry_total so JOIN product_category pc ON(pc.id = so.prod_categ_id)
                                  where pc.company_id=%d
                                  ORDER BY pc.name ASC"""%(data['form']['company_id'][0]))
        categ_list=self.cr.dictfetchall()
        return  categ_list
    def _get_consolidate_data(self,data):
        self.cr.execute("""SELECT DISTINCT
                                  pc.id,
                                  pc.name
                                  FROM scheme_entry_total so JOIN product_category pc ON(pc.id = so.prod_categ_id)
                                  where pc.company_id=%d
                                  ORDER BY pc.name"""%(data['form']['company_id'][0]))
        categ_list=self.cr.dictfetchall()
        s=[]
        if data['form']['sr_id'] != []:
            for k in data['form']['sr_id']:
                plist=[]
                add=[]
                self.cr.execute("""SELECT DISTINCT
                              res_partner.name,res_partner.city,res_partner.id
                              FROM res_partner
                              JOIN res_users on res_users.id = res_partner.user_id where  res_users.id = %d and res_partner.company_id = %s
                              ORDER BY res_partner.id ASC"""%(k,data['form']['company_id'][0]))
                line_list =  self.cr.dictfetchall()
                self.cr.execute("""select name,city from res_partner join res_users on res_users.partner_id=res_partner.id
                where res_users.id=%d and res_partner.company_id = %s """%(k,data['form']['company_id'][0]))
                stockiest= self.cr.dictfetchall()
                for j in line_list:
                        total=[]
                        amt=[]
                        tot=[]
                        for i in categ_list:
                            if data['form']['filter']== 'filter_period':
                                period=[]
                                for pop in range(data['form']['period_from'][0],data['form']['period_to'][0]+1):
                                    period.append(pop)
                                if len(period) == 1:
                                    rep='('+str(period[0])+')'
                                elif len(period) > 1:
                                    rep=str(tuple(period))
                                self.cr.execute("""SELECT DISTINCT
                                (coalesce(set.amount,0)) as quantity,
                                pp.default_code as code
                                FROM  scheme_entry_total  set
                                join sale_entry se on se.partner_id=set.partner_id
                                join product_template pt  on set.prod_categ_id = pt.categ_id
                                join product_product pp  on (pp.product_tmpl_id = pt.id and set.product_id = pp.id)
                                where set.partner_id=%d and set.prod_categ_id=%d and set.period_id in %s and pt.company_id=%s
                                """%(j['id'],i['id'],rep,data['form']['company_id'][0]))
                                line =  self.cr.dictfetchall()
                                self.cr.execute("""SELECT DISTINCT
                                coalesce(set.total,0.0) as amount ,pp.default_code as code
                                FROM  scheme_entry_total  set
                                join sale_entry se on se.partner_id=set.partner_id
                                join product_template pt  on set.prod_categ_id = pt.categ_id
                                join product_product pp  on (pp.product_tmpl_id = pt.id and set.product_id = pp.id)
                                where set.partner_id=%d and set.prod_categ_id=%d and set.period_id in %s and pt.company_id = %s
                                """%(j['id'],i['id'],rep,data['form']['company_id'][0]))
                                amtt =  self.cr.dictfetchall()
                            elif data['form']['filter']== 'filter_date':
                                self.cr.execute(""" SELECT DISTINCT sae.id,
                                      coalesce(sel.amount,0) as quantity,
                                      pp.default_code as code
                                FROM scheme_entry se
                                JOIN account_period ap ON (ap.id = se.period_id)
                                JOIN sale_entry sae ON (se.prod_categ_id = sae.prod_categ_id AND se.sr_id = sae.sr_id AND se.partner_id = sae.partner_id)
                                JOIN sale_entry_line sel ON (sel.sale_entry_id = sae.id)
                                 join rd_scheme rd on rd.id = se.scheme_id
                                 join rd_scheme_line rdl on rdl.scheme_id=rd.id and rdl.product_id=sel.product_id
                                 join product_template pt  on se.prod_categ_id = pt.categ_id
                                join product_product pp  on (pp.product_tmpl_id = pt.id and sel.product_id = pp.id)
                                WHERE sae.date_from >='%s' and sae.date_from <='%s' and sel.amount != 0.0 and se.partner_id=%d
                                and sae.prod_categ_id=%d  and pt.company_id=%s
                                 """%(data['form']['date_from'],data['form']['date_to'],j['id'],i['id'],data['form']['company_id'][0]))
                                line =  self.cr.dictfetchall()
                                self.cr.execute("""SELECT DISTINCT sae.id,
                                            coalesce((sel.amount)*rdl.scheme_price,0.0) as amount,
                                            pp.default_code as code,
                                            rdl.scheme_price
                                            FROM scheme_entry se
                                            JOIN account_period ap ON (ap.id = se.period_id)
                                            JOIN sale_entry sae ON (se.prod_categ_id = sae.prod_categ_id AND se.sr_id = sae.sr_id
                                             AND se.partner_id = sae.partner_id and ap.date_start <=sae.date_from AND ap.date_stop >=sae.date_from)
                                            JOIN sale_entry_line sel ON (sel.sale_entry_id = sae.id)
                                            join rd_scheme rd on rd.id = se.scheme_id and rd.period_id = se.period_id
                                            join rd_scheme_line rdl on rdl.scheme_id=rd.id and rdl.product_id=sel.product_id
                                            join product_template pt  on se.prod_categ_id = pt.categ_id
                                            join product_product pp  on (pp.product_tmpl_id = pt.id and sel.product_id = pp.id)
                                            WHERE sae.date_from >='%s' and sae.date_from <='%s'
                                             and sel.amount != 0.0 and se.partner_id=%d and sae.prod_categ_id=%d and pt.company_id=%s
                                             order by rdl.scheme_price
                                """%(data['form']['date_from'],data['form']['date_to'],j['id'],i['id'],data['form']['company_id'][0]))
                                amtt= self.cr.dictfetchall()
                            else:
                                self.cr.execute("""SELECT DISTINCT
                                (coalesce(set.amount,0)) as quantity,
                                set.period_id,
                                pp.default_code as code
                                FROM  scheme_entry_total  set
                                join sale_entry se on se.partner_id=set.partner_id
                                join product_template pt  on set.prod_categ_id = pt.categ_id
                                join product_product pp  on (pp.product_tmpl_id = pt.id and set.product_id = pp.id)
                                where set.partner_id=%d and set.prod_categ_id=%d  and pt.company_id=%s
                                """%(j['id'],i['id'],data['form']['company_id'][0]))
                                line =  self.cr.dictfetchall()
                                self.cr.execute("""SELECT DISTINCT
                                set.period_id,
                                coalesce(set.total,0) as amount ,
                                pp.default_code as code
                                FROM  scheme_entry_total  set
                                join sale_entry se on se.partner_id=set.partner_id
                                join product_template pt  on set.prod_categ_id = pt.categ_id
                                join product_product pp  on (pp.product_tmpl_id = pt.id and set.product_id = pp.id)
                                where set.partner_id=%d and set.prod_categ_id=%d  and pt.company_id = %s
                                """%(j['id'],i['id'],data['form']['company_id'][0]))
                                amtt =  self.cr.dictfetchall()
                            if line != []:
                                if len(line) > 1:
                                    count=[]
                                    for pp in line:
                                          count.append(pp['quantity'])
                                    add.append({i['name']:sum(count)})
                                    total.append({'qty':sum(count)})
                                elif len(line)==1:
                                    add.append({i['name']:line[0]['quantity']})
                                    total.append({'qty':line[0]['quantity']})
                            elif line ==[]:
                                add.append({i['name']:0})
                                total.append({'qty':0})
                            if amtt != []:
                                if len(amtt)==1:
                                    amt.append(amtt[0]['amount'])
                                elif len(amtt) > 1:
                                    ad=[]
                                    for i in amtt:
                                        ad.append(i['amount'])
                                    amt.append(sum(ad))

                            elif amtt ==[]:
                                amt.append(0)
                        v={}
                        for i in range(len(add)):
                            for key, value in sorted(add[i].iteritems()):
                                v.setdefault(key, []).append(value)
                        f=[]
                        for key,value in sorted(v.iteritems()):
                             f.append({'categ_name':key,'sum':sum(value)})
                        plist.append({'name':j['name'],'city':j['city'],'prod':total,'amount':sum(amt)})
                        for i in plist:
                              tot.append(i['amount'])
                s.append({'saleperson':stockiest[0]['name'],
                                'sp_city':stockiest[0]['city'],
                                 'customer_details':plist,
                                 'categ_count':sorted(f),
                                 'total':sum(tot)
                                  })
        return s
    def _get_spa_header_data(self,data):
        code=data['form']['period_id'][1]
        self.cr.execute("""SELECT DISTINCT ON (pp.id)
                                          (coalesce(rdl.invoice_price,0.0)) as invoice_price,
                                          (coalesce(rdl.mrp_price,0.0)) as mrp_price,
                                          pp.id as product_id,
                                          pp.name_template,
                                          pp.default_code,
                                          pt.case_qty,
                                          pt.list_price as price,
                                          pt.categ_id
                                          FROM  rd_scheme rds
                                          JOIN  rd_scheme_line rdl  ON rds.id = rdl.scheme_id
                                          JOIN account_period ap ON rds.period_id = ap.id
                                          JOIN product_template pt ON rds.prod_categ_id = pt.categ_id
                                          JOIN product_product pp ON rdl.product_id = pp.id and pp.product_tmpl_id = pt.id
                                          WHERE  pt.categ_id=%d and ap.code = '%s' and pt.company_id=%s
                                          ORDER BY pp.id ASC"""%(data['form']['prod_categ_id'][0],code,data['form']['company_id'][0]))
        line_list = [i for i in self.cr.dictfetchall()]
        if line_list == []:
            raise osv.except_osv(_('Error!'), _('There Is No Data For Selected Period!'))
        return line_list
    def _get_month(self,data):
        TODAY = datetime.strptime(data['form']['period_id'][1], '%m/%Y')
        code=TODAY.strftime('%m/%Y')
        thismonth=TODAY.strftime('%b-%y')
        LY=TODAY+relativedelta(years=-1)
        #last_yr = THIS MONTH LAST YEAR
        last_yr=LY.strftime('%m/%Y')
        LM = TODAY - relativedelta(months=1)
        last_month=LM.strftime('%m/%Y')
        lastmonth=LY.strftime('%b-%y')
        thismonth=TODAY.strftime('%b-%y')
        last='LY-'+str(lastmonth)
        this=str(thismonth)+ '  Month.Plan'
        res=[]
        res.append({'this':this,'last':last})
        return res

    def _get_stockiest_line(self,data):
        self.cr.execute("""DROP VIEW IF EXISTS stock_views CASCADE  """)
        TODAY = datetime.strptime(data['form']['period_id'][1], '%m/%Y')
        code=TODAY.strftime('%m/%Y')
        month=TODAY.strftime('%m')
        year=TODAY.strftime('%Y')
        p=self.pool.get('account.period')
        period_id=p.search(self.cursor, self.uid,[('code' ,'=', code),('company_id','=',data['form']['company_id'][0])])
        period=p.browse(self.cursor, self.uid,period_id[0])
        thismonth=TODAY.strftime('%B')
        LY=TODAY+relativedelta(years=-1)
        last_yr=LY.strftime('%m/%Y')
        lastmonth=LY.strftime('%b-%y')
        thismonth=TODAY.strftime('%b-%y')
        LM = TODAY - relativedelta(months=1)
        last_month=LM.strftime('%m/%Y')
        head=self._get_spa_header_data(data)
        ss=[]
        if   data['form']['stockiest_ids'] != []:
            for i in data['form']['stockiest_ids']:
                    slist=[]
                    awt=[]
                    prod = self.pool.get('res.partner').browse(self.cursor, self.uid,i)
                    self.cr.execute("""
                                            SELECT  DISTINCT
                                            coalesce(stl.amount,0) as amount,
                                            coalesce(stl.amount,0) * pt.list_price as val,
                                            pp.id,
                                            stl.product_id as product_id
                                            FROM
                                            sale_target st
                                            JOIN  sale_target_line stl ON (stl.sale_target_id = st.id)
                                            JOIN account_period ap ON (st.period_id = ap.id)
                                            JOIN product_template pt ON st.prod_categ_id = pt.categ_id
                                            JOIN product_product pp ON stl.product_id = pp.id and pp.product_tmpl_id = pt.id
                                            WHERE ap.code='%s' and st.prod_categ_id=%d and st.partner_id = %d and pt.company_id=%s
                                             ORDER BY pp.id ASC"""%(code,data['form']['prod_categ_id'][0],i,data['form']['company_id'][0]))
                    TY_list = [j for j in self.cr.dictfetchall()]
                    self.cr.execute("""
                                            SELECT  DISTINCT
                                            coalesce(stl.amount,0) as amount,
                                            coalesce(stl.amount,0) * pt.list_price as val,
                                            pp.id,
                                            stl.product_id as product_id
                                            FROM
                                            sale_target st
                                            JOIN  sale_target_line stl ON (stl.sale_target_id = st.id)
                                            JOIN account_period ap ON (st.period_id = ap.id)
                                            JOIN product_template pt ON st.prod_categ_id = pt.categ_id
                                            JOIN product_product pp ON stl.product_id = pp.id and pp.product_tmpl_id = pt.id
                                            WHERE ap.code='%s' and st.prod_categ_id=%d and st.partner_id = %d and pt.company_id=%s
                                             ORDER BY pp.id ASC"""%(last_yr,data['form']['prod_categ_id'][0],i,data['form']['company_id'][0]))
                    LY_list = [k for k in self.cr.dictfetchall()]
                    self.cr.execute("""SELECT
                                            distinct on (pp.id)
                                            (sel.current_stock) as amount,
                                            coalesce(sel.current_stock,0) * pt.list_price as val,
                                            sel.product_id as product_id,
                                            pp.id

                                            FROM scheme_entry se
                                            JOIN account_period ap ON (ap.id = se.period_id)
                                            JOIN sale_entry sae ON (se.prod_categ_id = sae.prod_categ_id AND se.sr_id = sae.sr_id AND se.partner_id = sae.partner_id)
                                            JOIN sale_entry_line sel ON (sel.sale_entry_id = sae.id )

                                            JOIN product_template pt ON sae.prod_categ_id = pt.categ_id
                                            JOIN product_product pp ON sel.product_id = pp.id and pp.product_tmpl_id = pt.id
                                            WHERE sae.date_from >= '%s' AND sae.date_from <= '%s'  and ap.code='%s' and se.partner_id=%d
                                            AND se.prod_categ_id = %d and pt.company_id=%s
                                            And sae.id = (select min(sale_entry.id) from sale_entry
                                             join sale_entry_line sel ON (sel.sale_entry_id = sale_entry.id )  where date_from >= '%s' AND date_from <= '%s'  and  sel.current_stock != 0 and prod_categ_id = %d and partner_id=%d)
                                            GROUP BY sel.current_stock,sae.date_from,pp.id,sel.product_id,pt.list_price
                                            order by pp.id asc
                                            """%(period.date_start,period.date_stop,code,i,data['form']['prod_categ_id'][0],data['form']['company_id'][0],period.date_start,period.date_stop,data['form']['prod_categ_id'][0],i))
                    stock_open=[s for s in self.cr.dictfetchall()]
                    self.cr.execute(""" SELECT DISTINCT
                                                coalesce(set.amount, 0) as amount,
                                                coalesce(set.amount, 0) * pt.list_price as val,
                                                set.product_id as product_id,
                                                pp.id
                                                FROM
                                                scheme_entry_total set
                                                JOIN account_period ap ON set.period_id = ap.id
                                                JOIN product_template pt ON set.prod_categ_id = pt.categ_id
                                                JOIN product_product pp ON set.product_id = pp.id and pp.product_tmpl_id = pt.id
                                                WHERE set.prod_categ_id=%d and set.partner_id = %d and ap.code='%s' and pt.company_id=%s
                                                GROUP BY set.product_id,pp.id,set.amount,pt.list_price
                                                ORDER BY pp.id ASC"""%(data['form']['prod_categ_id'][0],i,code,data['form']['company_id'][0]))
                    rd_tm =[r for r in self.cr.dictfetchall()]
                    self.cr.execute(""" SELECT DISTINCT
                                               coalesce(set.amount, 0) as amount,
                                               coalesce(set.amount, 0) * pt.list_price as val,
                                                set.product_id as product_id,
                                                pp.id
                                                FROM
                                                scheme_entry_total set
                                                JOIN account_period ap ON set.period_id = ap.id
                                                JOIN product_template pt ON set.prod_categ_id = pt.categ_id
                                                JOIN product_product pp ON set.product_id = pp.id and pp.product_tmpl_id = pt.id
                                                WHERE set.prod_categ_id=%d and set.partner_id = %d and ap.code='%s' and pt.company_id=%s
                                                 GROUP BY pp.id,pt.list_price,set.amount,set.product_id
                                                 ORDER BY pp.id ASC"""%(data['form']['prod_categ_id'][0],i,last_month,data['form']['company_id'][0]))
                    rd_lm=[l for l in self.cr.dictfetchall()]
                    self.cr.execute(""" CREATE or REPLACE VIEW stock_views as( SELECT DISTINCT  sm.id,sm.partner_id,coalesce(sm.origin_returned_move_id,0) as return_id,sm.product_id as product_id ,sm.product_qty as ordered_qty,
                                                (select coalesce(product_qty,0) from stock_move where id=sm.origin_returned_move_id) as returned_qty,so.prod_categ_id as categ_id
                                                FROM stock_picking sp
                                                LEFT JOIN stock_move sm
                                                ON sp.id = sm.picking_id
                                                LEFT JOIN procurement_order po
                                                ON sm.procurement_id = po.id
                                                LEFT JOIN sale_order_line sol
                                                ON po.sale_line_id = sol.id
                                                LEFT JOIN sale_order so
                                                ON sol.order_id = so.id
                                                LEFT JOIN stock_transfer_details std
                                                ON std.picking_id=sm.picking_id
                                                LEFT JOIN stock_transfer_details_items stdi
                                                ON stdi.transfer_id=std.id
                                                where  so.partner_id = %d and
                                                sm.id not in ( select srpl.move_id from stock_return_picking_line
                                                srpl join stock_return_picking srp on srpl.wizard_id = srp.id
                                                )
                                                and EXTRACT(MONTH FROM sm.date) = %s and EXTRACT(year FROM sm.date) = %s
                                                and so.prod_categ_id=%d  and so.company_id=%d)
                                               """%(i,month,year,data['form']['prod_categ_id'][0],data['form']['company_id'][0]))
                    self.cr.execute(""" select * from stock_views """)
                    line_list = [wow for wow in self.cr.dictfetchall()]
                    self.cr.execute(""" CREATE or REPLACE VIEW stock_qtys as   (
                                select case
                                when return_id = 0 then ordered_qty
                                when  return_id > 0 then returned_qty - ordered_qty
                                end as "qty" , product_id,partner_id,categ_id from stock_views
                                )""")
                    self.cr.execute(""" select * from stock_qtys  """)
                    line_list = [wo for wo  in self.cr.dictfetchall()]
                    self.cr.execute(""" select sum(qty) as amount,product_id from stock_qtys where partner_id = %d and product_id in (select distinct product_id from stock_views)  group by product_id order by product_id"""%(i))
                    awd=[a for a in self.cr.dictfetchall()]
                    if TY_list == []:
                        for h in head:
                              TY_list.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    if LY_list == []:
                        for h in head:
                              LY_list.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    if stock_open == []:
                        for h in head:
                              stock_open.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    elif stock_open !=[]:
                        product_list=[]
                        for r in stock_open:
                            product_list.append(r['product_id'])
                        for h in head:
                            if h['product_id'] not in product_list:
                                stock_open.append({'amount':0,'product_id':h['product_id'],'val':h['price']})

                    if rd_tm == []:
                        for h in head:
                              rd_tm.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    elif rd_tm !=[]:
                        product_list=[]
                        for r in rd_tm:
                            product_list.append(r['product_id'])
                        for h in head:
                            if h['product_id'] not in product_list:
                                rd_tm.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    if rd_lm == []:
                        for h in head:
                              rd_lm.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    elif rd_lm !=[]:
                        product_list=[]
                        for r in rd_lm:
                            product_list.append(r['product_id'])
                        for h in head:
                            if h['product_id'] not in product_list:
                                rd_lm.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    if awd == []:
                        for h in head:
                              awd.append({'amount':0,'product_id':h['product_id'],'val':h['price']})
                    elif awd !=[]:
                        product_list=[]
                        for r in awd:
                            product_list.append(r['product_id'])
                        for h in range(len(head)):
                            if head[h]['product_id'] not in product_list:
                                 awd.append({'amount':0,'product_id':head[h]['product_id']})
                    for ink in range(len(head)):
                         awd[ink].update({'val':head[ink]['price']})
                    vs=[]
                    close=[]
                    rdtmlist = sorted(rd_tm, key=lambda k: k['product_id'])
                    rdlmlist = sorted(rd_lm, key=lambda k: k['product_id'])
                    awdlist = sorted(awd, key=lambda k: k['product_id'])
                    for w in range(len(head)):
                        soc=stock_open[w]['amount']+awdlist[w]['amount']-rdtmlist[w]['amount']
                        close.append({'amount':soc,'id':w,'val':head[w]['price'],'product_id':head[w]['product_id']})
                        if rdlmlist[w]['amount']  > 0:
                            cent=(float(rdtmlist[w]['amount'])/float(rdlmlist[w]['amount'])*100)
                            vs.append({'id':w,'amount':cent,'val':head[w]['price']})
                        else:
                            vs.append({'id':w,'amount':0,'val':head[w]['price']})
                    closelist = sorted(close, key=lambda k: k['product_id'])
                    slist.append({'lastyr':LY_list ,'thisyr': TY_list,'saleopen': stock_open,'rdthis':rdtmlist,'rdlast':rdlmlist,'percentage':vs,'awd':awdlist,'closing':closelist})
                    ss.append({'name':prod.name,'lines':slist})
        return ss
