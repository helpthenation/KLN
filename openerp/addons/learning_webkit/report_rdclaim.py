# -*- coding: utf-8 -*-
# © 2015 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import xlwt
import time
from datetime import datetime
from openerp.osv import orm

from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import translate, _
from openerp import pooler
import logging
_logger = logging.getLogger(__name__)

_ir_translation_name = 'report.rdclaim.xls'


class ReportRDClaimParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        
        super(ReportRDClaimParser, self).__init__(
            cr, uid, name, context=context)
        sche_obj = self.pool.get('apex.rdclaim.wizard')
        self.context = context
        wanted_list = sche_obj._report_xls_fields(cr, uid, context)
        template_changes = sche_obj._report_xls_template(cr, uid, context)
        print'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',wanted_list
        self.localcontext.update({
            'datetime': datetime,
            'wanted_list': wanted_list,
            'template_changes': template_changes,
            '_': self._,
        })
   
    def _(self, src):
        lang = self.context.get('lang', 'en_US')
        return translate(self.cr, _ir_translation_name, 'report',
                         lang, src) or src


class ReportRDClaim(report_xls):
    def __init__(self, name, table, rml=False, parser=False, header=True, store=False):
        super(ReportRDClaim, self).__init__(name, table, rml, parser, header, store)
        
        # Cell Styles
        _xs = self.xls_styles     
        print'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', table  
        # header
        rh_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])
        self.rh_cell_style_right = xlwt.easyxf(rh_cell_format + _xs['right'])
        # lines  
        aml_cell_format = _xs['borders_all']
        self.aml_cell_style = xlwt.easyxf(aml_cell_format)
        self.aml_cell_style_center = xlwt.easyxf(aml_cell_format + _xs['center'])
        self.aml_cell_style_date = xlwt.easyxf(aml_cell_format + _xs['left'], num_format_str = report_xls.date_format)
        self.aml_cell_style_decimal = xlwt.easyxf(aml_cell_format + _xs['right'], num_format_str = report_xls.decimal_format)
        # totals
        rt_cell_format = _xs['bold'] + _xs['fill'] + _xs['borders_all']
        self.rt_cell_style = xlwt.easyxf(rt_cell_format)
        self.rt_cell_style_right = xlwt.easyxf(rt_cell_format + _xs['right'])       
        self.rt_cell_style_decimal = xlwt.easyxf(rt_cell_format + _xs['right'], num_format_str = report_xls.decimal_format)

        # XLS Template
        self.col_specs_template = {

            }

    # write table head
    def get_c_specs(self, wanted, col_specs, rowtype, data):

        """
        returns 'evaluated' col_specs

        Input:
        - wanted: element from the wanted_list
        - col_specs : cf. specs[1:] documented in xls_row_template method
        - rowtype : 'header' or 'data'
        - render_space : type dict, (caller_space + localcontext)
                         if not specified
        """
       
        row = col_specs[wanted][rowtype][:]
        print'rrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrrr',row
        row[3]=data[wanted]

        row.insert(0, wanted)
        return row

    def new_xls_write_row(self, ws, row_pos, row_data, header, headrot_style, dark_style, set_column_size=False ):
        print'NNNNNNNNNNNNNNNNNNNNNNNNNNNNNNNN',ws
        r = ws.row(row_pos)
        orig_style=row_style
        for col, size, spec in row_data:    

            data = spec[4]
            if header:
                if (col!=0) & (col!=1) & (col!=2):
                    row_style=headrot_style #+  'align: rotation 90;'
            else:
                if data=="X":
                    row_style=dark_style #+ 'pattern: pattern solid, fore_color 0;'
                else:
                    row_style=orig_style
            formula = spec[5].get('formula') and \
                xlwt.Formula(spec[5]['formula']) or None
            style = spec[6] and spec[6] or row_style
            if not data:
                # if no data, use default values
                data = report_xls.xls_types_default[spec[3]]
            if size != 1:
                if formula:
                    ws.write_merge(
                        row_pos, row_pos, col, col + size - 1, data, style)
                else:
                    ws.write_merge(
                        row_pos, row_pos, col, col + size - 1, data, style)
            else:
                if formula:
                    ws.write(row_pos, col, formula, style)
                else:
                    spec[5]['write_cell_func'](r, col, data, style)
            if set_column_size:
                ws.col(col).width = spec[2] * 256
        return row_pos + 1

        return True
    def generate_xls_report(self, _p, _xs, data, objects, wb):
        print'SSSSSSSSSSSSSSSSS',wb
        wanted_list = _p.wanted_list
        self.col_specs_template.update(_p.template_changes)
        _ = _p._
        #report_name = objects[0]._description or objects[0]._name
        report_name = _("Export Contract Countries")        
        ws = wb.add_sheet(report_name[:31])
        ws.panes_frozen = True
        ws.remove_splits = True
        ws.portrait = 0 # Landscape
        ws.fit_width_to_pages = 1
        row_pos = 0

        _xs = self.xls_styles 
        headrot_style = _xs['bold'] + _xs['fill'] + _xs['borders_all'] + 'align: rotation 90'
        xlwt_headrot=xlwt.easyxf(headrot_style) 
        dark_style = _xs['borders_all']+'pattern: pattern solid, fore_color 0;'

        #self.rh_cell_style = xlwt.easyxf(rh_cell_format)
        #self.rh_cell_style_center = xlwt.easyxf(rh_cell_format + _xs['center'])


        # set print header/footer
        ws.header_str = self.xls_headers['standard']
        ws.footer_str = self.xls_footers['standard']

        # Title
        cell_style = xlwt.easyxf(_xs['xls_title'])
        c_specs = [
            ('report_name', 1, 0, 'text', report_name),
        ]       
        row_data = self.xls_row_template(c_specs, ['report_name'])
        row_pos = self.new_xls_write_row(ws, row_pos, row_data, False, xlwt_headrot , xlwt.easyxf(dark_style), row_style=cell_style )
        row_pos += 1

        # Column headers
        c_specs = map(lambda x: self.render(x, self.col_specs_template, 'header', render_space={'_': _p._}), wanted_list)
        row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
        row_pos = self.new_xls_write_row(ws, row_pos, row_data, True, xlwt_headrot, xlwt.easyxf(dark_style), row_style=self.rh_cell_style, set_column_size=True)        
        ws.set_horz_split_pos(row_pos)   

        # account move lines
        for line in data['contract_list']:
            c_specs = map(lambda x: self.get_c_specs(x, self.col_specs_template, 'lines', line), wanted_list)
            row_data = self.xls_row_template(c_specs, [x[0] for x in c_specs])
            row_pos = self.new_xls_write_row(ws, row_pos, row_data, False, xlwt_headrot, xlwt.easyxf(dark_style), row_style=self.aml_cell_style)
