# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com)
#                       Jordi Esteve <jesteve@zikzakmedia.com>
#    Copyright (C) 2011 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2011-2013 Agile Business Group sagl
#    (<http://www.agilebg.com>)
#    Ported to Odoo by Andrea Cometa <info@andreacometa.it>
#    Ported to v8 API by Eneko Lacunza <elacunza@binovo.es>
#    Copyright (c) 2015 Serv. Tecnol. Avanzados - Pedro M. Baeza
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
import time
from openerp import SUPERUSER_ID
from openerp.osv import fields, osv
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
class hr_contract(osv.osv):
    _inherit = 'hr.contract'

    def _check_trial_dates(self, cr, uid, ids, context=None):
        for contract in self.read(cr, uid, ids, ['trial_date_start', 'trial_date_end'], context=context):
             if contract['trial_date_start'] and contract['trial_date_end'] and contract['trial_date_start'] > contract['trial_date_end']:
                 return False
        return True

    _constraints = [
        (_check_trial_dates, 'Error! Contract start-date must be less than contract end-date.', ['trial_date_start', 'trial_date_end'])
    ]    

    def onchange_date_start(self,cr,uid,ids,date_start,context=None):
            if date_start:
                six_months = datetime.datetime.strptime(date_start,'%Y-%m-%d')
                return {'value': {'trial_date_start': six_months}}
                    
    def onchange_trial_date_start(self, cr, uid, ids, trial_date_start, context=None):
        if  trial_date_start:
            six_months = datetime.datetime.strptime(trial_date_start,'%Y-%m-%d') + relativedelta(months=+6)  
            trial_end=(six_months + relativedelta(days=-1)).strftime('%Y-%m-%d')   
            return {'value': {'trial_date_end': trial_end}}


