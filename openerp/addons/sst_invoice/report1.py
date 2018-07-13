from openerp.osv import osv
from openerp.report import report_sxw


class sale_order_report1(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        if context is None:
            context = {}
        super(sale_order_report1, self).__init__(cr, uid, name, context)
        ids = context.get('active_ids')
        print'IDSIDSIDSIDSIDIDIDISIDISIDDIISIDDSIDISDIDIDID',ids
        self.localcontext.update({
            #~ 'get_inc_no': self._get_inc_no,
        })

    #~ def _get_inc_no(self):
        #~ line = 0
        #~ value = line + 1
        #~ return value
         

class wrapped_report_saleorder(osv.AbstractModel):
    _name = 'report.sst_invoice.rate_quotationsss'
    _inherit = 'report.abstract_report'
    _template = 'sst_invoice.rate_quotationsss'
    _wrapped_report_class = sale_order_report1
    
