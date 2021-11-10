from odoo import http
from odoo.http import request


class KsHelpdeskSupport(http.Controller):

    @http.route(['/helpdesk_support_ticket'], type='http', auth="user", website=True)
    def ks_create_ticket(self, **post):
        return request.render("website_helpdesk_support_ticket.website_helpdesk_support_ticket")