import time
from datetime import datetime
from dateutil import relativedelta
from openerp import api, fields, models, _



class BrsUnreconcileReport(models.AbstractModel):
    _name = 'report.fnet_brs_unreconcile_report.report_brs_template'


    @api.model
    def render_html(self, docids, data=None):
        Report = self.env['report']
        stock_report = Report._get_report_from_name('fnet_brs_unreconcile_report.report_brs_template')
        context = dict(self._context or {})
        active_ids = context.get('active_ids', [])
        brs_obj = self.env['brs.statement'].browse(docids)

        docargs = {
            'doc_ids': docids,
            'doc_model': 'brs.statement',
            'docs': brs_obj,
            'data': data,
        }
        return self.env['report'].render('fnet_brs_unreconcile_report.report_brs_template', docargs)
