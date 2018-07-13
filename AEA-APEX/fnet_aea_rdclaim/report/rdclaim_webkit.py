# -*- encoding: utf-8 -*-
##############################################################################
#
#    Author: Nicolas Bessi, Guewen Baconnier
#    Copyright Camptocamp SA 2011
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

from operator import itemgetter
from itertools import groupby
from datetime import datetime

from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _
from common_header import common_header
from .webkit_parser_header_fix import HeaderFooterTextWebKitParser


class RDClaimWebkitParser(report_sxw.rml_parse,common_header):

    def __init__(self, cursor, uid, name, context):
        super(RDClaimWebkitParser, self).__init__(
            cursor, uid, name, context=context)
        self.pool = pooler.get_pool(self.cr.dbname)
        self.cursor = self.cr

        company = self.pool.get('res.users').browse(
            self.cr, uid, uid, context=context).company_id
        header_report_name = ' - '.join(
            (_('RD CLAIM PRODUCT WISE REPORT '), company.name))
        footer_date_time = self.formatLang(str(datetime.today()),
                                           date_time=True)
        self.localcontext.update({
            'cr': cursor,
            'uid': uid,
            'report_name': _('RD Claim Xls'),  
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
        if (data['model'] == 'ir.ui.menu'):
            new_ids = 'company_id' in data['form'] and [data['form']['company_id'][0]] or []
            objects = self.pool.get('rdclaim.wizard').browse(self.cr, self.uid, new_ids)
        manager = self.get_manger_id(data)
        product=self._get_product_name(data)
        sale_person=self._get_sale_person(data)
        partner_lines=self._get_partner_lines(data)
        product_categ=self.get_prod_categ_id(data)
        saleperson_name=self.get_saleperson_name(data)
        self.localcontext.update({  
            'manager':manager,
            'product':product  ,
            'sale_person':sale_person,
            'partner_lines':partner_lines,
            'product_categ':product_categ,
            'saleperson_name':saleperson_name
        })
        return super(RDClaimWebkitParser, self).set_context(
            objects, data, new_ids, report_type=report_type)
HeaderFooterTextWebKitParser(
    'report.fnet_aea_rdclaim.report_rdclaim_webkit',
    'rdclaim.wizard',
    'addons/fnet_aea_rdclaim/report/templates/\
                                        rdclaim_report.mako',
    parser=RDClaimWebkitParser)
