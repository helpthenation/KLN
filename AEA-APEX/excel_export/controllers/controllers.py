# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012-2013:
#        Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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
try:
    import json
except ImportError:
    import simplejson as json
import xlsxwriter
import openerp.http as http
from openerp.http import request
from openerp import _
from openerp.exceptions import Warning
from openerp.addons.web.controllers.main import ExcelExport
from datetime import datetime
import xlrd
import os


url=os.path.dirname(os.path.realpath('excel_export'))
class ExcelExportView(ExcelExport):
    def __getattribute__(self, name):
        if name == 'fmt':
            raise AttributeError()
        return super(ExcelExportView, self).__getattribute__(name)


     
    @http.route('/web/export/xls_view/po/tax', type='http', auth='user')
    def export_xls_view_tn_po(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[]) 
        tax_rec=request.env['tn.po.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'tn_purchase_tax.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#8281c7'})
        merge_format2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})

        worksheet.set_column('A:A', 10)
        worksheet.set_column('A:B', 15)
        worksheet.set_column('A:C', 15)
        worksheet.set_column('A:D', 15)
        worksheet.set_column('A:E', 15)
        worksheet.set_column('A:F', 15)
        worksheet.set_column('A:G', 15)
        worksheet.set_column('A:H', 15)
        worksheet.set_column('A:I', 15)
        worksheet.set_column('A:J', 15)
        worksheet.write('A1', 'serial_no',merge_format1)
        worksheet.write('B1', 'Name_of_seller',merge_format1)
        worksheet.write('C1', 'Seller_TIN',merge_format1)
        worksheet.write('D1', 'commodity_code',merge_format1)
        worksheet.write('E1', 'Invoice_No',merge_format1)
        worksheet.write('F1', 'Invoice_Date',merge_format1)
        worksheet.write('G1', 'Purchase_Value',merge_format1)
        worksheet.write('H1', 'Tax_rate',merge_format1)
        worksheet.write('I1', 'VAT_CST_paid',merge_format1)
        worksheet.write('J1', 'Category',merge_format1)
                
        row=1
        col=0  
        s_no=1
        for line in tax_rec.tn_po_tax_ids:
            worksheet.write(row,col,s_no,merge_format2)
            worksheet.write(row,col+1,(line.partner_id.name if line.partner_id.name else ''),merge_format2)
            worksheet.write(row,col+2,(line.seller_tin if line.seller_tin else ''),merge_format2)
            worksheet.write(row,col+3,(line.commodity_code if line.commodity_code else ''),merge_format2)
            worksheet.write(row,col+4,(line.invoice_id.number if line.invoice_id.number else ''),merge_format2)
            worksheet.write(row,col+5,((datetime.strptime(line.invoice_date, '%Y-%m-%d').strftime('%m-%d-%Y'))  if line.invoice_date else ''),merge_format2)
            worksheet.write(row,col+6,(line.purchase_value if line.purchase_value else ''),merge_format2)
            worksheet.write(row,col+7,(line.tax_rate if line.tax_rate else ''),merge_format2)
            worksheet.write(row,col+8,(line.vat_cst_paid if line.vat_cst_paid else ''),merge_format2)
            worksheet.write(row,col+9,(line.categ_id.name if line.categ_id.name else ''),merge_format2)
            row=row+1                
            s_no=s_no+1
        workbook.close()
        fo = open(url+"tn_purchase_tax.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xml_view/po/tax', type='http', auth='user')
    def print_xml_tn_po_reports(self, data, token):
        
        obj=self.export_xls_view_tn_po(data,token)
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])
        url1 = url + 'tn_purchase_tax.xlsx'
        wb = xlrd.open_workbook(url1)
        sh = wb.sheet_by_index(0)
        tags = [n.replace(" ", "").lower() for n in sh.row_values(0)]

        result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<myItems>\n"

        for row in range(1, sh.nrows):
            result += "  <item>\n"
            print tags[0]
            for i in range(len(tags)):
                if tags[i]:
                    tag = tags[i].encode("utf-8")
                    val = str(sh.row_values(row)[i]).encode("utf-8")
                    result += "    <%s>%s</%s>\n" % (tag, val, tag)
            result += "  </item>\n"

        result += "</myItems>"

        f = open(url + 'tn_purchase_tax.xml', "w+")
        obu=f.write(result)
        f.read()
        fi = open(url + 'tn_purchase_tax.xml', "r+")
        return request.make_response(            
            fi.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="tn_purchase_tax.xml"'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xls_view/sale/tax', type='http', auth='user')
    def export_xls_view_tn_sale(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[]) 
        tax_rec=request.env['tn.sale.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'tn_sale_tax.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#8281c7'})
        merge_format2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})

        worksheet.set_column('A:A', 10)
        worksheet.set_column('A:B', 15)
        worksheet.set_column('A:C', 15)
        worksheet.set_column('A:D', 15)
        worksheet.set_column('A:E', 15)
        worksheet.set_column('A:F', 15)
        worksheet.set_column('A:G', 15)
        worksheet.set_column('A:H', 15)
        worksheet.set_column('A:I', 15)
        worksheet.set_column('A:J', 15)
        worksheet.write('A1', 'serial_no',merge_format1)
        worksheet.write('B1', 'Name_of_buyer',merge_format1)
        worksheet.write('C1', 'Buyer_TIN',merge_format1)
        worksheet.write('D1', 'commodity_code',merge_format1)
        worksheet.write('E1', 'Invoice_No',merge_format1)
        worksheet.write('F1', 'Invoice_Date',merge_format1)
        worksheet.write('G1', 'Sale_Value',merge_format1)
        worksheet.write('H1', 'Tax_rate',merge_format1)
        worksheet.write('I1', 'VAT_CST_paid',merge_format1)
        worksheet.write('J1', 'Category',merge_format1)
                
        row=1
        col=0  
        s_no=1
        for line in tax_rec.tn_so_tax_ids:
            worksheet.write(row,col,s_no,merge_format2)
            worksheet.write(row,col+1,(line.partner_id.name if line.partner_id.name else ''),merge_format2)
            worksheet.write(row,col+2,(line.buyer_tin if line.buyer_tin else ''),merge_format2)
            worksheet.write(row,col+3,(line.commodity_code if line.commodity_code else ''),merge_format2)
            worksheet.write(row,col+4,(line.invoice_id.number if line.invoice_id.number else ''),merge_format2)
            worksheet.write(row,col+5,((datetime.strptime(line.invoice_date, '%Y-%m-%d').strftime('%m-%d-%Y'))  if line.invoice_date else ''),merge_format2)
            worksheet.write(row,col+6,(line.sale_value if line.sale_value else ''),merge_format2)
            worksheet.write(row,col+7,(line.tax_rate if line.tax_rate else ''),merge_format2)
            worksheet.write(row,col+8,(line.vat_cst_paid if line.vat_cst_paid else ''),merge_format2)
            worksheet.write(row,col+9,(line.categ_id.name if line.categ_id.name else ''),merge_format2)
            row=row+1                
            s_no=s_no+1
        workbook.close()
        fo = open(url+"tn_sale_tax.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
       
    @http.route('/web/export/xml_view/sale/tax', type='http', auth='user')
    def print_xml_tn_sale_reports(self, data, token):
        
        obj=self.export_xls_view_tn_sale(data,token)
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])
        url1 = url + 'tn_sale_tax.xlsx'
        wb = xlrd.open_workbook(url1)
        sh = wb.sheet_by_index(0)
        tags = [n.replace(" ", "").lower() for n in sh.row_values(0)]

        # This is going to come out as a string, which will write to a file in the end.
        result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<myItems>\n"

        # Now, we'll just create a string that looks like an XML node for each row
        # in the sheet. Of course, a lot of things will depend on the prescribed XML
        # format but since we have no idea what it is, we'll just do this:
        for row in range(1, sh.nrows):
            result += "  <item>\n"
            print tags[0]
            for i in range(len(tags)):
                if tags[i]:
                    tag = tags[i].encode("utf-8")
                    val = str(sh.row_values(row)[i]).encode("utf-8")
                    result += "    <%s>%s</%s>\n" % (tag, val, tag)
            result += "  </item>\n"

        # Close our pseudo-XML string.
        result += "</myItems>"

        # Close our pseudo-XML string.
        # Write the result string to a file using the standard I/O.
        f = open(url + 'tn_sale_tax.xml', "w+")
        obu=f.write(result)
        f.read()
        fi = open(url + 'tn_sale_tax.xml', "r+")
        return request.make_response(            
            fi.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="tn_sale_tax.xml"'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )



    
    @http.route('/web/export/xls_view/ka/po/tax', type='http', auth='user')
    def export_xls_view_ka_po(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[]) 
        tax_rec=request.env['ka.po.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'ka_purchase_tax.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#8281c7'})
        merge_format2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})

        worksheet.set_column('A:A', 10)
        worksheet.set_column('A:B', 15)
        worksheet.set_column('A:C', 15)
        worksheet.set_column('A:D', 15)
        worksheet.set_column('A:E', 15)
        worksheet.set_column('A:F', 15)
        worksheet.set_column('A:G', 15)
        worksheet.set_column('A:H', 15)
        worksheet.set_column('A:I', 15)
        worksheet.set_column('A:J', 15)
        worksheet.write('A1', 'serial_no',merge_format1)
        worksheet.write('B1', 'Name_of_Seller',merge_format)
        worksheet.write('C1', 'Seller_TIN',merge_format1)
        worksheet.write('D1', 'Invoice_No',merge_format1)
        worksheet.write('E1', 'Invoice_Date',merge_format1)
        worksheet.write('F1', 'Net_Value',merge_format1)
        worksheet.write('G1', 'Tax_value',merge_format1)
        worksheet.write('H1', 'Other Charges',merge_format1)
        worksheet.write('I1', 'Total Value',merge_format1)
                
        row=1
        col=0  
        s_no=1
        for line in tax_rec.ka_po_tax_ids:
            worksheet.write(row,col,s_no,merge_format2)
            worksheet.write(row,col+1,(line.partner_id.name if line.partner_id.name else ''),merge_format2)
            worksheet.write(row,col+2,(line.seller_tin if line.seller_tin else ''),merge_format2)
            worksheet.write(row,col+3,(line.invoice_id.number if line.invoice_id.number else ''),merge_format2)
            worksheet.write(row,col+4,((datetime.strptime(line.invoice_date, '%Y-%m-%d').strftime('%m-%d-%Y'))  if line.invoice_date else ''),merge_format2)
            worksheet.write(row,col+5,(line.amount_untaxed if line.amount_untaxed else ''),merge_format2)
            worksheet.write(row,col+6,(line.amount_taxed if line.amount_taxed else ''),merge_format2)
            worksheet.write(row,col+7,(line.other_charges if line.other_charges else 0.0),merge_format2)
            worksheet.write(row,col+8,(line.amount_total if line.amount_total else ''),merge_format2)
            row=row+1                
            s_no=s_no+1
        workbook.close()
        fo = open(url+"ka_purchase_tax.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xml_view/ka/po/tax', type='http', auth='user')
    def print_xml_ka_po_reports(self, data, token):
        
        obj=self.export_xls_view_ka_po(data,token)
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])
        url1 = url + 'ka_purchase_tax.xlsx'
        wb = xlrd.open_workbook(url1)
        sh = wb.sheet_by_index(0)
        tags = [n.replace(" ", "").lower() for n in sh.row_values(0)]

        result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<myItems>\n"

        for row in range(1, sh.nrows):
            result += "  <item>\n"
            print tags[0]
            for i in range(len(tags)):
                if tags[i]:
                    tag = tags[i].encode("utf-8")
                    val = str(sh.row_values(row)[i]).encode("utf-8")
                    result += "    <%s>%s</%s>\n" % (tag, val, tag)
            result += "  </item>\n"

        result += "</myItems>"

        f = open(url + 'ka_purchase_tax.xml', "w+")
        obu=f.write(result)
        f.read()
        fi = open(url + 'ka_purchase_tax.xml', "r+")
        return request.make_response(            
            fi.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="ka_purchase_tax.xml"'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
            
    @http.route('/web/export/xls_view/ka/sale/tax', type='http', auth='user')
    def export_xls_view_ka_sale(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[]) 
        tax_rec=request.env['ka.sale.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'ka_sale_tax.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#8281c7'})
        merge_format2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})

        worksheet.set_column('A:A', 10)
        worksheet.set_column('A:B', 15)
        worksheet.set_column('A:C', 15)
        worksheet.set_column('A:D', 15)
        worksheet.set_column('A:E', 15)
        worksheet.set_column('A:F', 15)
        worksheet.set_column('A:G', 15)
        worksheet.set_column('A:H', 15)
        worksheet.set_column('A:I', 15)
        worksheet.set_column('A:J', 15)
        worksheet.write('A1', 'serial_no',merge_format1)
        worksheet.write('B1', 'Name_of_Buyer',merge_format1)
        worksheet.write('C1', 'Buyer_TIN',merge_format1)
        worksheet.write('D1', 'Invoice_No',merge_format1)
        worksheet.write('E1', 'Invoice_Date',merge_format1)
        worksheet.write('F1', 'Net_Value',merge_format1)
        worksheet.write('G1', 'Tax_value',merge_format1)
        worksheet.write('H1', 'Other Charges',merge_format1)
        worksheet.write('I1', 'Total Value',merge_format1)
                
        row=1
        col=0  
        s_no=1
        for line in tax_rec.ka_so_tax_ids:
            worksheet.write(row,col,s_no,merge_format2)
            worksheet.write(row,col+1,(line.partner_id.name if line.partner_id.name else ''),merge_format2)
            worksheet.write(row,col+2,(line.buyer_tin if line.buyer_tin else ''),merge_format2)
            worksheet.write(row,col+3,(line.invoice_id.number if line.invoice_id.number else ''),merge_format2)
            worksheet.write(row,col+4,((datetime.strptime(line.invoice_date, '%Y-%m-%d').strftime('%m-%d-%Y'))  if line.invoice_date else ''),merge_format2)
            worksheet.write(row,col+5,(line.amount_untaxed if line.amount_untaxed else ''),merge_format2)
            worksheet.write(row,col+6,(line.amount_taxed if line.amount_taxed else ''),merge_format2)
            worksheet.write(row,col+7,(line.other_charges if line.other_charges else 0.0),merge_format2)
            worksheet.write(row,col+8,(line.amount_total if line.amount_total else ''),merge_format2)
            row=row+1                
            s_no=s_no+1
        workbook.close()
        fo = open(url+"ka_sale_tax.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )        
    
    @http.route('/web/export/xml_view/ka/sale/tax', type='http', auth='user')
    def print_xml_ka_sale_reports(self, data, token):
        
        obj=self.export_xls_view_ka_sale(data,token)
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])
        url1 = url + 'ka_sale_tax.xlsx'
        wb = xlrd.open_workbook(url1)
        sh = wb.sheet_by_index(0)
        tags = [n.replace(" ", "").lower() for n in sh.row_values(0)]
        result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<myItems>\n"
        for row in range(1, sh.nrows):
            result += "  <item>\n"
            print tags[0]
            for i in range(len(tags)):
                if tags[i]:
                    tag = tags[i].encode("utf-8")
                    val = str(sh.row_values(row)[i]).encode("utf-8")
                    result += "    <%s>%s</%s>\n" % (tag, val, tag)
            result += "  </item>\n"

        result += "</myItems>"

        f = open(url + 'ka_sale_tax.xml', "w+")
        obu=f.write(result)
        f.read()
        fi = open(url + 'ka_sale_tax.xml', "r+")
        return request.make_response(            
            fi.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="ka_sale_tax.xml"'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
    


    
    @http.route('/web/export/xls_view/ap/sale/tax', type='http', auth='user')
    def export_xls_view_ap_sale(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[]) 
        tax_rec=request.env['ap.sale.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'ap_sale_tax.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})
            

        worksheet.set_column('A:A', 10)
        worksheet.set_column('A:B', 15)
        worksheet.set_column('A:C', 15)
        worksheet.set_column('A:D', 15)
        worksheet.set_column('A:E', 25)
        worksheet.set_column('A:F', 25)
        worksheet.set_column('A:G', 15)
        worksheet.write('A1', 'TIN/GRN',merge_format1)
        worksheet.write('B1', '37200101197',merge_format2)
        worksheet.write('A2', 'Tax Month',merge_format1)
        worksheet.write('B2', (datetime.strptime(str(tax_rec.from_date), "%Y-%m-%d").strftime('%B')),merge_format2)
        worksheet.write('A3', 'Year',merge_format1)
        worksheet.write('B3', (datetime.strptime(str(tax_rec.from_date), "%Y-%m-%d").date().year),merge_format2)
        worksheet.merge_range('C1:G1', 'SALE DETAILS', merge_format1)
        worksheet.write('A4', 'Sl_no',merge_format1)
        worksheet.write('B4', 'Purchaser Tin',merge_format1)
        worksheet.write('C4', 'Invoice No',merge_format1)
        worksheet.write('D4', 'Invoice_Date',merge_format1)
        worksheet.write('E4', 'Name Of the Commodity',merge_format1)
        worksheet.write('F4', 'Total Value Including VAT in Rupees',merge_format1)
        worksheet.write('G4', 'Rate of Tax %',merge_format1)
                
        row=4
        col=0  
        s_no=1
        for line in tax_rec.ap_so_tax_ids:
            worksheet.write(row,col,s_no,merge_format2)
            worksheet.write(row,col+1,(line.buyer_tin if line.buyer_tin else ''),merge_format2)
            worksheet.write(row,col+2,(line.invoice_id.number if line.invoice_id.number else ''),merge_format2)
            worksheet.write(row,col+3,((datetime.strptime(line.invoice_date, '%Y-%m-%d').strftime('%m-%d-%Y'))  if line.invoice_date else ''),merge_format2)
            worksheet.write(row,col+4,(line.categ_id.name if line.categ_id.name else ''),merge_format2)
            worksheet.write(row,col+5,(line.amount_total if line.amount_total else ''),merge_format2)
            worksheet.write(row,col+6,(line.tax_rate if line.tax_rate else ''),merge_format2)
            
            row=row+1                
            s_no=s_no+1
        workbook.close()
        fo = open(url+"ap_sale_tax.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )

    @http.route('/web/export/xml_view/ap/sale/tax', type='http', auth='user')
    def print_xml_ap_sale_reports(self, data, token):
        
        obj=self.export_xls_view_ap_sale(data,token)
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])
        url1 = url + 'ap_sale_tax.xlsx'
        wb = xlrd.open_workbook(url1)
        sh = wb.sheet_by_index(0)
        tags = [n.replace(" ", "").lower() for n in sh.row_values(0)]
        result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<myItems>\n"
        for row in range(1, sh.nrows):
            result += "  <item>\n"
            print tags[0]
            for i in range(len(tags)):
                if tags[i]:
                    tag = tags[i].encode("utf-8")
                    val = str(sh.row_values(row)[i]).encode("utf-8")
                    result += "    <%s>%s</%s>\n" % (tag, val, tag)
            result += "  </item>\n"

        result += "</myItems>"

        f = open(url + 'ap_sale_tax.xml', "w+")
        obu=f.write(result)
        f.read()
        fi = open(url + 'ap_sale_tax.xml', "r+")
        return request.make_response(            
            fi.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="ap_sale_tax.xml"'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xls_view/ap/po/tax', type='http', auth='user')
    def export_xls_view_ap_po(self, data, token):
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[]) 
        tax_rec=request.env['ap.po.report'].browse(id)
        workbook = xlsxwriter.Workbook(url+'ap_po_tax.xlsx')
        worksheet = workbook.add_worksheet()
        merge_format1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})
        merge_format2 = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',})
            

        worksheet.set_column('A:A', 10)
        worksheet.set_column('A:B', 15)
        worksheet.set_column('A:C', 15)
        worksheet.set_column('A:D', 15)
        worksheet.set_column('A:E', 25)
        worksheet.set_column('A:F', 25)
        worksheet.set_column('A:G', 15)
        worksheet.write('A1', 'TIN/GRN',merge_format1)
        worksheet.write('B1', '37200101197',merge_format2)
        worksheet.write('A2', 'Tax Month',merge_format1)
        worksheet.write('B2', (datetime.strptime(str(tax_rec.from_date), "%Y-%m-%d").strftime('%B')),merge_format2)
        worksheet.write('A3', 'Year',merge_format1)
        worksheet.write('B3', (datetime.strptime(str(tax_rec.from_date), "%Y-%m-%d").date().year),merge_format2)
        worksheet.merge_range('C1:G1', 'PURCHASE DETAILS', merge_format1)
        worksheet.write('A4', 'Sl_no',merge_format1)
        worksheet.write('B4', 'Seller Tin',merge_format1)
        worksheet.write('C4', 'Invoice No',merge_format1)
        worksheet.write('D4', 'Invoice_Date',merge_format1)
        worksheet.write('E4', 'Name Of the Commodity',merge_format1)
        worksheet.write('F4', 'Total Value Including VAT in Rupees',merge_format1)
        worksheet.write('G4', 'Rate of Tax %',merge_format1)
                
        row=4
        col=0  
        s_no=1
        for line in tax_rec.ap_po_tax_ids:
            worksheet.write(row,col,s_no,merge_format2)
            worksheet.write(row,col+1,(line.seller_tin if line.seller_tin else ''),merge_format2)
            worksheet.write(row,col+2,(line.invoice_id.number if line.invoice_id.number else ''),merge_format2)
            worksheet.write(row,col+3,((datetime.strptime(line.invoice_date, '%Y-%m-%d').strftime('%m-%d-%Y'))  if line.invoice_date else ''),merge_format2)
            worksheet.write(row,col+4,(line.categ_id.name if line.categ_id.name else ''),merge_format2)
            worksheet.write(row,col+5,(line.amount_total if line.amount_total else ''),merge_format2)
            worksheet.write(row,col+6,(line.tax_rate if line.tax_rate else ''),merge_format2)
            
            row=row+1                
            s_no=s_no+1
        workbook.close()
        fo = open(url+"ap_po_tax.xlsx", "rb+")
        return  request.make_response(
            fo.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="%s"'
                 % self.filename(model)),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
        
    @http.route('/web/export/xml_view/ap/po/tax', type='http', auth='user')
    def print_xml_ap_po_reports(self, data, token):
        
        obj=self.export_xls_view_ap_po(data,token)
        data = json.loads(data)
        model = data.get('model', [])
        id=data.get('id',[])
        url1 = url + 'ap_po_tax.xlsx'
        wb = xlrd.open_workbook(url1)
        sh = wb.sheet_by_index(0)
        tags = [n.replace(" ", "").lower() for n in sh.row_values(0)]
        result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<myItems>\n"
        for row in range(1, sh.nrows):
            result += "  <item>\n"
            print tags[0]
            for i in range(len(tags)):
                if tags[i]:
                    tag = tags[i].encode("utf-8")
                    val = str(sh.row_values(row)[i]).encode("utf-8")
                    result += "    <%s>%s</%s>\n" % (tag, val, tag)
            result += "  </item>\n"

        result += "</myItems>"

        f = open(url + 'ap_po_tax.xml', "w+")
        obu=f.write(result)
        f.read()
        fi = open(url + 'ap_po_tax.xml', "r+")
        return request.make_response(            
            fi.read(),
            headers=[
                ('Content-Disposition', 'attachment; filename="ap_po_tax.xml"'),
                ('Content-Type', self.content_type)
            ],
            cookies={'fileToken': token}
        )
