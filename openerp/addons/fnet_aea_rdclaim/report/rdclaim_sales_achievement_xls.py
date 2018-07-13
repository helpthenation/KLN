import xlwt
from datetime import datetime
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell
from openerp.addons.fnet_aea_rdclaim.wizard.rdclaim_wizard \
    import rdclaim_wizard
from openerp.tools.translate import _
from openerp import pooler
from openerp.report import report_sxw
from common_header import common_header
import xlsxwriter
from xlsxwriter.utility import xl_col_to_name
from xlsxwriter.utility import xl_cell_to_rowcol
_column_sizes = [
    ('date', 30),
    ('period', 20),
    ('move', 10),
    ('journal', 10),
    ('account_code', 10),
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

class RDClaimSalesAchievementParser(report_sxw.rml_parse,common_header):

    def __init__(self, cursor, uid, name, context):
        super(RDClaimSalesAchievementParser, self).__init__(
            cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join(
            (_('Sales Plan Achievement'), company.name, company.currency_id.name))
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('Sales Plan Achievement Xls'),
        })
        self.context = context    
    def set_context(self, objects, data, ids, report_type=None):
        new_ids = ids
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'company_id' in data['form'] and [data['form']['company_id'][0]] or []
            objects = self.pool.get('rdclaim.sales.achievement').browse(self.cr, self.uid, new_ids)
        manager = self.get_manger_id(data)
        sale_person=self._get_sale_person(data)
        product_categ=self.get_prod_categ_id(data)
        saleperson_name=self.get_saleperson_name(data)
        header=self._get_spa_header_data(data)
        stockiest_line=self._get_stockiest_line(data)
        month=self._get_month(data)
        period=self.get_period_id(data)
        self.localcontext.update({ 
            'manager':manager,
            'sale_person':sale_person,
            'product_categ':product_categ,
            'saleperson_name':saleperson_name,
            'header':header,
            'stockiest_line':stockiest_line,
            'month':month,
            'period':period
        })
        return super(RDClaimSalesAchievementParser, self).set_context(
            objects, data, new_ids, report_type=report_type)
