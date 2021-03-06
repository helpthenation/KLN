import openerp
import openerp.http as http
from openerp.http import request


class PopupController(openerp.http.Controller):

    @http.route('/popup_notifications/notify', type='json', auth="none")
    def notify(self):
        user_id = request.session.get('uid')
        return request.env['popup.notification'].sudo().search(
            [('partner_ids', '=', user_id), ('status', '!=', 'shown')]
        ).get_notifications()

    @http.route('/popup_notifications/notify_ack', type='json', auth="none")
    def notify_ack(self, notif_id, type='json'):
        notif_obj = request.env['popup.notification'].sudo().browse([notif_id])
        if notif_obj:
            notif_obj.status = 'shown'