ReportRDClaim(
    'report.report.rdclaim.xls', 'apex.rdclaim.wizard',
    parser=ReportRDClaimParser)
    #~ def table_head(self, ws, style0, style1):
        #~ """
            #~ generate fixed table head,return title_list and col number
        #~ """
        #~ ws.write_merge(1, 2, 0, 0, u'序号', style1)
        #~ ws.write_merge(1, 2, 1, 1, u'年月', style1)
        #~ ws.write_merge(1, 2, 2, 2, u'姓 名', style1)
        #~ ws.write_merge(1, 2, 3, 3, u'职位', style1)
        #~ col = 3
        #~ title_list = ['month', 'name', 'job_title']
        #~ return title_list, col
#~ 
    #~ def table_head_info(self, ws, col, rule_group, title_list, style1):
        #~ """
            #~ auto generate table head,return title_list and col number
        #~ """
        #~ if len(rule_group['rules']) == 1:
            #~ col += 1
            #~ ws.write_merge(1, 2, col, col, rule_group['category'], style1)
            #~ title_list.append(rule_group['rules'][0].name)
        #~ else:
            #~ merge_col = col + 1
            #~ if rule_group['type'] == 'add':
                #~ col += 1
                #~ ws.write(2, col, u'小计', style1)
                #~ title_list.append('add_total')
            #~ elif rule_group['type'] == 'sub':
                #~ col += 1
                #~ ws.write(2, col, u'小计', style1)
                #~ title_list.append('sub_total')
            #~ rules = []
            #~ for rule in rule_group['rules']:
                #~ obj_dict = {}
                #~ obj_dict['name'] = rule.name
                #~ obj_dict['sequence'] = rule.sequence
                #~ rules.append(obj_dict)
            #~ # sorted by rule sequence
            #~ rules = sorted(rules, key=lambda x: x['sequence'])
            #~ for rule in rules:
                #~ col += 1
                #~ ws.write(2, col, rule['name'], style1)
                #~ title_list.append(rule['name'])
            #~ ws.write_merge(
                #~ 1, 1, merge_col, col, rule_group['category'], style1)
            #~ if rule_group['type'] == 'add':
                #~ col += 1
                #~ ws.write_merge(1, 2, col, col, u'应发工资', style1)
                #~ title_list.append('should_paid')
            #~ elif rule_group['type'] == 'sub':
                #~ col += 1
                #~ ws.write_merge(1, 2, col, col, u'实发工资', style1)
                #~ title_list.append('real_wage')
        #~ return title_list, col
