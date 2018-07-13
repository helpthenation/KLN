
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

class daily_flash(osv.osv):
    _name = 'daily.flash'
    
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
           
          'date': fields.date('Date'),
          'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True),
          'target_amount':fields.float('Target '),
          'user_id': fields.many2one('res.users', 'Sales Representative', readonly=True),
          'company_id': fields.many2one('res.company', 'Company'),
          'state': fields.selection([('draft', 'submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
          'daily_flash_line':fields.one2many('daily.flash.line', 'flash_id', 'Scheme Line'),
           }

    _defaults = {
        'state':'draft',
        'date': time.strftime("%Y-%m-%d"),
        'company_id': _get_default_company,
        'period_id': _get_period,
        'user_id': lambda obj, cr, uid, context: uid,
        }
        
    def onchange_date(self, cr, uid, ids, date, company_id, context=None):
        result = {}
        list_of_dict=[]
        if date:
            cr.execute("""select 
                                 pc.id as prod_categ_id
                            from product_category pc
                            where visible is True and company_id = '%s'
                            order by 1 """ % (company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"prod_categ_id":fid['prod_categ_id']})
            result['value'] = {'daily_flash_line':list_of_dict,}
        return result
        
    def create(self, cr, uid, vals, context=None):
        print vals, 
        dt = vals.get('date')
        company_id = vals.get('company_id')
        period_ids = self.pool['account.period'].find(cr, uid, dt=dt, context=dict(context, company_id=company_id))
        vals.update({'period_id':period_ids[0]})
        today = time.strftime("%Y-%m-%d")
        if dt > today:
            raise osv.except_osv(_('Date Error!'),
                            _('Wrongly give date. Please give Today or less then date'))
        new_id = super(daily_flash, self).create(cr, uid, vals, context=context)
        return new_id

    def _get_target(self, cr, uid, ids, categ, user, period, com, context=None):
        cr.execute("""select 
                                target_amount 
                        from batterie_user_line bul
                        join target_details td on (td.id = bul.batterie_details_id)
                        where bul.sr_user_id = '%s' and bul.company_id = '%s' 
                        and bul.prod_categ_id  = '%s' and bul.period_id = '%s' and td.state = 'done' """ % (user, com, categ, period))
        line_list =cr.dictfetchall()
        return line_list
    
    
    def submit(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        cr.execute("""select 
                                ccs.user_id
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where smr.member_id = '%s' and ccs.company_id = '%s' """ % (obj.user_id.id, obj.company_id.id))
        line_list =cr.dictfetchall()
        for line in obj.daily_flash_line:
            tot_sr = self.pool.get('total.flash.daily').search(cr, uid, [('company_id', '=', obj.company_id.id), \
                     ('prod_categ_id', '=', line.prod_categ_id.id), ('sr_user_id', '=', obj.user_id.id),\
                     ('period_id', '=', obj.period_id.id)], context=context)
            target = self._get_target(cr, uid, ids, line.prod_categ_id.id, obj.user_id.id, obj.period_id.id, obj.company_id.id, context=context)
            if not tot_sr:
                vals = {
                  'prod_categ_id':line.prod_categ_id.id,
                  'manager_id':line_list[0]['user_id'],
                  'sr_user_id':obj.user_id.id,
                  'period_id':obj.period_id.id,
                  'target_qyt':target[0]['target_amount']
                  }
                tot = self.pool.get('total.flash.daily').create(cr, uid, vals, context=context)
                da = str(obj.date).split("-")
                lastday1=calendar.monthrange(int(da[0]),int(da[1]))
                end=datetime.date(int(da[0]),int(da[1]),lastday1[1])
                start = obj.date
                year_f, month_f, day_f = (int(x) for x in str(start).split('-'))
                year_t, month_t, day_t = (int(x) for x in str(end).split('-'))
                d1 = date(year_f, month_f, day_f)
                d2 = date(year_t, month_t, day_t)
                delta = d2 - d1
                for i in range(delta.days + 1):
                    dd =  d1 + td(days=i)
                    year, month, day = (int(x) for x in str(dd).split('-'))
                    ans = datetime.date(year, month, day)
                    val = {
                      'total_flash_id':tot,
                      'date':ans,
                    }
                    self.pool.get('total.flash.daily.line').create(cr, uid, val, context=context)
                    l = self.pool.get('total.flash.daily.line').search(cr, uid, [('total_flash_id','=', tot),('date', '=', obj.date)], context=context)
                    self.pool.get('total.flash.daily.line').write(cr, uid, l[0], {'total_qty':line.product_qty}, context=context)
            else:
                cr.execute("""select 
                                tfdl.id
                        from total_flash_daily tfd
                        join total_flash_daily_line tfdl on (tfdl.total_flash_id = tfd.id)
                        where tfd.prod_categ_id = '%s' and tfd.sr_user_id = '%s' and tfd.company_id = '%s' and tfd.period_id = '%s' and tfdl.date = '%s' and tfdl.total_qty is NULL """ 
                        % (line.prod_categ_id.id, obj.user_id.id, obj.company_id.id, obj.period_id.id, obj.date))
                lin =cr.dictfetchall()
                if not lin:
                    raise osv.except_osv(_('Submission Error!'), _('Already updated for this date!'))
                else:
                    for lines in lin:
                        t = self.pool.get('total.flash.daily.line').browse(cr, uid, lines['id'])
                        self.pool.get('total.flash.daily.line').write(cr, uid, t.id, {'total_qty':line.product_qty}, context=context)
        return True
           
class daily_flash_line(osv.osv):
    _name = 'daily.flash.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
     'flash_id':fields.many2one('daily.flash', 'Daily Flash'),
     'prod_categ_id': fields.many2one('product.category', 'Product_category', readonly=True),
     'product_qty':fields.float('Quantity'),
     'company_id': fields.many2one('res.company', 'Company'),
      }
      
    _defaults = {
        'company_id': _get_default_company,
        'product_qty': 0.00,
        }
        
   
daily_flash_line()

class target_details(osv.osv):
    _name = 'target.details'
    
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
    'manager_id':fields.many2one('res.users', 'INL/SO', readonly=True),
    'period_id': fields.many2one('account.period', 'Period', required=True),
    'sr_user_id':fields.many2one('res.users', 'Sales Representative'),
    'batterie_user_line':fields.one2many('batterie.user.line', 'batterie_details_id', 'Battries'),
    'productivity_targer_line':fields.one2many('productivity.targer.line', 'productivity_target_id', 'Productivity Target'),
    'state': fields.selection([('draft', 'Submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
    'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults  = {
        'manager_id': lambda obj, cr, uid, context: uid,
        'state': 'draft',
        'company_id': _get_default_company,
        'period_id': _get_period,
       }

    def onchange_manager_id(self, cr, uid, ids, manager_id, company_id, period_id, context=None):
        result = {}
        list_of_batterie=[]
        list_of_produc_tar = []
        list_li=[]
        list_li2=[]
        listlist = []
        domain = {}
        if manager_id:
            period = self.pool.get('account.period').browse(cr, uid, period_id)
            cr.execute("""select 
                                smr.member_id,
                                ccs.id 
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where ccs.user_id = '%s' and ccs.company_id = '%s' """ % (manager_id, company_id))
            line_list = [i for i in cr.dictfetchall()]
            cr.execute(""" select category_code from product_category where visible is True and company_id = '%s' """ % (company_id))
            product_code = [i for i in cr.dictfetchall()]
            for prod in product_code:
                cr.execute(""" select id from product_category where category_code = '%s' and company_id = '%s' """ % (prod['category_code'], company_id))
                bat = cr.dictfetchall()
                for fid in line_list:
                    list_li.append(fid['member_id'])
                    list_of_batterie.append({"sr_user_id":fid['member_id'], "prod_categ_id":bat[0]['id'], "period_id":period.id, "section_id":fid['id']})
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
                for fid in line_list:
                    list_of_produc_tar.append({"sr_user_id":fid['member_id'], "period_id":period.id, "section_id":fid['id'], "date":ans})
            result['value'] = {'batterie_user_line':list_of_batterie,
                               'productivity_targer_line':list_of_produc_tar,}
            list_l = [item for item, count in collections.Counter(list_li).items() if count > 1]
            domain = {'sr_user_id':[('id', 'in', tuple(list_l))]}
            result['domain']=domain
        return result
    
    def onchange_period_id(self, cr, uid, ids, period_id, manager_id, company_id, context=None):
        sr = self.onchange_manager_id(cr, uid, ids, manager_id, company_id, period_id, context=context)
        if period_id:    
            for line in sr['value']['batterie_user_line']:
                line['period_id'] = period_id
            for line in sr['value']['productivity_targer_line']:
                line['period_id'] = period_id
        return sr
        
    def onchange_sr_user_id(self, cr, uid, ids, sr_user_id, manager_id, company_id, period_id, context=None):
        sr = self.onchange_manager_id(cr, uid, ids, manager_id, company_id, period_id, context=context)
        result = {}
        app_line = []
        tar_line = []
        if sr_user_id:
            for line in sr['value']['batterie_user_line']:
                if line['sr_user_id'] == sr_user_id:
                    app_line.append(line)
            for line in sr['value']['productivity_targer_line']:
                if line['sr_user_id'] == sr_user_id:
                    tar_line.append(line)
        result['value'] = {'batterie_user_line':app_line,'productivity_targer_line':tar_line}
        return result

    def submit(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)     
        
target_details()

class batterie_user_line(osv.osv):
    _name = 'batterie.user.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
       'batterie_details_id':fields.many2one('target.details', 'Sales SR Target'),
       'sr_user_id':fields.many2one('res.users', 'Sales Representative', readonly=True),
       'section_id':fields.many2one('crm.case.section', 'District', readonly=True),
       'prod_categ_id': fields.many2one('product.category', 'Product_category', readonly=True),
       'period_id': fields.many2one('account.period', 'Period', readonly=True),
       'target_amount':fields.float('Target Quantity'),
       'company_id': fields.many2one('res.company', 'Company'),
       }
       
    _defaults  = {
        'company_id': _get_default_company,
       }
   
batterie_user_line()

# Productivity Target
class productivity_targer_line(osv.osv):
    _name = 'productivity.targer.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
       'productivity_target_id':fields.many2one('target.details', 'Sales SR Target'),
       'sr_user_id':fields.many2one('res.users', 'Sales Representative', readonly=True),
       'section_id':fields.many2one('crm.case.section', 'District', readonly=True),
       #~ 'prod_categ_id': fields.many2one('product.category', 'Product_category', readonly=True),
       'period_id': fields.many2one('account.period', 'Period', readonly=True),
       'date': fields.date('Date', readonly=True),
       'target_amount':fields.float('Target Calls'),
       'company_id': fields.many2one('res.company', 'Company'),
       }
       
    _defaults  = {
        'company_id': _get_default_company,
       }
   
productivity_targer_line()

class total_flash_daily(osv.osv):
    _name = 'total.flash.daily'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _columns = {
    'prod_categ_id': fields.many2one('product.category', 'Product_category', readonly=True),
    'manager_id':fields.many2one('res.users', 'INL/SO', readonly=True),
    'sr_user_id':fields.many2one('res.users', 'Sales Representative', readonly=True),
    'target_qyt':fields.float('Target Quantity', readonly=True),
    'period_id': fields.many2one('account.period', 'Period', required=True),
    'total_flash_line':fields.one2many('total.flash.daily.line' ,'total_flash_id', 'Total Flash'),
    'company_id': fields.many2one('res.company', 'Company'),
       }
       
    _defaults  = {
        'company_id': _get_default_company,
       }
    
total_flash_daily()
  
class total_flash_daily_line(osv.osv):
    _name = 'total.flash.daily.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _columns = { 
     'total_flash_id':fields.many2one('total.flash.daily', 'Total Flash'),
     'date': fields.date('Date', readonly=True),
     'total_qty':fields.float('Quantity', readonly=True),
     'company_id': fields.many2one('res.company', 'Company'),
       }
       
    _defaults  = {
        'company_id': _get_default_company,
       }

total_flash_daily_line()

  # Productivity
  
class daily_productivity(osv.osv):
    _name = 'daily.productivity'
    
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
           
          'date': fields.date('Date'),
          'period_id': fields.many2one('account.period', 'Period', required=True, readonly=True),
          'target_amount':fields.float('Target '),
          'user_id': fields.many2one('res.users', 'Sales Representative', readonly=True),
          'company_id': fields.many2one('res.company', 'Company'),
          'state': fields.selection([('draft', 'submit'),('done', 'Submitted')],'Status', readonly=True, track_visibility='always'),
          'daily_productivity_line':fields.one2many('daily.productivity.line', 'productivity_id', 'Productivity'),
           }

    _defaults = {
        'state':'draft',
        'date': time.strftime("%Y-%m-%d"),
        'company_id': _get_default_company,
        'period_id': _get_period,
        'user_id': lambda obj, cr, uid, context: uid,
        }
        
    def onchange_date(self, cr, uid, ids, date, company_id, context=None):
        result = {}
        list_of_dict=[]
        if date:
            cr.execute("""select 
                                 pc.id as prod_categ_id
                            from product_category pc
                            where visible is True and company_id = '%s'
                            order by 1 """ % (company_id))
            line_list = [i for i in cr.dictfetchall()]
            for fid in line_list:
                list_of_dict.append({"prod_categ_id":fid['prod_categ_id']})
            result['value'] = {'daily_productivity_line':list_of_dict,}
        return result
        
    def create(self, cr, uid, vals, context=None):
        print vals, 
        dt = vals.get('date')
        company_id = vals.get('company_id')
        period_ids = self.pool['account.period'].find(cr, uid, dt=dt, context=dict(context, company_id=company_id))
        vals.update({'period_id':period_ids[0]})
        today = time.strftime("%Y-%m-%d")
        if dt > today:
            raise osv.except_osv(_('Date Error!'),
                            _('Wrongly give date. Please give Today or less then date'))
        new_id = super(daily_productivity, self).create(cr, uid, vals, context=context)
        return new_id
        
    def submit(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        cr.execute("""select 
                                ccs.user_id
                        from crm_case_section ccs
                        join sale_member_rel smr on (smr.section_id = ccs.id)
                        where smr.member_id = '%s' and ccs.company_id = '%s' """ % (obj.user_id.id, obj.company_id.id))
        line_list =cr.dictfetchall()
        for line in obj.daily_productivity_line:
            tot_sr = self.pool.get('daily.productivity.total').search(cr, uid, [('company_id', '=', obj.company_id.id), \
                     ('prod_categ_id', '=', line.prod_categ_id.id), ('sr_user_id', '=', obj.user_id.id),\
                     ('period_id', '=', obj.period_id.id)], context=context)
            #~ target = self._get_target(cr, uid, ids, line.prod_categ_id.id, obj.user_id.id, obj.period_id.id, obj.company_id.id, context=context)
            if not tot_sr:
                vals = {
                  'prod_categ_id':line.prod_categ_id.id,
                  'manager_id':line_list[0]['user_id'],
                  'sr_user_id':obj.user_id.id,
                  'period_id':obj.period_id.id,
                  #~ 'target_qyt':target[0]['target_amount']
                  }
                tot = self.pool.get('daily.productivity.total').create(cr, uid, vals, context=context)
                da = str(obj.date).split("-")
                lastday1=calendar.monthrange(int(da[0]),int(da[1]))
                end=datetime.date(int(da[0]),int(da[1]),lastday1[1])
                start = obj.date
                year_f, month_f, day_f = (int(x) for x in str(start).split('-'))
                year_t, month_t, day_t = (int(x) for x in str(end).split('-'))
                d1 = date(year_f, month_f, day_f)
                d2 = date(year_t, month_t, day_t)
                delta = d2 - d1
                for i in range(delta.days + 1):
                    dd =  d1 + td(days=i)
                    year, month, day = (int(x) for x in str(dd).split('-'))
                    ans = datetime.date(year, month, day)
                    val = {
                      'productivity_total_id':tot,
                      'date':ans,
                    }
                    self.pool.get('daily.productivity.total.line').create(cr, uid, val, context=context)
                    l = self.pool.get('daily.productivity.total.line').search(cr, uid, [('productivity_total_id','=', tot),('date', '=', obj.date)], context=context)
                    self.pool.get('daily.productivity.total.line').write(cr, uid, l[0], {'total_qty':line.product_qty}, context=context)
            else:
                cr.execute("""select 
                                tfdl.id
                        from daily_productivity_total tfd
                        join daily_productivity_total_line tfdl on (tfdl.productivity_total_id = tfd.id)
                        where tfd.prod_categ_id = '%s' and tfd.sr_user_id = '%s' and tfd.company_id = '%s' and tfd.period_id = '%s' and tfdl.date = '%s' and tfdl.total_qty is NULL """ 
                        % (line.prod_categ_id.id, obj.user_id.id, obj.company_id.id, obj.period_id.id, obj.date))
                lin =cr.dictfetchall()
                if not lin:
                    raise osv.except_osv(_('Submission Error!'), _('Already updated for this date!'))
                else:
                    for lines in lin:
                        t = self.pool.get('daily.productivity.total.line').browse(cr, uid, lines['id'])
                        self.pool.get('daily.productivity.total.line').write(cr, uid, t.id, {'total_qty':line.product_qty}, context=context)
        return True
 
class daily_productivity_line(osv.osv):
    _name = 'daily.productivity.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
        
    _columns = {
     'productivity_id':fields.many2one('daily.productivity', 'Productivity'),
     'prod_categ_id': fields.many2one('product.category', 'Product_category', readonly=True),
     'product_qty':fields.float('No of calls'),
     'company_id': fields.many2one('res.company', 'Company'),
      }
      
    _defaults = {
        'company_id': _get_default_company,
        'product_qty': 0.00,
        }
        
   
daily_flash_line()

class daily_productivity_total(osv.osv):
    _name = 'daily.productivity.total'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _columns = {
    'prod_categ_id': fields.many2one('product.category', 'Product_category', readonly=True),
    'manager_id':fields.many2one('res.users', 'INL/SO', readonly=True),
    'sr_user_id':fields.many2one('res.users', 'Sales Representative', readonly=True),
    #~ 'target_qyt':fields.float('Target Quantity', readonly=True),
    'period_id': fields.many2one('account.period', 'Period', required=True),
    'daily_productivity_total_line':fields.one2many('daily.productivity.total.line' ,'productivity_total_id', 'Total Productivity'),
    'company_id': fields.many2one('res.company', 'Company'),
       }
       
    _defaults  = {
        'company_id': _get_default_company,
       }
      
daily_productivity_total()
  
class daily_productivity_total_line(osv.osv):
    _name = 'daily.productivity.total.line'
    
    def _get_default_company(self, cr, uid, context=None):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        if not company_id:
            raise osv.except_osv(_('Error!'), _('There is no default company for the current user!'))
        return company_id
    
    _columns = { 
     'productivity_total_id':fields.many2one('daily.productivity.total', 'Total Productivity'),
     'date': fields.date('Date', readonly=True),
     'total_qty':fields.float('No of Calls', readonly=True),
     'allocated_call':fields.float('Target Calls', readonly=True),
     'company_id': fields.many2one('res.company', 'Company'),
       }
       
    _defaults  = {
        'company_id': _get_default_company,
       }

daily_productivity_total_line()
