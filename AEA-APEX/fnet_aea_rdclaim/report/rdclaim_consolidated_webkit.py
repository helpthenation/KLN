import xlwt
from datetime import datetime
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.addons.fnet_aea_rdclaim.wizard.rdclaim_wizard \
    import rdclaim_wizard
from openerp.tools.translate import _
from openerp.report import report_sxw
from openerp import pooler
from openerp.report import report_sxw
from common_header import common_header
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser
_column_sizes = [
    ('date', 30),
    ('period', 20),
    ('move', 20),
    ('journal', 20),
    ('account_code', 20),
    ('partner', 10),
    ('ref', 10),
    ('label', 10),
    ('counterpart', 10),
    ('debit', 10),
    ('credit', 10),
    ('cumul_bal', 10),
    ('curr_bal', 10),
    ('curr_code', 10),
]

class RDClaimConsolidateWebkitParser(report_sxw.rml_parse,common_header):

    def __init__(self, cursor, uid, name, context):
        super(RDClaimConsolidateWebkitParser, self).__init__(
            cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join(
            (_('RD Claim Consolidated Report'), company.name))
        footer_date_time = self.formatLang(str(datetime.today()),
                                           date_time=True)
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('RD Claim Consolidated'),
            'filter_form': self._get_filter,
            'additional_args': [
                ('--header-font-name', 'Helvetica'),
                ('--footer-font-name', 'Helvetica'),
                ('--header-font-size', '10'),
                ('--footer-font-size', '6'),
                ('--header-left', header_report_name),
                ('--header-spacing', '2'),
                ('--footer-left', footer_date_time),
                ('--footer-right', ' '.join((_('Page'), '[page]', _('of'),
                                             '[topage]'))),
                ('--footer-line',),
            ],
           
        })
        self.context = context    
    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'company_id' in data['form'] and [data['form']['company_id'][0]] or []
            objects = self.pool.get('rdclaim.wizard').browse(self.cr, self.uid, new_ids)
        main_filter = self._get_form_param('filter', data, default='filter_no')       
        start_date = self._get_form_param('date_from', data)
        stop_date = self._get_form_param('date_to', data)
        start_period = self.get_start_period_br(data)
        stop_period = self.get_end_period_br(data)
        manager = self.get_manger_id(data)
        product=self._get_product_name(data)
        sale_person=self._get_sale_person(data)
        #~ partner_lines=self._get_partner_lines(data)
        #~ product_categ=self.get_prod_categ_id(data)
        saleperson_name=self.get_saleperson_name(data)
        consolidate=self._get_consolidate_data(data)
        categ_name=self._get_categ_name(data)
        # computation of ledger lines
        if main_filter == 'filter_date':
            start = start_date
            stop = stop_date
        else:
            start = start_period
            stop = stop_period
                    
        self.localcontext.update({           
            'start_date': start_date,
            'stop_date': stop_date,
            'start_period': start_period,
            'stop_period': stop_period,   
            'manager':manager,
            'product':product  ,
            'sale_person':sale_person,
            #~ 'partner_lines':partner_lines,
            #~ 'product_categ':product_categ,
            'saleperson_name':saleperson_name,
            'consolidate':consolidate,
            'categ_name':categ_name
        })
        return super(RDClaimConsolidateWebkitParser, self).set_context(
            objects, data, new_ids, report_type=report_type)
HeaderFooterTextWebKitParser(
    'report.fnet_aea_rdclaim.report_rdclaim_consolidate_webkit',
    'rdclaim.wizard',
    'addons/fnet_aea_rdclaim/report/templates/\
                                        rdclaim_consolidated_report.mako',
    parser=RDClaimConsolidateWebkitParser)
