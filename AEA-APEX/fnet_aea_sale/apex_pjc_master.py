
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
from datetime import datetime, timedelta
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import time
import calendar,datetime
from openerp.tools.translate import _
import collections
from datetime import date, timedelta as td
import datetime

from lxml import etree

class pjc_target(osv.osv):

    _name = 'pjc.target'

    def _balance_days(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'balance': 0.0
            }
            val = order.total_days - order.mandays_alloted
            res[order.id] = val
        return res

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False  

    _columns = {
          'name': fields.char('Name', size=64),
          'period_id': fields.many2one('account.period', 'Period', required=True),
          'manager_id': fields.many2one('res.users', 'Sales Manager', required=True),
          'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
          'company_id': fields.many2one('res.company', 'Company'),
          'mandays_alloted': fields.float('Mandays Alloted'),
          'route_local': fields.float('Route Local'),
          'route_val': fields.float('Route Van'),
          'local_ws': fields.float('Local WS'),
          'local_retail': fields.float('Local Retail'),
          'van_ws': fields.float('Van WS'),
          'van_retail': fields.float('Van Retail'),
          'total_days': fields.float('Total Days', readonly=True),
          'no_of_call': fields.float('No of Calls', required=True),
          'balance': fields.function(_balance_days, string='Balance Days', digits_compute= dp.get_precision('Discount')),
          'partner_id':fields.many2one('res.partner', 'Customer', required=True),
          'state': fields.selection([('draft', 'submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
           }

    _defaults = {
        'state':'draft',
        'company_id': _get_default_company,
        'manager_id': lambda obj, cr, uid, context: uid,
        'total_days':24.00,
        'period_id':_get_period,
        'no_of_call':45.00
        }

    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if manager_id:
            cr.execute("""select
                                smr.member_id as mem_id
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['mem_id'])
        domain = {'sr_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    def onchange_period_id(self, cr, uid, ids, period_id,company_id,context=None):
        result = {}
        list_of_date=[]
        if period_id:
            period = self.pool.get('account.period').browse(cr, uid, period_id)
            da = str(period.date_start).split("-")
            lastday1=calendar.monthrange(int(da[0]),int(da[1]))
            end=datetime.date(int(da[0]),int(da[1]),lastday1[1])
            start = period.date_start
            year_f, month_f, day_f = (int(x) for x in str(start).split('-'))
            year_t, month_t, day_t = (int(x) for x in str(end).split('-'))
            d1 = date(year_f, month_f, day_f)
            d2 = date(year_t, month_t, day_t)
            delta = d2 - d1
            for i in range(delta.days + 1):
                dd =  d1 + td(days=i)
                year, month, day = (int(x) for x in str(dd).split('-'))
                ans = datetime.date(year, month, day)
                list_of_date.append({"date":ans})
            result['value'] = {'pjc_call_line':list_of_date}
        return result
        
    def submit(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        pjc_sr = self.search(cr, uid, [('sr_id','=',obj.sr_id.id),('partner_id','=',obj.partner_id.id),('period_id','=',obj.period_id.id),('id','!=',obj.id)], context=context)
        if pjc_sr:
            raise osv.except_osv(_('Invalid Action!'), _('Already this entry submitted!'))
        elif obj.mandays_alloted <> obj.route_local + obj.route_val:
            raise osv.except_osv(_('Error!'), _('No of route values is wrong'))
        elif obj.route_local <>  obj.local_ws + obj.local_retail:
            raise osv.except_osv(_('Error!'), _('Local values is wrong'))
        elif obj.route_val <> obj.van_ws + obj.van_retail:
            raise osv.except_osv(_('Error!'), _('Van values is wrong'))
        else:
            self.write(cr, uid, ids, {'total_days':24.00,'mandays':obj.mandays_alloted},context=context)
            if obj.total_days < obj.mandays_alloted:
                raise osv.except_osv(_('Error!'), _('Mandays alloted is exceed'))
            else:
                val = obj.partner_id.name +'_'+ obj.period_id.name 
                self.write(cr, uid, ids, {'state':'done','name':val}, context=context)
pjc_target()

class pjc_items(osv.osv):

    _name = 'pjc.items'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False  

    _columns = {

          'period_id': fields.many2one('account.period', 'Period', required=True),
          'manager_id': fields.many2one('res.users', 'Sales Manager', required=True),
          'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
          'company_id': fields.many2one('res.company', 'Company'),
          'partner_id':fields.many2one('res.partner', 'Customer', required=True),
          'target_id':fields.many2one('pjc.target', 'Target Days', readonly=True),
          'prod_categ_id': fields.many2one('product.category', 'Product Category', required=True, track_visibility='always'),
          'state': fields.selection([('draft', 'submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
          'pjc_target_line':fields.one2many('pjc.target.line', 'pjc_id', 'PJC Line'),
           }

    _defaults = {
        'state':'draft',
        'company_id': _get_default_company,
        'manager_id': lambda obj, cr, uid, context: uid,
        'total_days':24.00,
        'period_id':_get_period,
        }

    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id,context=None):
        domain = {}
        result = {}
        list_li=[]
        if manager_id:
            cr.execute("""select
                                smr.member_id as mem_id
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_li.append(fid['mem_id'])
        domain = {'sr_id':[('id', 'in', tuple(list_li))]}
        result['domain']=domain
        return result
        
    def onchange_prod_categ_id(self, cr, uid, ids, prod_categ_id, company_id, period_id, context=None):
        result = {}
        list_of_dict=[]
        list_of_date=[]
        if prod_categ_id:
            cate = self.pool.get('product.category').browse(cr, uid, prod_categ_id)
            cr.execute("""select 
                              pp.id as prod,
                              pt.uom_id as uom,
                              pt.list_price as sale_pr,
                              pt.mrp_price as mrp 
                        from product_template pt
                        join product_product pp on (pp.product_tmpl_id = pt.id)
                        where pt.categ_id = '%s' and pt.company_id = '%s' and pt.type != 'service'
                            order by 2 """ % (prod_categ_id, cate.company_id.id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"product_id":fid['prod']})
            result['value'] = {'pjc_target_line':list_of_dict}
        return result

    def submit(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        pjc_sr = self.search(cr, uid, [('sr_id','=',obj.sr_id.id),('partner_id','=',obj.partner_id.id),('period_id','=',obj.period_id.id),('id','!=',obj.id),('prod_categ_id','=',obj.prod_categ_id.id)], context=context)
        if pjc_sr:
            raise osv.except_osv(_('Invalid Action!'), _('Already this entry submitted!'))
        else:
             pjc_sr = self.pool.get('pjc.target').search(cr, uid, [('sr_id','=',obj.sr_id.id),('partner_id','=',obj.partner_id.id),('period_id','=',obj.period_id.id)], context=context)
             self.write(cr, uid, ids, {'state':'done','target_id':pjc_sr[0]}, context=context)
    
pjc_items()

class pjc_target_line(osv.osv):
    _name = 'pjc.target.line'

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {
    'pjc_id':fields.many2one('pjc.items', 'PJC Target Items'),
    'product_id': fields.many2one('product.product', 'Product', required=True),
    'value':fields.float('Quantity'),
    'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'company_id': _get_default_company,
        }
pjc_target_line()


class pjc_entry(osv.osv):
    _name = 'pjc.entry'
    
    def _balance_days(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'balance': 0.0
            }
            val = 0.0
            res[order.id] = val
        return res


    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id

    _columns = {

          'from_date': fields.date('Date'),
          'period_id':fields.many2one('account.period', 'Period', readonly=True),
          'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
          'partner_id': fields.many2one('res.partner', 'Stokiest', required=True),
          'city':fields.char('Town', size=30),
          'company_id': fields.many2one('res.company', 'Company'),
          'act_mandays_alloted': fields.float('Mandays Alloted', readonly=True),
          'act_route_local': fields.float('Route Local', readonly=True),
          'act_route_val': fields.float('Route Van', readonly=True),
          'act_local_ws': fields.float('Local WS', readonly=True),
          'act_local_retail': fields.float('Local Retail', readonly=True),
          'act_van_ws': fields.float('Van WS', readonly=True),
          'act_van_retail': fields.float('Van Retail', readonly=True),
          'no_of_call': fields.float('No of Call', readonly=True),
          'tdt_manday_type': fields.selection([('full', 'Full Day'),('half', 'Half Day')],'Working Day', required=True),
          'tdt_route_type': fields.selection([('local', 'Local'),('van', 'Van')],'Route', required=True),
          'tdt_local_ws': fields.boolean('Local WS'),
          'tdt_local_retail': fields.boolean('Local Retail'),
          'tdt_van_ws': fields.boolean('Van WS'),
          'tdt_van_retail': fields.boolean('Van Retail'),
          'tdt_of_call': fields.float('No of Call', required=True),
          'bal_mandays_alloted': fields.float('Mandays Alloted', readonly=True),
          'bal_route_local': fields.float('Route Local', readonly=True),
          'bal_route_val': fields.float('Route Van', readonly=True),
          'bal_local_ws': fields.float('Local WS', readonly=True),
          'bal_local_retail': fields.float('Local Retail', readonly=True),
          'bal_van_ws': fields.float('Van WS', readonly=True),
          'bal_van_retail': fields.float('Van Retail', readonly=True),
          'dal_mandays_alloted': fields.float('Mandays Alloted', readonly=True),
          'dal_route_local': fields.float('Route Local', readonly=True),
          'dal_route_val': fields.float('Route Van', readonly=True),
          'dal_local_ws': fields.float('Local WS', readonly=True),
          'dal_local_retail': fields.float('Local Retail', readonly=True),
          'dal_van_ws': fields.float('Van WS', readonly=True),
          'dal_van_retail': fields.float('Van Retail', readonly=True),
          'dal_of_call': fields.float('No of Call', readonly=True),
          'pjc_product_line':fields.one2many('pjc.product.line', 'pjc_prod_id', 'PJC Product Line'),
          'state': fields.selection([('draft', 'validate'),
                                     ('progress', 'Progress'),
                                     ('product', 'Product Update'),
                                     ('submit', 'Waiting for Approval'),
                                     ('done', 'Submitted'),
                                     ('refuse', 'Cancel')],'Status', readonly=True, track_visibility='always'),
           }

    _defaults = {
        'state':'draft',
        'company_id': _get_default_company,
        'from_date': time.strftime("%Y-%m-%d"),
        'tdt_route_type':'local',
        'sr_id': lambda obj, cr, uid, context: uid,
        'tdt_manday_type':'full',
        }

    def onchange_partner_id(self, cr, uid, ids, partner_id, from_date, sr_id, context=None):
        result = {}
        if partner_id:
            part = self.pool.get('res.partner').browse(cr, uid, partner_id)
            result['value'] = {
                 'city':part.city,
                    }
        return result

    def generate(self, cr, uid, ids, context=None):
        obj = self.browse(cr,uid,ids)
        period_ids = self.pool['account.period'].find(cr, uid, dt=obj.from_date, context=dict(context, company_id=obj.company_id.id))
        self.write(cr, uid, ids, {'period_id':period_ids[0]}, context=context)
        cr.execute("""SELECT
                                pt.id as idsa,
                                pt.mandays_alloted as man,
                                pt.route_local as loc,
                                pt.route_val as val,
                                pt.local_ws as lo_ws,
                                pt.local_retail as lo_retail,
                                pt.van_ws as van_ws,
                                pt.van_retail as van_ret,
                                pt.no_of_call as calls
                            FROM pjc_target pt
                            JOIN account_period ap ON (ap.id = pt.period_id)
                            WHERE ap.date_start <= '%s' AND ap.date_stop >= '%s' AND pt.partner_id = '%s' AND pt.sr_id = '%s'
                   """ % (obj.from_date,obj.from_date,obj.partner_id.id,obj.sr_id.id))
        line_list = [i for i in cr.dictfetchall()]
        for line in line_list:
            vals = {
               'act_mandays_alloted':line['man'],
               'act_route_local':line['loc'],
               'act_route_val':line['val'],
               'act_local_ws':line['lo_ws'],
               'act_local_retail':line['lo_retail'],
               'act_van_ws':line['van_ws'],
               'act_van_retail':line['van_ret'],
               'no_of_call':line['calls']
             }
            self.write(cr, uid, ids, vals, context=context)
        cr.execute("""SELECT
                          coalesce(sum(pe.dal_mandays_alloted),0) as man,
                          coalesce(sum(pe.dal_route_local),0) as loc,
                          coalesce(sum(pe.dal_route_val),0) as val,
                          coalesce(sum(pe.dal_local_ws),0) as lo_ws,
                          coalesce(sum(pe.dal_local_retail),0) as lo_retail,
                          coalesce(sum(pe.dal_van_ws),0) as van_ws,
                          coalesce(sum(pe.dal_van_retail),0) as van_ret
                        FROM pjc_entry pe
                        WHERE pe.period_id = '%s' and state = 'done'
                   """ % (obj.period_id.id))
        line_list1 = [i for i in cr.dictfetchall()]
        if line_list1:
            for line1 in line_list1:
                val = {
                   'bal_mandays_alloted':obj.act_mandays_alloted - line1['man'],
                   'bal_route_local':obj.act_route_local - line1['loc'],
                   'bal_route_val':obj.act_route_val - line1['val'],
                   'bal_local_ws':obj.act_local_ws - line1['lo_ws'],
                   'bal_local_retail':obj.act_local_retail - line1['lo_retail'],
                   'bal_van_ws':obj.act_van_ws - line1['van_ws'],
                   'bal_van_retail':obj.act_van_retail - line1['van_ret']
                 }
                self.write(cr, uid, ids, val, context=context)
        else:
            val = {
                   'bal_mandays_alloted':obj.act_mandays_alloted,
                   'bal_route_local':obj.act_route_local,
                   'bal_route_val':obj.act_route_val,
                   'bal_local_ws':obj.act_local_ws,
                   'bal_local_retail':obj.act_local_retail,
                   'bal_van_ws':obj.act_van_ws,
                   'bal_van_retail':obj.act_van_retail
                 }
            self.write(cr, uid, ids, val, context=context)
        return self.write(cr, uid, ids, {'state':'progress'},context=context)
        
    def generate_entry(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        if obj.bal_mandays_alloted > 0.0:
            pj_sr = self.search(cr, uid, [('from_date','=',obj.from_date),('sr_id','=',obj.sr_id.id),('partner_id','=',obj.partner_id.id),('id','!=',obj.id)],context=context)
            if pj_sr:
                pj_br = self.browse(cr, uid, pj_sr[0])
                if pj_br.tdt_manday_type == 'half':
                    if obj.tdt_manday_type == 'half':
                        if obj.tdt_route_type == 'local':
                            if obj.tdt_local_ws is False and obj.tdt_local_retail is False:
                                raise osv.except_osv(_('Error!'), _('Please tick local WS or RETAIL'))
                            elif obj.tdt_local_ws is True:
                                if obj.tdt_local_ws is True and obj.bal_local_ws >= 0.50:
                                    self.write(cr, uid, ids, {'dal_local_ws':0.50,'dal_route_local':0.50,'dal_mandays_alloted':0.50},context=context)
                                else:
                                    raise osv.except_osv(_('Error!'), _('You cant entry local ws'))
                            elif obj.tdt_local_retail is True:
                                if obj.tdt_local_retail is True and obj.bal_local_retail >= 0.50:
                                    self.write(cr, uid, ids, {'dal_local_retail':0.50,'dal_route_local':0.50,'dal_mandays_alloted':0.50},context=context)
                                else:
                                    raise osv.except_osv(_('Error!'), _('You cant entry LOCAL RETAIL'))
                            else:
                                print "Success"
                        if obj.tdt_route_type == 'van':
                            if obj.tdt_van_ws is False and obj.tdt_van_retail is False:
                                raise osv.except_osv(_('Error!'), _('Please tick Van WS or RETAIL'))
                            elif obj.tdt_van_ws is True:
                                if obj.tdt_van_ws is True and obj.bal_van_ws >= 0.50:
                                    self.write(cr, uid, ids, {'dal_van_ws':0.50,'dal_route_val':0.50,'dal_mandays_alloted':0.50},context=context)
                                else:
                                    raise osv.except_osv(_('Error!'), _('You cant entry VAN WS'))
                            elif obj.tdt_van_retail is True:
                                if obj.tdt_van_retail is True and obj.bal_van_retail >= 0.50:
                                    self.write(cr, uid, ids, {'dal_van_retail':0.50,'dal_route_val':0.50,'dal_mandays_alloted':0.50},context=context)
                                else:
                                    raise osv.except_osv(_('Error!'), _('You cant entry VAN RETAIL'))
                            else:
                                print "Success"
                    else:
                        raise osv.except_osv(_('Error!'), _('Possible only half day enty entered'))
                else:
                    raise osv.except_osv(_('Error!'), _('Already this date entry submited'))
            else:
                if obj.tdt_manday_type == 'full':
                    if obj.tdt_route_type == 'local':
                        if obj.tdt_local_ws is False and obj.tdt_local_retail is False:
                            raise osv.except_osv(_('Error!'), _('Please tick local WS or RETAIL'))
                        elif obj.tdt_local_ws is True:
                            if obj.tdt_local_ws is True and obj.bal_local_ws >=1.00:
                                self.write(cr, uid, ids, {'dal_local_ws':1.00,'dal_route_local':1.00,'dal_mandays_alloted':1.00},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry local ws'))
                        elif obj.tdt_local_retail is True:
                            if obj.tdt_local_retail is True and obj.bal_local_retail >= 1.00:
                                self.write(cr, uid, ids, {'dal_local_retail':1.00,'dal_route_local':1.00,'dal_mandays_alloted':1.00},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry local retail'))
                        else:
                            print "Success"
                    if obj.tdt_route_type == 'van':
                        if obj.tdt_van_ws is False and obj.tdt_van_retail is False:
                            raise osv.except_osv(_('Error!'), _('Please tick Van WS or RETAIL'))
                        elif obj.tdt_van_ws is True:
                            if obj.tdt_van_ws is True and obj.bal_van_ws >= 1.00:
                                self.write(cr, uid, ids, {'dal_van_ws':1.00,'dal_route_val':1.00,'dal_mandays_alloted':1.00},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry van ws'))
                        elif obj.tdt_van_retail is True:
                            if obj.tdt_van_retail is True and obj.bal_van_retail >= 1.00:
                                self.write(cr, uid, ids, {'dal_van_retail':1.00,'dal_route_val':1.00,'dal_mandays_alloted':1.00},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry van retail'))
                        else:
                            print "Success"
                else:
                    if obj.tdt_route_type == 'local':
                        if obj.tdt_local_ws is False and obj.tdt_local_retail is False:
                            raise osv.except_osv(_('Error!'), _('Please tick local WS or RETAIL'))
                        elif obj.tdt_local_ws is True:
                            if obj.tdt_local_ws is True and obj.bal_local_ws >= 0.50:
                                self.write(cr, uid, ids, {'dal_local_ws':0.50,'dal_route_local':0.50,'dal_mandays_alloted':0.50},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry local ws'))
                        elif obj.tdt_local_retail is True:
                            if obj.tdt_local_retail is True and obj.bal_local_retail >= 0.50:
                                self.write(cr, uid, ids, {'dal_local_retail':0.50,'dal_route_local':0.50,'dal_mandays_alloted':0.50},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry LOCAL RETAIL'))
                        else:
                            print "Success"
                    if obj.tdt_route_type == 'van':
                        if obj.tdt_van_ws is False and obj.tdt_van_retail is False:
                            raise osv.except_osv(_('Error!'), _('Please tick Van WS or RETAIL'))
                        elif obj.tdt_van_ws is True:
                            if obj.tdt_van_ws is True and obj.bal_van_ws >= 0.50:
                                self.write(cr, uid, ids, {'dal_van_ws':0.50,'dal_route_val':0.50,'dal_mandays_alloted':0.50},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry VAN WS'))
                        elif obj.tdt_van_retail is True:
                            if obj.tdt_van_retail is True and obj.bal_van_retail >= 0.50:
                                self.write(cr, uid, ids, {'dal_van_retail':0.50,'dal_route_val':0.50,'dal_mandays_alloted':0.50},context=context)
                            else:
                                raise osv.except_osv(_('Error!'), _('You cant entry VAN RETAIL'))
                        else:
                            print "Success"
        else:
            raise osv.except_osv(_('Error!'), _('You cant enter Entry. Your target is over'))
        return self.write(cr, uid, ids, {'state':'product'},context=context)
        
    
    def done(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'},context=context)
        
    def submit(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'submit'},context=context)
        
    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancel'},context=context)
    
    def onchange_tdt_local_ws(self, cr, uid, ids, tdt_local_ws, context=None):
        result = {}
        if tdt_local_ws:
            result['value'] = {
                 'tdt_local_retail':False,
                        }
        return result

    def onchange_tdt_local_retail(self, cr, uid, ids, tdt_local_retail, context=None):
        result = {}
        if tdt_local_retail:
            result['value'] = {
                 'tdt_local_ws':False,
                        }
        return result

    def onchange_tdt_van_ws(self, cr, uid, ids, tdt_van_ws, context=None):
        result = {}
        if tdt_van_ws:
            result['value'] = {
                 'tdt_van_retail':False,
                        }
        return result

    def onchange_tdt_van_retail(self, cr, uid, ids, tdt_van_retail, context=None):
        result = {}
        if tdt_van_retail:
            result['value'] = {
                 'tdt_van_ws':False,
                        }
        return result

    def onchange_tdt_route_type(self, cr, uid, ids, tdt_route_type, context=None):
        result = {}
        if tdt_route_type == 'local':
            result['value'] = {
                 'tdt_van_ws':False,
                 'tdt_van_retail':False,
                        }
        else:
            result['value'] = {
                 'tdt_local_ws':False,
                 'tdt_local_retail':False,
                        }
        return result

pjc_entry()

class pjc_product_line(osv.osv):
    _name = 'pjc.product.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _columns = {
        'pjc_prod_id':fields.many2one('pjc.entry','PJC Entry'),
        'prod_categ_id': fields.many2one('product.category', 'Product Category', required=True),
        'product_id':fields.many2one('product.product', 'Product',required=True),
        'quantity':fields.float('Quantity'),
        'company_id': fields.many2one('res.company', 'Company'),
    }
    
    _defaults = {
        'company_id': _get_default_company,
        }
        
pjc_product_line()

#~ class pjc_entry_total(osv.osv):
    #~ _name = 'pjc.entry.total'

    #~ def _get_default_company(self, cr, uid, context=None):
        #~ company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        #~ if not company_id:
            #~ raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        #~ return company_id

    #~ _columns = {

          #~ 'from_date': fields.date('Date'),
          #~ 'sr_id': fields.many2one('res.users', 'Sales Representative', required=True),
          #~ 'company_id': fields.many2one('res.company', 'Company'),
          #~ 'state': fields.selection([('draft', 'submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
          #~ 'pjc_entry_line':fields.one2many('pjc.entry.line', 'pjc_entry_id', 'PJC Line'),
           #~ }

    #~ _defaults = {
        #~ 'state':'draft',
        #~ 'company_id': _get_default_company,
        #~ 'from_date': time.strftime("%Y-%m-%d"),
        #~ }

#~ pjc_entry_total()


class travel_expense(osv.osv):
    _name='travel.expense'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
            
    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('travel.expense.line').browse(cr, uid, ids, context=context):
            result[line.expense_id.id] = True
        return result.keys()
            
    def _amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'fare_total': 0.0,
                'allowance_total': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = val2 = 0.0
            for line in order.travel_expense_line_ids:
                val += line.price_subtotal
                val1 += line.allowance
                val2 += line.expense_amount
            res[order.id]['fare_total'] = val2
            res[order.id]['allowance_total'] = val1
            res[order.id]['amount_total'] = val
        return res  
    
    _columns={
            'sr_id':fields.many2one('res.users','Sales Representative',required=True),
            'company_id': fields.many2one('res.company', 'Company'),
            'designation':fields.char('Designation'),
            'head_quaters':fields.char('HQ'),
            'from_date':fields.date('Period From',required=True),
            'to_date':fields.date('Period To',required=True),
            'travel_expense_line_ids':fields.one2many('travel.expense.line','expense_id','Travel Expense Line'),
            'fare_total': fields.function(_amount_total, digits_compute=dp.get_precision('Discount'), string='Fare Total',
            store={
                'travel.expense': (lambda self, cr, uid, ids, c={}: ids, ['travel_expense_line_ids'], 10),
                'travel.expense.line': (_get_order, ['expense_amount', 'allowance', 'price_subtotal'], 10),
            },
            multi='sums'),
            'allowance_total': fields.function(_amount_total, digits_compute=dp.get_precision('Discount'), string='Allowance Total',
            store={
                'travel.expense': (lambda self, cr, uid, ids, c={}: ids, ['travel_expense_line_ids'], 10),
                'travel.expense.line': (_get_order, ['expense_amount', 'allowance', 'price_subtotal'], 10),
            },
            multi='sums'),
            'amount_total': fields.function(_amount_total, digits_compute= dp.get_precision('Discount'), string='Total',
            store={
                'travel.expense': (lambda self, cr, uid, ids, c={}: ids, ['travel_expense_line_ids'], 10),
                'travel.expense.line': (_get_order, ['expense_amount', 'allowance', 'price_subtotal'], 10),
            },
            multi='sums'),
            'state': fields.selection([('draft', 'Draft'),('waiting','Waiting For Approval'),('approve', 'Approve'),('refuse', 'Declined'),('done','Done')],'Status', readonly=True, track_visibility='always'),
            }      
            
    _defaults={
    
        'state':'draft',
        'company_id': _get_default_company,
    }
            
    def generate_travel_expense(self, cr, uid, ids, context=None):
        travel_expense=[]
        result = {}
        rec=self.browse(cr,uid,ids,context=context)
        cr.execute("""select sr_id,city from pjc_entry where sr_id= %s and from_date >= '%s' and from_date <= '%s' and company_id= %s """ % (rec.sr_id.id,rec.from_date,rec.to_date,rec.company_id.id))
        line_list = [i for i in cr.dictfetchall()] 
        print line_list   
        vals={}
        if line_list:
            for line1 in line_list:
                vals={
                    'expense_id':rec.id,
                    'destination_place':line1['city']
                }
                self.pool.get('travel.expense.line').create(cr,uid,vals,context=None)
        self.write(cr, uid, ids, {'state':'waiting'},context=context)
        return result  
        
    def submit(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'approve'},context=context)
        
    def manager_approval(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'done'},context=context)
        
    def reject(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'refuse'},context=context) 
        
    def set_to_draft(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'waiting'},context=context)   
        
    def write(self, cr, uid, ids, vals, context=None):
        res = super(travel_expense, self).write(cr, uid, ids, vals, context=context)
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft','waiting']:
				raise osv.except_osv(_('Invalid Action!'), _('Cannot Edit a Expense which is in state \'%s\'.') %(rec.state,))
        return res 
        
    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.state not in ['draft']:
                raise osv.except_osv(_('Invalid Action!'), _('Cannot delete a Expense which is in state \'%s\'.') %(rec.state,))
        return super(travel_expense, self).unlink(cr, uid, ids, context=context)                                    
            
class travel_expense_line(osv.osv):
    _name='travel.expense.line'
    

    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
            
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = line.expense_amount + line.allowance + line.postage
        return res  
    
    _columns={
            'expense_id':fields.many2one('travel.expense'),
            'start_place':fields.char('From'),
            'destination_place':fields.char('To'),
            'departure_date':fields.date('Departure'),
            'arrival_date':fields.date('Arrival'),
            'mode_of_travel':fields.selection([('bus', 'Bus'),('van', 'Van'),('train', 'Train')],'Mode of Travel'),
            'expense_amount':fields.float('Fare'),
            'allowance':fields.float('Daily Allowance'),
            'postage':fields.float('Postage'),
            'price_subtotal': fields.function(_amount_line, string='Total', digits_compute= dp.get_precision('Discount')),
            'company_id': fields.many2one('res.company', 'Company'),
    
    }
    
    _defaults={
        'company_id': _get_default_company,
    }    
