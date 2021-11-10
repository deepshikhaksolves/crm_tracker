# -*- coding: utf-8 -*-

from lxml import etree
from lxml.html import builder as html

from odoo import _, api, fields, models


class KsInvite(models.TransientModel):
    """ Wizard to invite partners (or channels) and make them followers. """
    _inherit = 'mail.wizard.invite'

    @api.model
    def default_get(self, fields):
        """This code is overridden to add lead code in """
        result = super(KsInvite, self).default_get(fields)
        # Override the function only if res_model is 'crm.lead' to add lead's code in invitation.
        if result.get('res_model') == 'crm.lead':
            user_name = self.env.user.name_get()[0][1]
            model = result.get('res_model')
            res_id = result.get('res_id')
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            parameters = '/web#id=%s&model=%s&view_type=form&menu_id=111' % (res_id, model)
            task_url = base_url + str(parameters)
            lead_code = self.env[model].browse(res_id).code or ''
            if model and res_id:
                document = self.env['ir.model']._get(model).display_name
                title = self.env[model].browse(res_id).display_name
                msg_fmt = _('%(user_name)s invited you to follow %(document)s %(lead_code)s document: %(title)s.')
            else:
                msg_fmt = _('%(user_name)s invited you to follow a new document %(lead_code)s.')

            text = msg_fmt % locals()
            message = html.DIV(
                html.P(_('Hello,')),
                html.P(text),
                html.P(html.A('View Lead/Opportunity', href=task_url, style="background-color:#875A7B; padding: 10px; "
                                                                            "text-decoration: none; color: #fff; "
                                                                            "border-radius: 5px;"),
                       style="margin-top: 24px; margin-bottom: 16px; margin-left: 200px;")
            )
            result['message'] = etree.tostring(message)
        return result