#~ 
    #~ def table_title(self, ws, col, title, style0, style1):
        #~ """
            #~ generate table title,return col number
        #~ """
        #~ col += 1
        #~ ws.write_merge(1, 2, col, col, u'备注', style1)
        #~ ws.write_merge(0, 0, 0, col, title, style0)
        #~ col += 1
        #~ ws.row(0).height = 255 * 3
        #~ return col
#~ 
    #~ # write table information
    #~ def table_info(self, ws, num, result, title_list, style1):
        #~ """
            #~ generate table information,return row number
        #~ """
        #~ number = 0
        #~ for number, res in enumerate(result):
            #~ ws.write(num, 0, number + 1, style1)
            #~ for title in title_list:
                #~ ws.write(num, title_list.index(title) + 1, res[title], style1)
            #~ ws.write(num, title_list.index(title) + 2, '', style1)
            #~ num += 1
        #~ return num
#~ 
    #~ def table_foot(self, ws, num, col, style1, style2):
        #~ """
            #~ generate table foot,return row number
        #~ """
        #~ ws.write_merge(num, num, 0, 3, u'合     计', style1)
        #~ for number in range(4, col):
            #~ ws.write(num, number, '', style1)
        #~ num += 1
        #~ ws.write_merge(num, num, 0, 2, u'负责人：', style2)
        #~ ws.write_merge(num, num, 3, 5, u'出纳：', style2)
        #~ ws.write_merge(num, num, 6, 8, u'会计：', style2)
        #~ ws.write_merge(num, num, 9, 11, u'制表：', style2)
        #~ ws.write_merge(num, num, 12, 14, u'制表：', style2)
        #~ num += 1
        #~ return num
#~ 
    #~ def get_job_title(self, obj):
        #~ """
            #~ return job title
        #~ """
        #~ if obj.employee_id.job_id and obj.employee_id.job_id.name:
            #~ return obj.employee_id.job_id.name
        #~ else:
            #~ return ''
#~ 
    #~ def xls_format(self):
        #~ '''
        #~ return xls style
        #~ @return style0, style1, style2
        #~ '''
        #~ borders = xlwt.Borders()
        #~ borders.left = 1
        #~ borders.right = 1
        #~ borders.top = 1
        #~ borders.bottom = 1
        #~ borders.bottom_colour = 0x3A
#~ 
        #~ font0 = xlwt.Font()
        #~ font0.name = 'Arial'
        #~ font0.height = 350
        #~ font0.bold = True
        #~ font0.underline = True
