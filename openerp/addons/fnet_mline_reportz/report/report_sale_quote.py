#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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

from openerp.osv import osv
from openerp.report import report_sxw


class sale_qoute_report1(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(sale_qoute_report1, self).__init__(cr, uid, name, context)
        self.localcontext.update({
        })



class wrapped_report_salequote(osv.AbstractModel):
    _name = 'report.fnet_mline_reportz.report_salequote'
    _inherit = 'report.abstract_report'
    _template = 'fnet_mline_reportz.report_salequote'
    _wrapped_report_class = sale_qoute_report1

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
