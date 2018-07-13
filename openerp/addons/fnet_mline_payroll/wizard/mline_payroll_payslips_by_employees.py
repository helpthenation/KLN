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
from datetime import datetime
from dateutil import relativedelta

from openerp.osv import fields, osv
from openerp.tools.translate import _

class mline_payslip_employees(osv.osv_memory):

    _name ='mline.payslip.employees'
    _description = 'Generate payslips for all selected employees'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'mline_employee_group_rel', 'payslip_id', 'employee_id', 'Employees'),
    }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('mline.payroll')
        run_pool = self.pool.get('mline.payroll.run')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, [context['active_id']], ['date_start', 'date_end', 'credit_note'])[0]
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        if not data['employee_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False, context=context)
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'payroll_run_id': context.get('active_id', False),
                'job_id':emp.job_id.id,
                'branch_id':emp.branch_id.id,
                'payslip_type':'general',
                'date_from': from_date,
                'date_to': to_date,
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        print'SSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS',slip_ids
        for slip in slip_ids:    
            slip_pool.worked_days(cr, uid, slip, context=context)
            slip_pool.compute_sheet(cr, uid, slip, context=context)
        return {'type': 'ir.actions.act_window_close'}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