#~ 
        #~ font1 = xlwt.Font()
        #~ font1.name = 'Arial'
        #~ font1.height = 200
#~ 
        #~ # center
        #~ alignment = xlwt.Alignment()
        #~ alignment.horz = xlwt.Alignment.HORZ_CENTER
        #~ alignment.vert = xlwt.Alignment.VERT_CENTER
#~ 
        #~ # for title
        #~ style0 = xlwt.XFStyle()
        #~ style0.font = font0
        #~ style0.alignment = alignment
#~ 
        #~ style1 = xlwt.XFStyle()
        #~ style1.font = font1
        #~ style1.borders = borders
        #~ style1.alignment = alignment
#~ 
        #~ style2 = xlwt.XFStyle()
        #~ style2.font = font1
        #~ style2.alignment = alignment
        #~ return style0, style1, style2
#~ 
    #~ def generate_xls_report(self, _p, _xs, data, objects, wb):
        #~ """
            #~ generate hr payslip report
        #~ """
        #~ style0, style1, style2 = self.xls_format()
        #~ ws = wb.add_sheet('Sheet1')
        #~ rule_groups = []
        #~ result = []
        #~ num = 3
        #~ slip_objs = objects.slip_ids
        #~ # if not have payslip,display empty file
        #~ if slip_objs:
            #~ # satisfy the condition
            #~ categorys = slip_objs[0].struct_id.rule_ids.read_group(
                #~ [('appear_on_report', '=', True),
                 #~ ('id', 'in', slip_objs[0].struct_id.rule_ids.ids)],
                #~ [], ['category_id'])
            #~ title_list, col = self.table_head(ws, style0, style1)
            #~ for category in categorys:
                #~ groups = {}
                #~ rule_ids = self.pool.get('hr.salary.rule').search(
                    #~ self.cr, SUPERUSER_ID, category['__domain'])
                #~ rules = self.pool.get('hr.salary.rule').browse(
                    #~ self.cr, SUPERUSER_ID, rule_ids)
                #~ groups['rules'] = rules
                #~ groups['sequence'] = rules[0].category_id.sequence_number
                #~ groups['category'] = rules[0].category_id.name
                #~ groups['type'] = rules[0].category_id.category_type
                #~ rule_groups.append(groups)
            #~ # sorted by rule category sequence
            #~ rule_groups = sorted(rule_groups, key=lambda x: x['sequence'])
            #~ for rule_group in rule_groups:
                #~ title_list, col = self.table_head_info(
                    #~ ws, col, rule_group, title_list, style1)
            #~ col = self.table_title(ws, col, objects.name, style0, style1)
            #~ for slip in slip_objs:
                #~ obj_dict = {}
                #~ obj_dict['month'] = slip.date_from
                #~ obj_dict['name'] = slip.employee_id.name_related
                #~ obj_dict['job_title'] = self.get_job_title(slip)
                #~ obj_dict['remarks'] = ''
                #~ add_total = 0.0
                #~ sub_total = 0.0
                #~ basic_total = 0.0
                #~ for rule in slip.details_by_salary_rule_category:
                    #~ obj_dict[rule.name] = rule.total
                    #~ if rule.category_id.category_type == 'add':
                        #~ add_total += rule.total
                    #~ if rule.category_id.category_type == 'sub':
                        #~ sub_total += rule.total
                    #~ if rule.category_id.category_type == 'basic':
                        #~ basic_total += rule.total
                #~ obj_dict['add_total'] = add_total
                #~ obj_dict['should_paid'] = basic_total + add_total
                #~ obj_dict['sub_total'] = sub_total
                #~ obj_dict['real_wage'] = basic_total + add_total + sub_total
                #~ result.append(obj_dict)
            #~ num = self.table_info(ws, num, result, title_list, style1)
            #~ num = self.table_foot(ws, num, col, style1, style2)
#~ contract_sales_forecast_xls('report.contract.sales.forecast.xls', 
    #~ 'abc.salesforecast',
    #~ parser="contract_sales_forecast_xls_parser")


