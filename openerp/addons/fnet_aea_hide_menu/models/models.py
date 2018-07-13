from openerp import api,models,fields,_
from openerp.osv import fields, osv

from datetime import datetime
import time

class account_journal(osv.osv):
    _inherit = 'account.journal'      

    _columns = {
         'restricted_journal': fields.boolean('Allowed To Users', help='Check this if the journal is to be allowed for user level login.'),
        }    
    _order = 'restricted_journal desc'

    def name_get(self, cr, user, ids, context=None):
        """
        Returns a list of tupples containing id, name.
        result format: {[(id, name), (id, name), ...]}

        @param cr: A database cursor
        @param user: ID of the user currently logged in
        @param ids: list of ids for which name should be read
        @param context: context arguments, like lang, time zone

        @return: Returns a list of tupples containing id, name
        """
        if not ids:
            return []
        if isinstance(ids, (int, long)):
            ids = [ids]
        result = self.browse(cr, user, ids, context=context)
        user_obj=self.pool.get('res.users').browse(cr,ids,user)
        res = []
        ress = []
        for rs in result:
            if rs.currency:
                currency = rs.currency
            else:
                currency = rs.company_id.currency_id
            if rs.user_id.has_group('fnet_aea_hide_menu.restricted_journal') and rs.restricted_journal == True:  
                name = "%s (%s)" % (rs.name, currency.name)
                data=(rs.id, name)
                res.append(data)
            else:
                name = "%s (%s)" % (rs.name, currency.name)
                data=(rs.id, name)
                ress.append(data)                    
        for rs in result:
            if res != []:
                return res
            elif ress != []:        
                return ress
