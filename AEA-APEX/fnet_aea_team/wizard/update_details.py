from openerp.osv import osv
from openerp.tools.translate import _

class update_details(osv.osv_memory):
    """
    This wizard will submit the all the selected Sale Target
    """

    _name = "update.details"
    _description = "Submit the selected Sale Target"

    def invoice_confirm(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []
        proxy = self.pool['account.invoice']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            cr.execute("select section_id,user_id from res_partner where id = %d"%(record.partner_id))
            data=cr.dictfetchone()
            if data['user_id'] != None and data['section_id'] != None:
                cr.execute("update account_invoice set user_id=%d , section_id=%d where id = %d"%(data['user_id'],data['section_id'],record.ids[0]))
            elif  data['user_id'] != None and data['section_id'] == None:  
                 cr.execute("""SELECT 
                                      crm_case_section.id as id
                                    FROM 
                                      crm_case_section
                                      JOIN sale_member_rel ON sale_member_rel.section_id = crm_case_section.id
                                      JOIN res_users ON sale_member_rel.member_id = res_users.id 
                                    WHERE res_users.id = %d"""%(data['user_id']))
                 section_id=cr.dictfetchone()
                 if  section_id:
                    cr.execute("update account_invoice set user_id=%d , section_id=%d where id = %d"%(data['user_id'],section_id['id'],record.ids[0]))
                    cr.execute("update res_partner set section_id=%d where id = %d"%(section_id['id'],record.partner_id))
                    
                                    
            #~ if record.state not in ('draft',):
                #~ raise osv.except_osv(_('Warning!'), _("Selected Sale Target(s) cannot be confirmed as they are not in 'Draft' state."))
            #~ else:
                #~ record.write({'state':'done'})
            #~ record.signal_workflow('submit')
            
        return {'type': 'ir.actions.act_window_close'}