class sales_achievement_xls(report_xls):
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
        style = xlwt.easyxf('pattern: pattern solid, fore_colour turquoise;'
                              'font: colour black, bold True ;')
        cell_format = _xs['bold'] + _xs['fill_blue'] + _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_styles_blue = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        c_specs = [
            ('coa', 2, 0, 'text', _('Sales Manager')),
            ('af', 5, 0, 'text', _('Sale Representative')),
            ('prd',3,0,'text',_('Period')),
            ('tm', 3, 0, 'text', _(' Product Category')),]
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.xls_write_row(
            ws, row_pos, row_data, row_style=cell_style_center) 
        cell_format = _xs['borders_all']
        cell_style = xlwt.easyxf(cell_format)
        cell_style_center = xlwt.easyxf(cell_format + _xs['center'])
        coa =_('Sale Manager')+': '
        if _p.manager.name:
            coa+=' '+_p.manager.partner_id.name 
        c_specs = [('coa',2,0,'text',coa),
           ('af', 5, 0, 'text', _p.saleperson_name),
           ('prd',3,0,'text',_p.period.name),
            ('tm', 3, 0, 'text', _p.product_categ.name),
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
        
        c_mrp=[
        ('mrp', 1, 0, 'text', _('MRP Price'), None, style),
        ('emp', 1, 0, 'text', _(' '), None, style)]
        for i in _p.header:
            t=(i['product_id'], 1, 0, 'text', _(str(i['mrp_price'])), None, style)
            c_mrp.append(t)
        c_mrp+=[('emp1', 1, 0, 'text', _(' '), None, style),
                         ('emp2', 1, 0, 'text', _(' '), None, style)]
        c_hdr_data = self.xls_row_template(c_mrp, [x[0] for x in c_mrp])  
        
        c_specs=[('emp', 1, 0, 'text', _(' '), None,),('empt', 1, 0, 'text', _(' '), None,cell_styles_blue)]
        for i in _p.header:
            t=(i['product_id'], 1, 0, 'text', _(i['default_code']), None, cell_styles_blue)
            c_specs.append(t)
        c_specs+=[('Pcs', 1, 0, 'text', _('Pcs'), None, cell_styles_blue),
                         ('Value', 1, 0, 'text', _('Value'), None, cell_styles_blue)]    
        c_hdr_data1 = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        
        c_qty=[('prod', 1, 0, 'text', _('Stockiest'), None),
       
        ('product', 1, 0, 'text', _('Pcs / Cs'), None, cell_styles_blue)]
        for i in _p.header:
            t=(i['product_id'], 1, 0, 'text', _(str(i['case_qty'])), None, cell_styles_blue)
            c_qty.append(t)
        c_qty+=[('emp', 1, 0, 'text', _(' '), None, cell_styles_blue),
                         ('emp', 1, 0, 'text', _(' '), None, cell_styles_blue)]    
        c_hdr_data2 = self.xls_row_template(c_qty, [x[0] for x in c_qty]) 
        c_invoice=[   ('name', 1, 0, 'text', _('Name'), None),
       
        ('inv', 1, 0, 'text', _('Price'), None, cell_styles_blue)]
        for i in _p.header:
            t=(i['product_id'], 1, 0, 'text', _(str(i['invoice_price'])), None, cell_styles_blue)
            c_invoice.append(t)
        c_invoice+=[ ('emp', 1, 0, 'text', _(' '), None, cell_styles_blue),
                          ('emp', 1, 0, 'text', _(' '), None, cell_styles_blue)]            
        c_hdr_data3 = self.xls_row_template(c_invoice, [x[0] for x in c_invoice]) 
        ll_cell_format = _xs['borders_all']
        ll_cell_style = xlwt.easyxf(ll_cell_format)
        ll_cell_style_center = xlwt.easyxf(ll_cell_format + _xs['center'])
        ll_cell_style_date = xlwt.easyxf(
            ll_cell_format + _xs['left'],
            num_format_str=report_xls.date_format)
        ll_cell_style_decimal = xlwt.easyxf(
            ll_cell_format + _xs['right'],
            num_format_str=report_xls.decimal_format)
        cnt = 0  
        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data)
        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data1)
        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data2)
        row_pos = self.xls_write_row(ws, row_pos, c_hdr_data3)
        for i in _p.stockiest_line:
                cnt += 1 
                row_start = row_pos
                c_sp1=[]
                c_sp2=[]
                c_sp3=[]
                c_sp4=[]
                c_sp5=[]
                for j in i['lines']:
                    c_sp1=[('emp', 1, 0, 'text', _(' '), None, c_hdr_cell_style),('coln', 1, 0, 'text', _(_p.month[0]['last']), None)]
                    v1=0
                    v2=0
                    v3=0
                    v4=0
                    v5=0
                    v6=0
                    v7=0
                    v8=0
                    c1=0
                    c2=0
                    c3=0
                    c4=0
                    c5=0
                    c6=0
                    c7=0
                    c8=0

                    for p in j['lastyr']: 
                        v1+=p['amount']*p['val'] 
                        c1+=p['amount']                      
                        t=(p['product_id'], 1, 0, 'number', _(p['amount']), None, ll_cell_style_center)
                        c_sp1.append(t)
                    c_sp1+=[('val', 1, 0, 'number', _(c1), None),('c', 1, 0, 'number', _(v1), None)]
                    c_sp2=[('emp', 1, 0, 'text', _(' '), None, c_hdr_cell_style),('coln', 1, 0, 'text', _(_p.month[0]['this']), None)]
                    for q in j['thisyr']:
                        v2+=q['amount']*q['val'] 
                        c2+=q['amount']                         
                        t=(q['product_id'], 1, 0, 'number', _(q['amount']), None,ll_cell_style_center)
                        c_sp2.append(t)     
                    c_sp2+=[('c2', 1, 0, 'number', _(c2), None),('v2', 1, 0, 'number', _(v2), None)]
                    c_sp3=[('colns', 1, 0, 'text', _(i['name']), None, c_hdr_cell_style),('coln', 1, 0, 'text', _('Opening Stock'), None)]
                    for r in j['saleopen']:                        
                        v3+=r['amount']*r['val'] 
                        c3+=r['amount']                             
                        t=(r['product_id'], 1, 0, 'number', _(r['amount']), None, ll_cell_style_center)
                        c_sp3.append(t) 
                    c_sp3+=[('c3', 1, 0, 'number', _(c3), None),('v3', 1, 0, 'number', _(v3), None)]
                    c_sp4=[('emp', 1, 0, 'text', _(' '), None, c_hdr_cell_style),('colm', 1, 0, 'text', _('TM RD Till Date'), None)]
                    for s in j['rdthis']:                        
                        v4+=s['amount']*s['val'] 
                        c4+=s['amount']                             
                        t=(s['product_id'], 1, 0, 'number', _(s['amount']), None, ll_cell_style_center)
                        c_sp4.append(t) 
                    c_sp4+=[('c4', 1, 0, 'number', _(c4), None),('v4', 1, 0, 'number', _(v4), None)]
                    c_sp5=[('emp', 1, 0, 'text', _(' '), None, c_hdr_cell_style),('col', 1, 0, 'text', _('LM RD Till Date'), None)]
                    for tt in j['rdlast']:                        
                        v5+=tt['amount']*tt['val'] 
                        c5+=tt['amount']                            
                        t=(tt['product_id'], 1, 0, 'number', _(tt['amount']), None, ll_cell_style_center)
                        c_sp5.append(t) 
                    c_sp5+=[('c5', 1, 0, 'number', _(c5), None),('v5', 1, 0, 'number', _(v5), None)]
                    c_sp6=[('emp', 1, 0, 'text', _(' '), None, c_hdr_cell_style),('col', 1, 0, 'text', _('% VS LM'), None)]
                    for v in j['percentage']:                        
                        v6+=v['amount']*v['val'] 
                        c6+=v['amount']                             
                        t=(v['id'], 1, 0, 'number', _(v['amount']), None, ll_cell_style_center)
                        c_sp6.append(t)                              
                    c_sp6+=[('c6', 1, 0, 'number', _(c6), None),('v6', 1, 0, 'number', _(v6), None)]
                    c_sp7=[('emp', 1, 0, 'text', _(' '), None, c_hdr_cell_style),('col', 1, 0, 'text', _('Till Date AWD'), None)]
                    for vv in j['awd']:   
                        v7+=vv['amount']*vv['val'] 
                        c7+=vv['amount']                                                 
                        t=(vv['product_id'], 1, 0, 'number', _(vv['amount']), None, ll_cell_style_center)
                        c_sp7.append(t)      
                    c_sp7+=[('c7', 1, 0, 'number', _(c7), None),('v7', 1, 0, 'number', _(v7), None)]
                    c_sp8=[('emp', 1, 0, 'text', _(' '), None, c_hdr_cell_style),('col', 1, 0, 'text', _('Closing'), None,c_hdr_cell_style_center)]
                    for cls in j['closing']:                        
                        v8+=cls['amount']*cls['val'] 
                        c8+=cls['amount']                             
                        t=(cls['id'], 1, 0, 'number', _(cls['amount']), None, c_hdr_cell_style_center)
                        c_sp8.append(t)                                                                     
                    c_sp8+=[('c8', 1, 0, 'number', _(c8), None,c_hdr_cell_style_center),('v8', 1, 0, 'number', _(v8), None,c_hdr_cell_style_center)]
                row_data = self.xls_row_template(c_sp1, [x[0] for x in c_sp1])
                row_pos = self.xls_write_row(ws, row_pos, row_data,ll_cell_style)
                row_data = self.xls_row_template(c_sp2, [x[0] for x in c_sp2])
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style)
                row_data = self.xls_row_template(c_sp3, [x[0] for x in c_sp3])
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style)
                row_data = self.xls_row_template(c_sp7, [x[0] for x in c_sp7])                       
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style) 
                row_data = self.xls_row_template(c_sp5, [x[0] for x in c_sp5])                       
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style)                 
                row_data = self.xls_row_template(c_sp4, [x[0] for x in c_sp4])
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style)
                row_data = self.xls_row_template(c_sp6, [x[0] for x in c_sp6])                       
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style) 
                row_data = self.xls_row_template(c_sp8, [x[0] for x in c_sp8])                       
                row_pos = self.xls_write_row(ws, row_pos, row_data, ll_cell_style)  
                row_pos += 0      
sales_achievement_xls('report.fnet_aea_rdclaim.rdclaim_sales_achievement_xls',
                   'rdclaim.sales.achievement',
                   parser=RDClaimSalesAchievementParser)

