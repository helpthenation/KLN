# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Yannick Vaucher
#    Copyright 2013 Camptocamp SA
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
from openerp import models, api
import time
import datetime
from dateutil.relativedelta import relativedelta

import openerp
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.osv import fields, osv

class sale_configuration(osv.osv_memory):
    _inherit = 'hr.config.settings'
    
    _columns = {    
    'company_id': fields.many2one('res.company', 'Company', required=True),
    'number_of_days_vacation_leave':fields.related('company_id' , 'number_of_days_vacation_leave', type='float',
    string="Number of Days To Generate Vacancy ",help="Allows you to apply some discount per sales order Total Amount."),
    #~ 'group_product_discount':fields.related('company_id','group_product_discount',type='boolean',string="Allow setting a discount on the sales order line",
            #~ implied_group='fnet_discount.group_discount_global',
            #~ help="Allows you to apply some discount per sales order line."),  
    #~ 'discount_value':fields.related('company_id','discount_value',type='float',string='Discount Value',help='Choose the value of the Discount'),
    #~ 'discount_percentage':fields.related('company_id','discount_percentage',type='float',string='Discount Percentage',help='Choose the percentage of the Discount'),
    #~ 'discount_calculation_account_id':fields.related(type='many2one',
        #~ related='company_id.discount_calculation_account_id',
        #~ comodel='account.account',
        #~ string='Discount Account'),
    #~ 'product_discount_account_id':fields.related(type='many2one',
        #~ related='company_id.product_discount_account_id',
        #~ comodel='account.account',
        #~ string='Trading Account')
        }

    def _default_company(self, cr, uid, context=None):
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        return user.company_id.id
        
    _defaults = {
        'company_id': _default_company
    }        
    
    def create(self, cr, uid, values, context=None):
        id = super(sale_configuration, self).create(cr, uid, values, context)
        # Hack: to avoid some nasty bug, related fields are not written upon record creation.
        # Hence we write on those fields here.
        vals = {}
        for fname, field in self._columns.iteritems():
            if isinstance(field, fields.related) and fname in values:
                vals[fname] = values[fname]
        self.write(cr, uid, [id], vals, context)
        return id    
    
    @api.model
    def get_default_company_values(self, fields):
        company = self.env.user.company_id
        return {
            'number_of_days_vacation_leave': company.number_of_days_vacation_leave,
            #~ 'group_product_discount': company.group_product_discount,
            #~ 'discount_value': company.discount_value,
            #~ 'discount_percentage': company.discount_percentage,
            #~ 'discount_calculation_account_id': company.discount_calculation_account_id.id,
            #~ 'product_discount_account_id': company.product_discount_account_id.id,
        }

    @api.one
    def set_company_values(self):
        company = self.env.user.company_id
        company.number_of_days_vacation_leave = self.number_of_days_vacation_leave
        #~ company.group_product_discount = self.group_product_discount
        #~ company.discount_value = self.discount_value
        #~ company.discount_percentage = self.discount_percentage
        #~ company.discount_calculation_account_id = self.discount_calculation_account_id
        #~ company.product_discount_account_id = self.product_discount_account_id       
        
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(sale_configuration, self
                    ).onchange_company_id(cr, uid, ids,
                                          company_id, context=context)
        company = self.pool.get('res.company').browse(cr, uid, company_id,
                                                      context=context)
        res['value']['number_of_days_vacation_leave'] = company.number_of_days_vacation_leave
        #~ res['value']['group_product_discount'] = company.group_product_discount
        #~ res['value']['discount_value'] = company.discount_value
        #~ res['value']['discount_percentage'] = company.discount_percentage
        #~ res['value']['discount_calculation_account_id'] = \
            #~ company.discount_calculation_account_id.id
        #~ res['value']['product_discount_account_id'] = \
            #~ company.product_discount_account_id.id  
        return res
