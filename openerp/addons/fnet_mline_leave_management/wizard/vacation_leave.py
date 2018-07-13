# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017-TODAY Serpent Consulting Services Pvt. Ltd.
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
from openerp.osv import osv,fields
from openerp.tools.translate import _
from lxml import etree
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import date
from openerp.osv import orm, fields
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT
class vacation_leave_wizard(osv.osv_memory):
    _name='vacation.leave.wizard'

    def _get_period(self, cr, uid, context=None):
        if context is None: context = {}
        if context.get('period_id', False):
            return context.get('period_id')
        periods = self.pool.get('account.period').find(cr, uid, context=context)
        return periods and periods[0] or False 
        
            
    _columns={
    'period_id':fields.many2one('account.period','Select A Period'),
    'date':fields.date('Date'),
    'company_id': fields.many2one('res.company', 'Company'),
    }

    _defaults = {
        'date': time.strftime("%Y-%m-%d"),
        'period_id':_get_period,
        }

    def update(self, cr, uid, ids, context=None):
        obj = self.browse(cr, uid, ids)
        print'OBJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJ',obj
