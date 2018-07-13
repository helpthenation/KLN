# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, _


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    @api.multi
    def button_import_attendance(self):
        for payslip in self:
            payslip._import_attendance()

    @api.multi
    def _import_attendance(self):
        self.ensure_one()
        wd_obj = self.env["hr.payslip.worked_days"]
        day_obj = self.env["hr_timesheet_sheet.sheet.day"]
        date_from = self.date_from
        date_to = self.date_to        
        det =  self.date_from
        year_obj, month_obj, day = (int(x) for x in det.split('-'))
        self.cr.env.execute('''select distinct on(name::Date) name::Date from hr_attendance 
                       where employee_id = '%s' and to_char(name, 'MM')='%s' 
                      and to_char(name, 'YYYY')='%s' ''' % (obj.employee_id.id, str(month_obj).zfill(2), str(year_obj)))
        attend = self.cr.env.dictfetchall()   
        print'DDDDDDDDDDDDDDDDDDDDDDDD',attend
        res = {
            "name": _("Total Attendance"),
            "code": "ATTN",
            "number_of_days": 0.0,
            "number_of_hours": 0.0,
            "contract_id": self.contract_id.id,
            "payslip_id": self.id,
        }
        if attend:
                res["number_of_days"] = len(attend)

        wd_obj.create(res)
