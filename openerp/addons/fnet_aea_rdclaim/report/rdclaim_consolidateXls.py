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
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from xlsxwriter.utility import xl_cell_to_rowcol
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

class RDClaimConsolidateXlsParser(report_sxw.rml_parse,common_header):

    def __init__(self, cursor, uid, name, context):
        super(RDClaimConsolidateXlsParser, self).__init__(
            cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join(
            (_('RD Claim Report'), company.name, company.currency_id.name))
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('RD Claim Consolidated Xls'),
            'filter_form': self._get_filter,
           
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
            'saleperson_name':saleperson_name,
            'consolidate':consolidate,
            'categ_name':categ_name
        })
        return super(RDClaimConsolidateXlsParser, self).set_context(
            objects, data, new_ids, report_type=report_type)
class rdclaim_consolidate_xls(report_xls):
    column_sizes = [x[1] for x in _column_sizes]

    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet(_p.report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0  # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0
        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']
        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        report_name = ' - '.join([_p.report_name.upper(),
                                 _p.company.partner_id.name,
                                 _p.company.currency_id.name])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style)
        c_sizes = self.column_sizes
        c_specs = [('empty%s' % i, 1, c_sizes[i], 'text', None)
                   for i in range(0, len(c_sizes))]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, set_column_size=True)      
        # Header Table
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 2, 0, 'text', _('Sales Manager')),
            
            ('df', 3, 0, 'text', _p.filter_form(data) ==
             'filter_date' and _('Dates Filter') or _('Periods Filter')),
            ('af', 5, 0, 'text', _('Sale Representative'))     

        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center) 
        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        coa =_('Sale Manager')+': '
        if _p.manager.name:
            coa+=' '+_p.manager.partner_id.name
        df = _('From') + ': '       

        if _p.filter_form(data) == 'filter_date':
            df += _p.start_date if _p.start_date else u''
        else:
            df += _p.start_period.name if _p.start_period else u''
        df += ' ' + _('To') + ': '
        if _p.filter_form(data) == 'filter_date':
            df += _p.stop_date if _p.stop_date else u''
        else:
            df += _p.stop_period.name if _p.stop_period else u''
        c_specs = [('coa',2,0,'text',coa),
            ('df', 3, 0, 'text', df),
           ('af', 5, 0, 'text', _p.saleperson_name)
        ]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(ws, row_pos, row_data, row_style=cell_style_center)
        ws.set_horz_split_pos(row_pos)
        row_pos += 1
        cell_format = _xs['bold']
        c_title_cell_style = xlwt.easyxf(cell_format)

        # Column Header Row
        cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        c_hdr_cell_style = xlwt.easyxf(cell_format)
        c_hdr_cell_style_right = xlwt.easyxf(cell_format + _xs['right'])
        c_hdr_cell_style_left = xlwt.easyxf(_xs['left'])
        c_hdr_cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_hdr_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)

        # Column Initial Balance Row
        cell_format = _xs['italic'] + _xs['borders_all']
        c_init_cell_style = xlwt.easyxf(cell_format)
        c_init_cell_style_decimal = xlwt.easyxf(
            cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        c_specs=[('prod', 1, 0, 'text', _('Stockiest Name'), None, c_hdr_cell_style),
       
        ('product', 1, 0, 'text', _('City'), None, c_hdr_cell_style)]
        for i in _p.categ_name:
            t=(i['id'], 1, 0, 'text', _(i['name']), None, c_hdr_cell_style)
            c_specs.append(t)
        c_specs+=[('Total Claim Value', 1, 0, 'text', _('Total'), None, c_hdr_cell_style),
                         ('Special Pool Value', 1, 0, 'text', _('Special'), None, c_hdr_cell_style)]    
        c_hdr_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])

        ll_cell_format = _xs['borders_all']
        ll_cell_style = xlwt.easyxf(ll_cell_format)
        ll_cell_style_center = xlwt.easyxf(ll_cell_format + _xs['center'])
        ll_cell_style_date = xlwt.easyxf(
            ll_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        ll_cell_style_decimal = xlwt.easyxf(
            ll_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        col=1
        if _p.categ_name:
            for i in _p.categ_name:
                col=col+1
                columns = xl_col_to_name(col) 
        else:
            columns = xl_col_to_name(col+1)     
        cnt = 0 
        for i in _p.consolidate:
                cnt += 1 
                row_pos = self.xls_write_row(ws, row_pos, c_hdr_data)
                row_start = row_pos
                no=row_start+1
                for j in  i['customer_details']:
                    
                    c_sp=[
                    ('period', 1, 0, 'text', _(j['name']), None, c_hdr_cell_style_left),
                    ('per', 1, 0, 'text', _(j['city']), None, c_hdr_cell_style_left)]
                    amt=('amt', 1, 0, 'number', _(j['amount']), None, c_hdr_cell_style_decimal)
                    for k in j['prod']:
                         t=(k, 1, 0, 'number', _(k['qty']), None, ll_cell_style_center)
                         c_sp.append(t)
                    count_start = 'C'+str(no)
                    count_end = str(columns)+str(no)
                    count_formula = 'SUM(' + count_start + ':' + count_end + ')' 
                    count=(no, 1, 0, 'number', None,count_formula, c_hdr_cell_style_decimal) 
                    no=no+1
                    c_sp.append(count) 
                    c_sp.append(amt)  
                    
                    row_data = self.xls_row_template(
                                c_sp, [x[0] for x in c_sp])
                           
                    row_pos = self.xls_write_row(
                                ws, row_pos, row_data, ll_cell_style)  
                n=0
                c_sps=[('scah', 1, 0, 'text', _(i['saleperson']), None, c_hdr_cell_style),
                ('schh', 1, 0, 'text', _(i['sp_city']), None, c_hdr_cell_style)]
                for i in range(len(_p.categ_name)+2):
                    n=n+1
                    debit_start = rowcol_to_cell(row_start, n+1)
                    debit_end = rowcol_to_cell(row_pos - 1, n+1)
                    debit_formula = 'SUM(' + debit_start + ':' + debit_end + ')' 
                    c_sps += [
                        (n, 1, 0, 'number', None,
                         debit_formula, c_hdr_cell_style_decimal) ]
                row_data = self.xls_row_template(
                        c_sps, [x[0] for x in c_sps])
                row_pos = self.xls_write_row(
                        ws, row_pos, row_data, c_hdr_cell_style)

                row_pos += 1
rdclaim_consolidate_xls('report.fnet_aea_rdclaim.rdclaim_consolidated_xls',
                   'rdclaim.wizard',
                   parser=RDClaimConsolidateXlsParser)
